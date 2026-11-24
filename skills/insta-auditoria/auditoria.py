#!/usr/bin/env python3
"""
auditoria.py - mede o que já foi postado contra a mediana do próprio perfil.

Entrada: arquivo separado por TAB, uma linha por post. Só `post` e
`visualizacoes` são obrigatórios; célula vazia é "não sei", nunca zero.

  post  formato  data  horas  visualizacoes  alcance  nao_seguidores
  retencao_3s  compartilhamentos  salvamentos  comentarios  seguidores_novos
  segundos  gancho

`horas` é a idade do post quando o número foi lido. Post com menos de 48 h
aparece, mas fica fora da mediana: ainda está rodando.

Uso
  python auditoria.py posts.tsv
  python auditoria.py posts.tsv --json
"""

import argparse
import json
import re
import statistics
import sys

NUMERICAS = ["horas", "visualizacoes", "alcance", "nao_seguidores", "retencao_3s",
             "compartilhamentos", "salvamentos", "comentarios", "seguidores_novos", "segundos"]
HORAS_MINIMAS = 48


def numero(txt):
    """Número do jeito brasileiro: 1.234 / 12,5% / 1,2 mil. Ilegível -> None."""
    t = (txt or "").strip().lower().replace("%", "").strip()
    mult = 1
    m = re.match(r"^(.*?)\s*(mil|mi|k)$", t)
    if m:
        t, mult = m.group(1), {"mil": 1000, "k": 1000, "mi": 1000000}[m.group(2)]
    if mult == 1 and re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", t):
        t = t.replace(".", "")
    t = t.replace(",", ".")
    if not re.fullmatch(r"\d+(\.\d+)?", t):
        return None
    return float(t) * mult


def ler(texto):
    linhas = [l for l in texto.lstrip("﻿").splitlines()
              if l.strip() and not l.lstrip().startswith("#")]
    if not linhas:
        return []
    cols = [c.strip().lower() for c in linhas[0].split("\t")]
    if "post" not in cols or "visualizacoes" not in cols:
        raise ValueError("a primeira linha precisa ter as colunas post e visualizacoes, separadas por TAB")
    posts = []
    for linha in linhas[1:]:
        cel = [c.strip() for c in linha.split("\t")]
        p = dict(zip(cols, cel + [""] * (len(cols) - len(cel))))
        for c in NUMERICAS:
            p[c] = numero(p.get(c, ""))
        if p["visualizacoes"] is not None and p.get("post"):
            posts.append(p)
    return posts


def mediana(itens, chave):
    v = [i[chave] for i in itens if i.get(chave) is not None]
    return statistics.median(v) if v else None


def confianca(n):
    if n < 10:
        return "BAIXA", "amostra pequena: dá para levantar hipótese, não para concluir"
    if n < 30:
        return "MÉDIA", "dá para ver tendência; confirme testando"
    return "BOA", "dá para ver padrão deste perfil"


def gargalo(posts):
    """Onde trava. Sempre hipótese: são limites de partida, não regras do Instagram."""
    if not posts:
        return "Sem post com 48 h ou mais: ainda não dá para dizer."
    ret = mediana(posts, "retencao_3s")
    nao = mediana(posts, "nao_seguidores")
    seg = mediana(posts, "seguidores_por_alcance")
    if ret is not None and ret < 50:
        return f"GANCHO (hipótese): mais da metade sai antes dos 3 s (ficam {ret:.0f}%). Vá para /insta-reel."
    if nao is not None and nao < 20:
        extra = ("falta a retenção em 3 s, que é o dado que confirma ou descarta o gancho"
                 if ret is None else "a retenção está razoável; olhe assunto, compartilhamento e collab")
        return f"ALCANCE (hipótese): só {nao:.0f}% vem de não seguidores; {extra}."
    if nao is not None and seg is not None and nao >= 40 and seg < 0.5:
        return "PERFIL (hipótese): chega gente nova e quase ninguém segue. Vá para /insta-perfil."
    if ret is None and nao is None:
        return "NÃO DÁ PARA DIZER: faltam retenção em 3 s e % de não seguidores."
    return "Nenhum gargalo claro com estes dados."


