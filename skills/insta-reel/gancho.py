#!/usr/bin/env python3
"""
gancho.py - dá nota de 0 a 100 à frase de abertura (o gancho) de um Reel.

Cinco propriedades, todas checáveis no texto:
  TAMANHO       cabe em ~2 segundos falado e em duas linhas na tela
  CONCRETO      tem número, valor em R$, nome, quantidade falada
  TENSÃO        alguma coisa está em jogo: erro, perda, "nunca", "sem", custo
  NA FRENTE     a palavra que interessa vem nas primeiras 4 palavras
  PRA QUEM      fala com uma pessoa ("você"), ou manda fazer algo

A nota final pesa a média e a pior propriedade: uma só fraca já basta para o
polegar continuar rolando. Há também os "eliminatórios" (cumprimento, "nesse
vídeo eu vou mostrar", hashtag, emoji), que descontam 15 pontos cada.

LEIA ISTO: no teste do autor original (inglês, 74 ganchos de Shorts) a nota
separou bem gancho ruim de gancho bom em geral, mas NÃO conseguiu prever qual
vídeo de um mesmo criador ia bombar. Use para DESCARTAR gancho fraco, não para
escolher o vencedor. Esta versão em português ainda não foi medida.

Uso
  python gancho.py ganchos.txt            # um gancho por linha, sai o ranking
  python gancho.py --gancho "uma frase"   # nota detalhada de um só
  python gancho.py ganchos.txt --json
"""

import argparse
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptbr  # noqa: E402

HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

TENSAO = {
    "pare", "para de", "parar", "nunca", "jamais", "errado", "errada", "erro", "erros",
    "errei", "perdi", "perde", "perder", "perdendo", "perdeu", "prejuízo", "custou",
    "custa", "custo", "quebrou", "quebrei", "falhou", "falência", "faliu", "ninguém",
    "não", "nem", "sem", "multa", "multado", "multada", "demiti", "demitido", "apaguei",
    "cortei", "cortou", "grátis", "pagou", "paguei", "pagando", "cobrei", "cobrando",
    "economizei", "economiza", "proibido", "ilegal", "pior", "odeio", "desperdício",
    "joguei", "golpe", "mentira", "verdade", "segredo", "escondido", "roubo", "antes",
    "em vez", "mas", "exceto", "problema", "risco", "perigo", "cuidado", "atenção",
    "arrependo", "arrependi", "deveria", "devia", "ainda", "já", "só", "apenas",
    "versus", "contra", "primeiro", "parei", "larguei", "trocar", "troquei",
    "substituiu", "acabou", "acabei", "rombo", "dívida", "atrasado", "atraso",
    "esqueci", "esquecer", "esquece", "esqueceu", "esquecido", "deve", "devendo", "devia", "deviam", "fiado", "calote", "atrasou", "atrasada", "atrasadas", "vencida", "vencidas", "parada", "parado", "sumiu", "sobrou", "faltou", "falta", "levava", "demorava", "gastava", "virou",
}
# Expressões de mais de uma palavra procuradas no texto inteiro.
TENSAO_EXPR = ["para de", "em vez de", "de graça", "na verdade", "ninguém te"]

ABERTURAS_FRACAS = [
    "então", "bom", "ok", "olá", "oi", "e aí", "eai", "galera", "pessoal", "gente",
    "fala", "bem-vindo", "bem-vindos", "hoje", "basicamente", "sinceramente",
    "olha", "escuta", "tipo", "vamos", "vou", "eu queria", "eu quero", "eu vim",
    "você sabia", "vocês", "nesse", "neste", "esse é", "esse aqui", "isso é",
    "existe", "tem um", "tem uma", "uma das", "um dos", "a coisa", "muita gente",
    "quando se", "se você já", "sabe aquele", "sabe aquela", "deixa eu",
]

IMPERATIVOS = {
    "pare", "copie", "apague", "tente", "veja", "assista", "leia", "salve", "use",
    "monte", "faça", "escreva", "envie", "mande", "comece", "largue", "confira",
    "anote", "nunca", "sempre", "não", "esqueça", "troque", "corte", "cobre",
    "guarde", "evite", "esquece", "para",
}

