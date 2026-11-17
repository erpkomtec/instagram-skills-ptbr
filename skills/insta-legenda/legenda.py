#!/usr/bin/env python3
"""
legenda.py - confere a legenda de um post do Instagram e mostra exatamente o
que aparece no feed antes do "... mais".

O feed mostra uns 125 caracteres e esconde o resto atrás de um toque. É ali
que quase toda legenda falha: o gancho está na terceira frase, a primeira
linha é um "Bom dia, pessoal!" ou abre com hashtag. Este script imprime a
parte visível numa caixa, para você ler como um estranho rolando a tela, e
faz as checagens que valem a pena.

O corte de 125 é aproximado: muda com o celular, o tamanho da fonte e onde
caem as quebras de linha. Por isso o objetivo é ter folga, não terminar
exatamente no 125. Mude com --corte para testar mais apertado.

Uso
  python legenda.py legenda.txt
  python legenda.py legenda.txt --buscas "sistema para oficina,orçamento rápido"
  python legenda.py legenda.txt --json
"""

import argparse
import json
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptbr  # noqa: E402

LIMITE = 2200          # limite do Instagram para legenda.
CORTE = 125            # mais ou menos onde o feed corta para "... mais".
LIMITE_HASHTAGS = 5    # máximo por post/Reel desde 18/12/2025 (antes eram 30).

HASHTAG_RE = re.compile(r"(?:^|\s)(#\w+)")
MENCAO_RE = re.compile(r"(?:^|\s)(@[\w.]+)")
LINK_RE = re.compile(
    r"https?://\S+|\bwww\.\S+|\b[a-z0-9-]+\.(?:com|com\.br|br|net|org|io|app|ai)(?:/\S*)?\b",
    re.IGNORECASE)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿←-⇿️]")

CHAMADAS = [
    (re.compile(r"(?i)\bcomente?\s+(?:a palavra\s+|aqui\s+)?[\"“]?[A-ZÀ-Ú0-9]{2,}\b"), "comentar uma palavra"),
    (re.compile(r"(?i)\b(?:me chama|chama|manda(?: um)?|me manda(?: um)?)\s+(?:no |uma? )?(?:direct|dm|inbox)\b"), "chamar no direct"),
    (re.compile(r"(?i)\b(?:chama|me chama|fala comigo|manda mensagem)\s+no\s+(?:whats|whatsapp|zap)\b"), "chamar no WhatsApp"),
    (re.compile(r"(?i)\bsalv[ae]\s+(?:esse|este|o post|pra|para)\b"), "salvar"),
    (re.compile(r"(?i)\b(?:compartilh[ae]|mand[ae] (?:pra|para|esse post pra))\b"), "compartilhar"),
    (re.compile(r"(?i)\b(?:sig[ae]|segue)\s+(?:a gente|o perfil|a página|a @|@|pra|para)"), "seguir"),
    (re.compile(r"(?i)\blink\s+(?:na|da)\s+bio\b"), "link na bio"),
    (re.compile(r"(?i)\b(?:arrast[ae]|deslize|desliza|passa pro lado)\b"), "arrastar"),
    (re.compile(r"(?i)\b(?:me conta|conta aqui|qual (?:você|voces|vocês)|o que (?:você|vocês) acha|comenta aqui)\b"), "responder uma pergunta"),
]

HASHTAGS_VAZIAS = {
    "#viral", "#fyp", "#explore", "#explorepage", "#foryou", "#foryoupage",
    "#trending", "#instagood", "#love", "#amor", "#follow", "#sigam",
    "#segueeusigo", "#sdv", "#curtir", "#like4like", "#reels", "#reelsinstagram",
    "#reelsbrasil", "#viralreels", "#instadaily", "#tbt", "#brasil", "#trend",
    "#viralizar", "#foco", "#sucesso", "#gratidão",
}


