#!/usr/bin/env python3
"""
pesquisa.py - ordena Reels coletados à mão pelo quanto cada um superou a
própria conta, e diz qual fórmula de gancho usou.

Visualização bruta não é evidência: 400 mil numa conta de 2 milhões é um dia
fraco; numa conta de 4 mil é um achado.

Entrada separada por TAB, com cabeçalho:
  conta  seguidores  mediana  visualizacoes  gancho
Sem `mediana` usa os seguidores, e a saída avisa: é uma base bem pior.
(Usa ganchos.json e gancho.py da pasta vizinha insta-reel, se existirem.)

Uso
  python pesquisa.py coletados.tsv --saida ~/.claude/instagram/referencias.md
"""

import argparse
import json
import os
import re
import statistics
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
REEL = os.path.join(AQUI, "..", "insta-reel")
sys.path.insert(0, AQUI)
import ptbr  # noqa: E402

try:
    sys.path.insert(1, REEL)
    from gancho import avaliar
except ImportError:                    # insta-pesquisa copiada sozinha
    avaliar = None


def formulas():
    try:
        with open(os.path.join(REEL, "ganchos.json"), encoding="utf-8") as f:
            d = json.load(f)
    except OSError:
        return []
    por_id = {g["id"]: g for g in d["ganchos"]}
    return [(i, por_id[i]["nome"], re.compile(por_id[i]["reconhece"], re.I))
            for i in d["ordem_classificacao"]]


def inteiro(t):
    t = (t or "").strip().lower()
    m = re.match(r"^(\d+(?:[.,]\d+)?)\s*(mil|mi|k)$", t)
    if m:
        fator = {"mil": 1000, "k": 1000, "mi": 1000000}[m.group(2)]
        return round(float(m.group(1).replace(",", ".")) * fator)
    d = re.sub(r"\D", "", t)
    return int(d) if d else None


def ler(texto):
    linhas = [l for l in texto.lstrip("﻿").splitlines()
              if l.strip() and not l.lstrip().startswith("#")]
    if not linhas:
        return []
    cols = [c.strip().lower() for c in linhas[0].split("\t")]
    if "visualizacoes" not in cols or "gancho" not in cols:
        raise ValueError("a primeira linha precisa ter as colunas visualizacoes e gancho, separadas por TAB")
    out = []
    for linha in linhas[1:]:
        cel = [c.strip() for c in linha.split("\t")]
        r = dict(zip(cols, cel + [""] * (len(cols) - len(cel))))
        for c in ("seguidores", "mediana", "visualizacoes"):
            r[c] = inteiro(r.get(c))
        if r["visualizacoes"] and r["gancho"]:
            out.append(r)
    return out


def mediana_palavras(reels):
    return statistics.median(r["palavras"] for r in reels) if reels else None


def analisar(reels, forms=None):
    forms = formulas() if forms is None else forms
    for r in reels:
        r["base"] = r["mediana"] or r["seguidores"]
        r["base_fraca"] = not r["mediana"]
        r["multiplo"] = round(r["visualizacoes"] / r["base"], 2) if r["base"] else None
        r["formula_id"], r["formula"] = next(
            ((i, n) for i, n, p in forms if p.search(r["gancho"])), (None, "não classificado"))
        r["palavras"] = len(ptbr.palavras(r["gancho"]))
        r["nota"] = round(avaliar(r["gancho"])[1]) if avaliar else None
    # Múltiplo sobre mediana e sobre seguidores não se comparam: base fraca vai para o fim.
    ordem = sorted(reels, key=lambda r: (r["base_fraca"], -(r["multiplo"] or 0)))
    bons = [r for r in ordem if not r["base_fraca"]]
    corte = len(bons) // 3
    topo, fundo = (bons[:corte], bons[-corte:]) if corte else ([], [])
    cont = {}
    for r in topo:
        cont[r["formula"]] = cont.get(r["formula"], 0) + 1
    return {"n": len(ordem), "contas": len({r.get("conta", "") for r in ordem}), "reels": ordem,
            "sem_mediana": sum(r["base_fraca"] for r in ordem),
            "formulas_topo": sorted(cont.items(), key=lambda x: -x[1]),
            "palavras_topo": mediana_palavras(topo), "palavras_fundo": mediana_palavras(fundo),
            "nao_classificados": sum(r["formula_id"] is None for r in ordem)}


def texto(a):
    l = ["# Referências", "",
         f"{a['n']} Reels de {a['contas']} conta(s), pelo múltiplo sobre a mediana de cada conta."]
    if a["sem_mediana"]:
        l.append(f"{a['sem_mediana']} sem mediana (usa seguidores, base fraca): no fim e fora da comparação.")
    if a["n"] < 40 or a["contas"] < 6:
        l.append("Amostra pequena (menos de 40 Reels ou 6 contas): trate como pista, não como prova.")
    l.append("")
    for r in a["reels"]:
        m = f"{r['multiplo']:.1f}x".replace(".", ",") if r["multiplo"] else "?"
        cod = f"#{r['formula_id']} " if r["formula_id"] else ""
        nota = f" · nota {r['nota']}" if r["nota"] is not None else ""
        l.append(f"- **{m}** {r.get('conta', '')} · {cod}{r['formula']}{nota} · {r['visualizacoes']} vis"
                 + (" · base fraca" if r["base_fraca"] else ""))
        l.append(f"  \"{r['gancho']}\"")
    if a["formulas_topo"]:
        l += ["", "Fórmulas no terço de cima: " + ", ".join(f"{n} x{c}" for n, c in a["formulas_topo"]),
              f"Palavras no gancho: {a['palavras_topo']:g} em cima x {a['palavras_fundo']:g} embaixo"]
    l += ["", f"Não classificados: {a['nao_classificados']}. Leia esses à mão."]
    return "\n".join(l) + "\n"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Ordena Reels coletados pelo múltiplo sobre a própria conta.")
    ap.add_argument("entrada")
    ap.add_argument("--saida")
    args = ap.parse_args()
    try:
        with open(args.entrada, encoding="utf-8") as f:
            reels = ler(f.read())
    except (OSError, ValueError) as e:
        print(e, file=sys.stderr)
        sys.exit(2)
    if not reels:
        print("nenhum Reel com visualizações e gancho", file=sys.stderr)
        sys.exit(2)
    t = texto(analisar(reels))
    print(t)
    if args.saida:
        destino = os.path.abspath(os.path.expanduser(args.saida))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(t)


if __name__ == "__main__":
    main()