ELIMINATORIOS = [
    (re.compile(r"(?i)^\s*(?:para de rolar|não (?:passa|pula|rola)|espera(?:\s|,|!|$))"),
     "Abre com \"para de rolar\" / \"espera\". Pedir atenção prova que você ainda não ganhou."),
    (re.compile(r"(?i)\b(?:n[ea]ss?e vídeo|n[ea]st[ea] vídeo|n[ea]ss?e reels?|hoje eu vou (?:te |lhe )?(?:mostrar|ensinar)|vou (?:te |lhe )?mostrar)\b"),
     "Preâmbulo de vídeo. Apague e comece pelo resultado."),
    (re.compile(r"(?i)^\s*(?:oi|olá|e a[ií]|fala(?: galera| pessoal| gente)?|bom dia|boa tarde|boa noite|salve)\b"),
     "Cumprimento. Ninguém abriu o feed para ser cumprimentado."),
    (HASHTAG_RE, "Hashtag no gancho. Hashtag vai no fim da legenda, se for."),
    (EMOJI_RE, "Emoji no gancho. Texto grande de gancho tem espaço para palavra ou para emoji, não os dois."),
]


def limitar(n):
    return max(0.0, min(100.0, n))


def ver_tamanho(texto):
    """Tem que chegar antes do polegar mexer: uns dois segundos."""
    n = len(ptbr.palavras(texto))
    sil = ptbr.silabas(texto)
    seg = sil / 5.0
    chars = len(texto.strip())
    # O limite que manda é o tempo falado (até 3 s); a contagem de palavras
    # pega o gancho curto demais para dizer alguma coisa.
    if 5 <= n <= 11 and seg <= 3.0:
        nota = 100.0
    elif n < 5:
        nota = limitar(100 - (5 - n) * 20)
    else:
        nota = limitar(100 - max(n - 11, 0) * 11 - max(seg - 3.0, 0) * 25)
    if chars > 60:                     # duas linhas de texto grande na tela
        nota -= 12
    return limitar(nota), f"{n} palavras, {sil} sílabas, ~{seg:.1f}s falado, {chars} caracteres (ideal: 5-11 palavras, até 3s)"


def ver_concreto(texto):
    """Uma coisa concreta vale mais do que três abstratas."""
    toks = ptbr.palavras(texto)
    nums = [t for t in toks if ptbr.eh_numero(t)]
    nomes = ptbr.nomes_proprios(texto)
    falados = [t for t in (x.lower() for x in toks)
               if t in ptbr.NUMEROS_FALADOS or t in ptbr.PALAVRAS_DINHEIRO]
    n = len(nums) + len(nomes) + len(falados)
    nota = 15.0 if n == 0 else limitar(45 + n * 30)
    achados = ", ".join(nums[:2] + nomes[:2] + falados[:2])
    return nota, (f"{n} marcador(es) concreto(s)" + (f": {achados}" if achados
                  else " - sem número, sem nome, nada que dê para conferir"))


def ver_tensao(texto):
    """Algo que a pessoa pode perder, um custo, uma negação."""
    baixo = texto.lower()
    toks = ptbr.minusculas(texto)
    marcas = sorted({t for t in toks if t in TENSAO}
                    | {e for e in TENSAO_EXPR if e in baixo})
    if ptbr.DINHEIRO_RE.search(texto):
        marcas.append("um valor em R$")
    n = len(marcas)
    nota = {0: 20.0, 1: 70.0}.get(n, 100.0)
    return nota, (f"{n} marcador(es) de tensão" + (f": {', '.join(marcas[:4])}" if marcas
                  else " - nada está em jogo nessa frase"))


def ver_na_frente(texto):
    """A palavra que interessa não pode estar na posição nove."""
    toks = ptbr.palavras(texto)
    if not toks:
        return 0.0, "vazio"
    baixo = [t.lower() for t in toks]
    inicio = " ".join(baixo[:3])
    penal, fraca = 0, None
    for f in ABERTURAS_FRACAS:
        if inicio == f or inicio.startswith(f + " ") or baixo[0] == f:
            penal, fraca = 30, f
            break
    nomes = set(ptbr.nomes_proprios(texto))
    carga = None
    for i, t in enumerate(baixo):
        if (t in TENSAO or t in ptbr.NUMEROS_FALADOS or t in ptbr.PALAVRAS_DINHEIRO
                or ptbr.eh_numero(t) or toks[i] in nomes):
            carga = i
            break
    if carga is None:
        base, onde = 30.0, "nenhuma palavra de peso na frase"
    elif carga <= 3:
        base, onde = 100.0, f"palavra de peso na posição {carga + 1}"
    elif carga <= 6:
        base, onde = 70.0, f"palavra de peso na posição {carga + 1}, dá para puxar para frente"
    else:
        base, onde = 40.0, f"palavra de peso na posição {carga + 1}, tarde demais"
    return limitar(base - penal), onde + (f"; abertura fraca \"{fraca}\"" if fraca else "")


