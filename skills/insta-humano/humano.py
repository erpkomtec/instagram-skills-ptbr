#!/usr/bin/env python3
"""
humano.py - tira o "jeito de texto de IA" de um rascunho em português e mostra
o que ainda precisa ser reescrito por alguém.

Corrige sozinho: caracteres invisíveis, travessão, aspas curvas, reticências
de um caractere. Expressão batida e forma repetida são apenas APONTADAS:
trocar por regex quebra concordância em português.

Não é detector de IA e não imita nenhum. Conta só o que está em vicios.json.

Uso
  python humano.py rascunho.txt
  python humano.py rascunho.txt -o limpo.txt
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import ptbr  # noqa: E402

URL_RE = re.compile(r"https?://\S+|www\.\S+|\S+@\S+\.\S+")
EMOJI = "\U0001F000-\U0001FAFF←-⇿☀-➿⬀-⯿"


def vicios():
    with open(os.path.join(AQUI, "vicios.json"), encoding="utf-8") as f:
        return json.load(f)


def limpar(texto):
    """Devolve (texto limpo, {o que mudou: quantas vezes})."""
    urls, mudou = [], {}

    def guarda(m):
        urls.append(m.group(0))
        return f"\x00{len(urls) - 1}\x00"

    def troca(nome, padrao, por, t):
        t, n = re.subn(padrao, por, t)
        if n:
            mudou[nome] = mudou.get(nome, 0) + n
        return t

    t = URL_RE.sub(guarda, texto)
    # O ZWJ dentro de emoji composto é legítimo: guarda antes de limpar.
    t = re.sub(f"(?<=[{EMOJI}️])‍(?=[{EMOJI}])", "\x01", t)
    n = sum(unicodedata.category(c) == "Cf" for c in t)
    if n:
        mudou["caractere invisível"] = n
        t = "".join(c for c in t if unicodedata.category(c) != "Cf")
    t = t.replace("\x01", "‍")
    t = troca("espaço especial", "[     ]", " ", t)
    t = troca("travessão", r"(?m)^[ \t]*[—–][ \t]*", "- ", t)
    t = troca("travessão", r"(?<=\d)[ \t]*–[ \t]*(?=\d)", "-", t)
    t = troca("travessão", r"[ \t]*—[ \t]*|[ \t]+–[ \t]+", ", ", t)
    t = troca("aspas curvas", "[“”]", '"', t)
    t = troca("aspas curvas", "[‘’]", "'", t)
    t = troca("reticências", "…", "...", t)
    if "travessão" in mudou:
        t = re.sub(r",[ \t]*([,.;:!?])", r"\1", t)
        t = re.sub(r"(?m),[ \t]*$", "", t)
    for i, u in enumerate(urls):
        t = t.replace(f"\x00{i}\x00", u)
    return t, mudou


def avaliar(texto):
    v = vicios()
    sem_url = URL_RE.sub(" ", texto)
    toks = ptbr.palavras(sem_url)
    n = len(toks)
    apontar = []
    for e in v["expressoes"]:
        for m in re.finditer(r"(?<!\w)(?:" + e["busca"] + r")(?!\w)", sem_url, re.I):
            apontar.append((m.group(0), e["dica"]))
    for e in v["formas"]:
        for m in re.finditer(e["busca"], sem_url, re.I | re.M):
            apontar.append((re.sub(r"\s+", " ", m.group(0)).strip()[:60], e["dica"]))
    frases = [len(ptbr.palavras(f)) for f in re.split(r"[.!?\n]+", sem_url)]
    frases = [f for f in frases if f > 2]
    if len(frases) >= 5 and statistics.pstdev(frases) / statistics.mean(frases) < 0.20:
        apontar.append(("ritmo", "frases quase todas do mesmo tamanho; quebre uma bem curta"))
    concretos = sum(ptbr.eh_numero(p) for p in toks) + len(set(ptbr.nomes_proprios(sem_url)))
    if n >= 25 and concretos == 0:
        apontar.append(("sem nada concreto", "nenhum número ou nome; ponha um dado real ou {{seu número}}"))
    por100 = len(apontar) * 100 / n if n else 0
    veredito = "LIMPO" if not apontar else "REVISAR" if por100 <= 4 else "REESCREVER"
    return {"palavras": n, "apontar": apontar, "veredito": veredito}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Limpa e aponta o jeito de texto de IA em português.")
    ap.add_argument("entrada")
    ap.add_argument("-o", "--saida")
    args = ap.parse_args()
    with open(args.entrada, encoding="utf-8") as f:
        limpo, mudou = limpar(f.read())
    a = avaliar(limpo)
    print(limpo)
    print("-" * 62)
    for k, q in mudou.items():
        print(f"  corrigido   {k} ({q})")
    for trecho, dica in a["apontar"]:
        print(f"  REESCREVA   \"{trecho}\": {dica}")
    print(f"  {a['veredito']}  ·  {a['palavras']} palavras, {len(a['apontar'])} ponto(s) para reescrever")
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(limpo)
    sys.exit(0 if a["veredito"] == "LIMPO" else 1)


if __name__ == "__main__":
    main()