def contar_concretos(texto):
    return (sum(1 for t in ptbr.palavras(texto) if ptbr.eh_numero(t))
            + len(ptbr.nomes_proprios(texto)))


def janela_visivel(texto, corte):
    """O que o feed mostra. O Instagram corta no meio da palavra; aqui também."""
    t = texto.strip()
    return t if len(t) <= corte else t[:corte]


def caixa(janela, cortado, out=sys.stdout, largura=52):
    print("\n  O QUE O FEED MOSTRA", file=out)
    print("  +" + "-" * (largura + 2) + "+", file=out)
    linhas = []
    for bruto in janela.split("\n"):
        linhas.extend(textwrap.wrap(bruto, largura) or [""])
    for l in linhas[:8]:
        print(f"  | {l:<{largura}} |", file=out)
    rabo = "... mais" if cortado else "(cabe inteira)"
    print("  +" + "-" * (largura + 2 - len(rabo) - 2) + f" {rabo} " + "+", file=out)


def analisar(texto, corte=CORTE, buscas=None):
    t = texto.strip()
    chars = len(t)
    primeira = t.split("\n")[0].strip() if t else ""
    tags = HASHTAG_RE.findall(t)
    mencoes = MENCAO_RE.findall(t)
    links = LINK_RE.findall(t)
    emojis = EMOJI_RE.findall(t)
    janela = janela_visivel(t, corte)
    cortado = chars > corte
    chamadas = [nome for padrao, nome in CHAMADAS if padrao.search(t)]
    vazias = [x for x in tags if x.lower() in HASHTAGS_VAZIAS]
    buscas = [b.strip() for b in (buscas or []) if b.strip()]

    checagens = []

    def add(nome, status, detalhe):
        checagens.append({"checagem": nome, "status": status, "detalhe": detalhe})

    add("TAMANHO", "FALHA" if chars > LIMITE else "OK",
        f"{chars} / {LIMITE} caracteres" + (f", {chars - LIMITE} acima do limite"
                                            if chars > LIMITE else ""))

    if not primeira:
        add("1ª LINHA", "FALHA", "a legenda começa com linha em branco")
    elif primeira.startswith(("#", "@")):
        add("1ª LINHA", "FALHA", "abre com hashtag ou menção, na única posição que vale uma frase")
    elif re.match(r"(?i)^\s*(?:oi|olá|bom dia|boa tarde|boa noite|e a[ií]|fala)\b", primeira):
        add("1ª LINHA", "AVISO", "abre com cumprimento, gastando o espaço visível com nada")
    elif len(primeira) > corte:
        add("1ª LINHA", "AVISO",
            f"{len(primeira)} caracteres, cortada no {corte} no meio do raciocínio. "
            "Tudo bem se o corte deixa suspense, ruim se corta no meio de uma explicação")
    else:
        add("1ª LINHA", "OK", f"{len(primeira)} caracteres, aparece inteira")

    n = contar_concretos(janela)
    add("CONCRETO", "OK" if n else "AVISO",
        f"{n} número(s) ou nome(s) na parte visível"
        + ("" if n else " - nada que dê para conferir antes do toque"))

    if len(tags) > LIMITE_HASHTAGS:
        add("HASHTAGS", "FALHA", f"{len(tags)} hashtags, acima do limite de {LIMITE_HASHTAGS} do "
                                 "Instagram. As que passam da quinta não contam")
    elif vazias:
        add("HASHTAGS", "AVISO", f"{len(tags)} hashtag(s), {len(vazias)} genérica(s) "
                                 f"({', '.join(vazias[:3])}). Essas não descrevem nada")
    else:
        add("HASHTAGS", "OK", f"{len(tags)} hashtag(s)" + (f": {' '.join(tags)}" if tags else ""))

    if not tags:
        add("POSIÇÃO TAGS", "OK", "sem hashtags para posicionar")
    elif any(re.search(r"(?:^|\s)" + re.escape(x) + r"(?!\w)", janela) for x in tags):
        add("POSIÇÃO TAGS", "AVISO", "tem hashtag na parte visível, gastando espaço do feed com rótulo")
    else:
        add("POSIÇÃO TAGS", "OK", "hashtags abaixo do corte")

    add("LINKS", "AVISO" if links else "OK",
        f"{len(links)} link(s) na legenda, e link em legenda não é clicável. "
        "Coloque na bio ou mande no direct" if links else "sem link morto no texto")

    if len(chamadas) == 1:
        add("UMA CHAMADA", "OK", f"uma chamada para ação: {chamadas[0]}")
    elif not chamadas:
        add("UMA CHAMADA", "AVISO", "nenhuma chamada para ação. Decida para que serve este post")
    else:
        add("UMA CHAMADA", "AVISO", f"{len(chamadas)} chamadas ({', '.join(chamadas)}). "
                                    "Duas chamadas é o mesmo que nenhuma")

    dens = len(emojis) * 100 / max(chars, 1)
    add("EMOJI", "AVISO" if dens > 4 else "OK",
        f"{len(emojis)} emoji(s), {dens:.1f} a cada 100 caracteres"
        + (" - vira enfeite" if dens > 4 else ""))

    if buscas:
        baixo = ptbr.sem_acento(t.lower())
        achou = [b for b in buscas if ptbr.sem_acento(b.lower()) in baixo]
        falta = [b for b in buscas if b not in achou]
        visiveis = [b for b in achou if ptbr.sem_acento(b.lower()) in ptbr.sem_acento(janela.lower())]
        status = "OK" if not falta else ("AVISO" if achou else "FALHA")
        add("BUSCAS", status,
            f"{len(achou)}/{len(buscas)} presentes"
            + (f", {len(visiveis)} na parte visível" if achou else "")
            + (f". Faltando: {', '.join(falta)}" if falta else ""))

    falhas = sum(1 for c in checagens if c["status"] == "FALHA")
    avisos = sum(1 for c in checagens if c["status"] == "AVISO")
    veredito = "CORRIGIR" if falhas else ("REVISAR" if avisos else "PRONTA")

    return {
        "caracteres": chars, "limite": LIMITE, "corte": corte,
        "visivel": janela, "cortado": cortado,
        "hashtags": tags, "mencoes": mencoes, "links": links,
        "emojis": len(emojis), "chamadas": chamadas,
        "checagens": checagens, "veredito": veredito,
    }