def ver_pra_quem(texto):
    """Mirado numa pessoa, ou solto no ar."""
    baixo = texto.lower()
    toks = ptbr.minusculas(texto)
    if re.search(r"\b(você|vocês|voce|seu|sua|seus|suas|te|tu|teu|tua|contigo)\b", baixo):
        return 100.0, "fala com quem está assistindo"
    if toks and toks[0] in IMPERATIVOS:
        return 90.0, f"abre mandando fazer (\"{toks[0]}\")"
    if re.search(r"\b(eu|meu|minha|meus|minhas|me|nós|nosso|nossa|a gente)\b", baixo):
        return 70.0, "primeira pessoa, sem falar com ninguém"
    return 35.0, "terceira pessoa, ninguém na sala"


CHECAGENS = ["TAMANHO", "CONCRETO", "TENSÃO", "NA FRENTE", "PRA QUEM"]


def avaliar(texto):
    res = {
        "TAMANHO": ver_tamanho(texto),
        "CONCRETO": ver_concreto(texto),
        "TENSÃO": ver_tensao(texto),
        "NA FRENTE": ver_na_frente(texto),
        "PRA QUEM": ver_pra_quem(texto),
    }
    alertas = [msg for padrao, msg in ELIMINATORIOS if padrao.search(texto)]
    notas = [res[c][0] for c in CHECAGENS]
    geral = limitar(statistics.mean(notas) * 0.6 + min(notas) * 0.4 - len(alertas) * 15)
    veredito = "FORTE" if geral >= 70 and min(notas) >= 55 and not alertas else (
        "OK" if geral >= 50 else "FRACO")
    return res, geral, veredito, alertas


def barra(nota, largura=24):
    cheio = round(nota / 100 * largura)
    return "#" * cheio + "." * (largura - cheio)


def mostrar_um(texto, res, geral, veredito, alertas, out=sys.stdout):
    print("\nNOTA DO GANCHO", file=out)
    print("=" * 62, file=out)
    print(f"  \"{texto.strip()}\"\n", file=out)
    for nome in CHECAGENS:
        nota, det = res[nome]
        print(f"  {nome:<11} {barra(nota)} {nota:5.1f}", file=out)
        print(f"  {'':<11} {det}", file=out)
    print("-" * 62, file=out)
    print(f"  {'NOTA':<11} {barra(geral)} {geral:5.1f}   {veredito}", file=out)
    for a in alertas:
        print(f"\n  ELIMINATÓRIO  {a}", file=out)
    if veredito != "FORTE":
        pior = min(CHECAGENS, key=lambda c: res[c][0])
        print(f"\n  Ponto mais fraco: {pior}. Corrija esse e rode de novo.", file=out)
    print("", file=out)


def mostrar_ranking(linhas, out=sys.stdout):
    print("\nRANKING DOS GANCHOS\n" + "=" * 78, file=out)
    for i, r in enumerate(linhas, 1):
        seta = "->" if i == 1 else "  "
        g = r["gancho"] if len(r["gancho"]) <= 62 else r["gancho"][:59] + "..."
        print(f"{seta} {r['nota']:5.1f} {r['veredito']:<6} {g}", file=out)
        print(f"        mais fraco: {r['mais_fraco']} ({r['checagens'][r['mais_fraco']]['nota']:.0f})", file=out)
        for a in r["alertas"]:
            print(f"        eliminatório: {a}", file=out)
    print("\nGrave o primeiro. Se o primeiro está abaixo de 50, nenhum destes é o gancho.\n",
          file=out)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Nota do gancho de um Reel em 5 propriedades.")
    ap.add_argument("entrada", nargs="?", default="-", help="arquivo com um gancho por linha, ou -")
    ap.add_argument("--gancho", help="avalia um gancho só, passado na linha de comando")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.gancho:
        linhas = [args.gancho]
    else:
        if args.entrada == "-":
            bruto = sys.stdin.read()
        else:
            with open(args.entrada, encoding="utf-8") as f:
                bruto = f.read()
        linhas = [l.strip() for l in bruto.splitlines() if l.strip()]
    if not linhas:
        print("nada para avaliar", file=sys.stderr)
        sys.exit(2)

    saida = []
    for l in linhas:
        res, geral, veredito, alertas = avaliar(l)
        saida.append({
            "gancho": l,
            "checagens": {k: {"nota": round(v[0], 1), "detalhe": v[1]} for k, v in res.items()},
            "mais_fraco": min(CHECAGENS, key=lambda c: res[c][0]),
            "alertas": alertas, "nota": round(geral, 1), "veredito": veredito,
        })

    if args.json:
        print(json.dumps(saida if len(saida) > 1 else saida[0], indent=2, ensure_ascii=False))
    elif len(saida) == 1:
        mostrar_um(linhas[0], *avaliar(linhas[0]))
    else:
        mostrar_ranking(sorted(saida, key=lambda r: -r["nota"]))
    sys.exit(0 if max(s["nota"] for s in saida) >= 70 else 1)


if __name__ == "__main__":
    main()