def analisar(posts):
    maduros = [p for p in posts if p["horas"] is None or p["horas"] >= HORAS_MINIMAS]
    med = mediana(maduros, "visualizacoes")
    for p in posts:
        p["recente"] = p["horas"] is not None and p["horas"] < HORAS_MINIMAS
        p["multiplo"] = round(p["visualizacoes"] / med, 2) if med else None
        alc = p["alcance"]
        for nome, campo in (("envios_por_alcance", "compartilhamentos"),
                            ("salvos_por_alcance", "salvamentos"),
                            ("seguidores_por_alcance", "seguidores_novos")):
            p[nome] = round(p[campo] / alc * 100, 2) if alc and p[campo] is not None else None
    ordem = sorted(maduros, key=lambda p: -(p["multiplo"] or 0))
    corte = len(ordem) // 3
    topo, fundo = (ordem[:corte], ordem[-corte:]) if corte else ([], [])
    comparar = {}
    for c in ("retencao_3s", "nao_seguidores", "segundos", "envios_por_alcance", "seguidores_por_alcance"):
        a, b = mediana(topo, c), mediana(fundo, c)
        if a is not None and b is not None:
            comparar[c] = (a, b)
    nivel, porque = confianca(len(maduros))
    faltam = [c for c in ("retencao_3s", "nao_seguidores", "alcance", "compartilhamentos", "seguidores_novos")
              if not any(p[c] is not None for p in maduros)]
    return {"n": len(posts), "maduros": len(maduros), "mediana": med, "confianca": nivel,
            "confianca_porque": porque, "sem_idade": sum(p["horas"] is None for p in maduros),
            "posts": ordem, "recentes": [p for p in posts if p["recente"]],
            "topo_x_fundo": comparar, "gargalo": gargalo(maduros), "faltam": faltam}


def fmt(v, suf=""):
    if v is None:
        return "-"
    return (f"{v:.0f}" if float(v).is_integer() else f"{v:.1f}".replace(".", ",")) + suf


def mostrar(a):
    print(f"\nAUDITORIA  ·  {a['n']} posts  ·  mediana {fmt(a['mediana'])} visualizações"
          f"  ·  confiança {a['confianca']}")
    print("=" * 78)
    print(f"  {a['confianca_porque']}")
    if a["sem_idade"]:
        print(f"  {a['sem_idade']} post(s) sem a coluna horas: idades misturadas enfraquecem a comparação")
    print(f"\n  {'múltiplo':>8} {'vis':>6} {'não seg':>8} {'ret 3s':>7} {'envios':>7}  post")
    for p in a["posts"] + a["recentes"]:
        m = f"{p['multiplo']:.1f}x".replace(".", ",") if p["multiplo"] is not None else "-"
        print(f"  {m:>8} {fmt(p['visualizacoes']):>6} {fmt(p['nao_seguidores'], '%'):>8} "
              f"{fmt(p['retencao_3s'], '%'):>7} {fmt(p['envios_por_alcance'], '%'):>7}  {p['post'][:38]}"
              + ("  (menos de 48 h)" if p["recente"] else ""))
    if a["topo_x_fundo"]:
        print("\n  TERÇO DE CIMA x TERÇO DE BAIXO (medianas)")
        for c, (x, y) in a["topo_x_fundo"].items():
            print(f"    {c:<24} {fmt(x)}  x  {fmt(y)}")
    print(f"\n  ONDE TRAVA   {a['gargalo']}")
    if a["faltam"]:
        print(f"  FALTA        {', '.join(a['faltam'])}")
    print()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Auditoria dos posts contra a mediana do próprio perfil.")
    ap.add_argument("entrada")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        with open(args.entrada, encoding="utf-8") as f:
            posts = ler(f.read())
    except (OSError, ValueError) as e:
        print(e, file=sys.stderr)
        sys.exit(2)
    if not posts:
        print("nenhum post com visualizações no arquivo", file=sys.stderr)
        sys.exit(2)
    a = analisar(posts)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        mostrar(a)


if __name__ == "__main__":
    main()