def mostrar(a, out=sys.stdout):
    cab = (f"LEGENDA  ·  {a['caracteres']} / {a['limite']} caracteres  ·  "
           f"{len(a['hashtags'])} hashtags  ·  {len(a['chamadas'])} chamada(s)")
    print("\n" + cab, file=out)
    print("=" * max(len(cab), 62), file=out)
    caixa(a["visivel"], a["cortado"], out=out)
    print("", file=out)
    for c in a["checagens"]:
        print(f"  {c['status']:<6} {c['checagem']:<14} {c['detalhe']}", file=out)
    print("-" * max(len(cab), 62), file=out)
    print(f"  VEREDITO  {a['veredito']}\n", file=out)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Confere uma legenda do Instagram.")
    ap.add_argument("entrada", nargs="?", default="-", help="arquivo da legenda, ou -")
    ap.add_argument("--corte", type=int, default=CORTE,
                    help=f"caracteres visíveis antes do '... mais' (padrão {CORTE})")
    ap.add_argument("--buscas", default="", help="termos pelos quais quer ser encontrado, separados por vírgula")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.entrada == "-":
        bruto = sys.stdin.read()
    else:
        with open(args.entrada, encoding="utf-8") as f:
            bruto = f.read()
    a = analisar(bruto, corte=args.corte, buscas=args.buscas.split(","))
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        mostrar(a)
    sys.exit(0 if a["veredito"] == "PRONTA" else 1)


if __name__ == "__main__":
    main()
