#!/usr/bin/env python3
"""
tempos.py - transforma o roteiro de um Reel num mapa de tempos antes de gravar.

Calcula quanto tempo cada fala leva, empilha em minutagem e aponta as quatro
coisas que matam um Reel na edição: gancho que passa dos 3 segundos, trecho
longo demais sem mudar a imagem, sequência de falas sem nada concreto e
duração fora do alvo.

Diferente do original em inglês (que conta palavras), aqui o tempo é estimado
por SÍLABAS: em português "é" e "configuração" são uma palavra cada, mas não
levam o mesmo tempo para falar. O padrão é 5 sílabas por segundo, ritmo de
narração clara. Meça o seu com --calibrar e use --sps daí em diante.

Formato do roteiro
  Uma fala por linha. Linha vazia é ignorada.
  Texto que vai NA TELA (cartela) fica entre colchetes, na linha de cima da
  fala em que ele aparece:
      [tela: 5 HORAS -> 20 MIN]
      Orçamento que levava cinco horas agora sai em vinte minutos.

Uso
  python tempos.py roteiro.txt
  python tempos.py roteiro.txt --alvo 30
  python tempos.py roteiro.txt --sps 5.6 --alvo 45
  python tempos.py roteiro.txt --srt-fala fala.srt --srt-tela tela.srt
  python tempos.py roteiro.txt --calibrar 27.5     # você leu em 27,5 s
  python tempos.py roteiro.txt --json

Os .srt importam direto no CapCut (Texto > Legendas > Importar) e em qualquer
editor de vídeo. O de tela vira a trilha de cartelas no tempo certo; o de fala
serve de guia até você trocar pela legenda automática do áudio real.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptbr  # noqa: E402

JANELA_GANCHO = 3.0   # segundos. Depois disso o polegar já decidiu.
TRECHO_MAX = 4.0      # segundos numa ideia só, sem mudar a imagem.
SEQ_ABSTRATA = 3      # falas seguidas sem nada que dê para conferir.
SPS_PADRAO = 5.0      # sílabas por segundo.
TELA_RE = re.compile(r"^\s*\[\s*tela\s*:\s*(.+?)\s*\]\s*$", re.IGNORECASE)
FRASE_RE = re.compile(r"[^.!?]+[.!?]*")


def concretos(texto):
    """Número, nome próprio, número falado ou palavra de dinheiro."""
    toks = ptbr.minusculas(texto)
    return (sum(1 for t in toks if ptbr.eh_numero(t))
            + len(ptbr.nomes_proprios(texto))
            + sum(1 for t in toks if t in ptbr.NUMEROS_FALADOS or t in ptbr.PALAVRAS_DINHEIRO))


def ler_roteiro(bruto, sps):
    """Devolve [(fala, [cartelas])]. Fala longa demais é quebrada nas frases."""
    trechos, cartelas = [], []
    for linha in [l.strip() for l in bruto.splitlines()]:
        if not linha:
            continue
        m = TELA_RE.match(linha)
        if m:
            cartelas.append(m.group(1))
            continue
        if ptbr.silabas(linha) / sps <= TRECHO_MAX * 1.5:
            trechos.append((linha, cartelas))
            cartelas = []
            continue
        partes = [p.strip() for p in FRASE_RE.findall(linha) if p.strip()]
        buf = ""
        for parte in partes:
            junto = (buf + " " + parte).strip()
            if buf and ptbr.silabas(junto) / sps > TRECHO_MAX:
                trechos.append((buf, cartelas))
                cartelas = []
                buf = parte
            else:
                buf = junto
        if buf:
            trechos.append((buf, cartelas))
            cartelas = []
    if cartelas and trechos:              # cartela solta no fim: vai no último
        trechos[-1][1].extend(cartelas)
    return trechos


def analisar(bruto, sps=SPS_PADRAO, alvo=None):
    trechos = ler_roteiro(bruto, sps)
    if not trechos:
        return None

    linhas, relogio = [], 0.0
    for i, (texto, cartelas) in enumerate(trechos):
        sil = ptbr.silabas(texto)
        dur = sil / sps
        linhas.append({
            "n": i + 1, "inicio": round(relogio, 2), "dur": round(dur, 2),
            "silabas": sil, "palavras": len(ptbr.palavras(texto)),
            "texto": texto, "tela": list(cartelas),
            "concretos": concretos(texto), "rotulo": "", "alertas": [],
        })
        relogio += dur
    total = relogio

    for r in linhas:
        if r["n"] == 1 or r["inicio"] + r["dur"] <= JANELA_GANCHO:
            r["rotulo"] = "GANCHO"
    linhas[-1]["rotulo"] = "CHAMADA" if linhas[-1]["rotulo"] != "GANCHO" else "GANCHO/CHAMADA"
    meio = total / 2
    for r in linhas:
        if not r["rotulo"] and r["inicio"] <= meio < r["inicio"] + r["dur"]:
            r["rotulo"] = "MEIO"

    notas = []
    g = linhas[0]
    if g["dur"] > JANELA_GANCHO:
        g["alertas"].append(f"gancho leva {g['dur']:.1f}s, passa dos {JANELA_GANCHO:.0f}s")
        notas.append(f"A fala 1 leva {g['dur']:.1f}s. Corte para umas "
                     f"{int(JANELA_GANCHO * sps)} sílabas, senão o gancho chega depois que a "
                     "pessoa já decidiu passar.")
    if g["concretos"] == 0:
        notas.append("A fala 1 não tem número, nome nem valor. Gancho sem nada que dê "
                     "para conferir é o que mais se pula.")
    if not g["tela"]:
        notas.append("Nenhuma cartela [tela: ...] no gancho. O texto na tela é lido antes "
                     "do áudio ser ouvido: ele precisa estar lá no primeiro quadro.")

    for r in linhas:
        if r["dur"] > TRECHO_MAX:
            r["alertas"].append(f"{r['dur']:.1f}s numa fala só")
    longos = [r["n"] for r in linhas if r["dur"] > TRECHO_MAX]
    if longos:
        notas.append(f"Fala(s) {', '.join(map(str, longos))} passam de {TRECHO_MAX:.0f}s. "
                     "Divida a frase ou mude a imagem no meio dela. Tela parada é onde "
                     "a pessoa sai.")

    seq, ini = 0, None
    for r in linhas:
        if r["concretos"] == 0:
            seq += 1
            ini = ini if ini is not None else r["n"]
            if seq == SEQ_ABSTRATA:
                notas.append(f"Falas {ini}-{r['n']} não têm nada concreto. Coloque um "
                             "número, um nome ou um valor em uma delas.")
        else:
            seq, ini = 0, None

    def assunto(texto):
        return {ptbr.raiz(p): p for p in ptbr.minusculas(texto)
                if p not in ptbr.STOPWORDS and len(p) > 2}
    no_gancho = assunto(linhas[0]["texto"])
    eco = sorted(no_gancho[k] for k in no_gancho.keys() & assunto(linhas[-1]["texto"]).keys())
    if len(linhas) > 1 and eco:
        notas.append(f"Fecha o ciclo: a última fala repete \"{', '.join(eco[:3])}\" do "
                     "gancho. Quem assiste de novo emenda sem perceber.")
    elif len(linhas) > 1:
        notas.append("Sem ciclo. A última fala não repete nenhuma palavra do gancho, então "
                     "o vídeo termina seco. Repetir uma palavra da fala 1 é o replay mais "
                     "barato que existe.")

    if alvo:
        dif = total - alvo
        if abs(dif) <= alvo * 0.1:
            notas.append(f"Duração no alvo ({total:.1f}s para {alvo:.0f}s).")
        elif dif > 0:
            notas.append(f"{dif:.1f}s acima do alvo. Corte umas {int(dif * sps)} sílabas.")
        else:
            notas.append(f"{-dif:.1f}s abaixo do alvo. Acrescente umas {int(-dif * sps)} "
                         "sílabas ou grave curto mesmo. Curto quase sempre é melhor.")

    return {
        "sps": sps, "alvo": alvo, "total_segundos": round(total, 2),
        "total_palavras": sum(r["palavras"] for r in linhas),
        "total_silabas": sum(r["silabas"] for r in linhas),
        "trechos": linhas, "notas": notas,
    }


def tc(seg):
    m, s = divmod(seg, 60)
    return f"{int(m)}:{s:04.1f}"


def tc_srt(seg):
    ms = int(round(seg * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def quebrar_legenda(texto, largura=32):
    """Até duas linhas de ~32 caracteres, que é o que cabe legível no 9:16."""
    blocos, linha, atual = [], [], []
    for p in texto.split():
        if len(" ".join(linha + [p])) > largura and linha:
            atual.append(" ".join(linha))
            linha = [p]
            if len(atual) == 2:
                blocos.append(atual)
                atual = []
        else:
            linha.append(p)
    if linha:
        atual.append(" ".join(linha))
    if atual:
        blocos.append(atual)
    return ["\n".join(b) for b in blocos]


def srt_fala(a):
    """Cada fala vira 1+ legendas; o tempo da fala é dividido pelos blocos."""
    itens, n = [], 0
    for r in a["trechos"]:
        blocos = quebrar_legenda(r["texto"])
        pesos = [max(1, ptbr.silabas(b)) for b in blocos]
        t = r["inicio"]
        for b, w in zip(blocos, pesos):
            d = r["dur"] * w / sum(pesos)
            n += 1
            itens.append(f"{n}\n{tc_srt(t)} --> {tc_srt(t + d)}\n{b}\n")
            t += d
    return "\n".join(itens)


def srt_tela(a):
    """Cartela fica na tela da fala onde foi marcada até a próxima cartela."""
    marcas = [(r["inicio"], c) for r in a["trechos"] for c in r["tela"]]
    fim = a["total_segundos"]
    itens = []
    for i, (ini, texto) in enumerate(marcas):
        ate = marcas[i + 1][0] if i + 1 < len(marcas) else fim
        if ate <= ini:                       # duas cartelas na mesma fala
            ate = ini + 1.0
        itens.append(f"{i + 1}\n{tc_srt(ini)} --> {tc_srt(ate)}\n{texto}\n")
    return "\n".join(itens)


def mostrar(a, out=sys.stdout):
    cab = (f"MAPA DE TEMPOS  ·  {a['total_palavras']} palavras  ·  {a['total_silabas']} sílabas"
           f"  ·  ~{a['total_segundos']:.1f}s a {a['sps']:g} síl/s"
           + (f"  ·  alvo {a['alvo']:g}s" if a["alvo"] else ""))
    print("\n" + cab, file=out)
    print("=" * max(len(cab), 72), file=out)
    for r in a["trechos"]:
        rot = f"{r['rotulo']:<15}" if r["rotulo"] else " " * 15
        for c in r["tela"]:
            print(f"  {'':>6}  {'':>5}  {'':<15}[tela] {c}", file=out)
        print(f"  {tc(r['inicio'])}  {r['dur']:4.1f}s  {rot}{r['texto']}", file=out)
        for al in r["alertas"]:
            print(f"  {'':>6}  {'':>5}  {'':<15}^ {al}", file=out)
    print("-" * max(len(cab), 72), file=out)
    for n in a["notas"]:
        print(f"  - {n}", file=out)
    print("", file=out)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Mapa de tempos de um roteiro de Reel.")
    ap.add_argument("entrada", nargs="?", default="-", help="arquivo do roteiro, ou - para stdin")
    ap.add_argument("--sps", type=float, default=SPS_PADRAO,
                    help=f"sílabas por segundo da sua fala (padrão {SPS_PADRAO:g})")
    ap.add_argument("--alvo", type=float, help="duração desejada em segundos")
    ap.add_argument("--calibrar", type=float, metavar="SEGUNDOS",
                    help="quanto tempo você levou lendo o roteiro em voz alta; devolve o seu --sps")
    ap.add_argument("--srt-fala", metavar="ARQ", help="grava legenda da fala em .srt")
    ap.add_argument("--srt-tela", metavar="ARQ", help="grava as cartelas [tela: ...] em .srt")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.entrada == "-":
        bruto = sys.stdin.read()
    else:
        with open(args.entrada, encoding="utf-8") as f:
            bruto = f.read()

    if args.calibrar:
        fala = "\n".join(l for l in bruto.splitlines() if not TELA_RE.match(l))
        sil = ptbr.silabas(fala)
        if not sil or args.calibrar <= 0:
            print("roteiro vazio ou tempo inválido", file=sys.stderr)
            sys.exit(2)
        sps = sil / args.calibrar
        print(f"{sil} sílabas em {args.calibrar:g}s = {sps:.2f} sílabas por segundo.")
        print(f"Use daqui em diante:  --sps {sps:.1f}")
        print("Dica: anote no seu voz.md, no campo Ritmo.")
        return

    a = analisar(bruto, sps=args.sps, alvo=args.alvo)
    if not a:
        print("roteiro vazio", file=sys.stderr)
        sys.exit(2)
    if args.srt_fala:
        with open(args.srt_fala, "w", encoding="utf-8") as f:
            f.write(srt_fala(a))
    if args.srt_tela:
        with open(args.srt_tela, "w", encoding="utf-8") as f:
            f.write(srt_tela(a))
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        mostrar(a)
        for nome, arq in (("fala", args.srt_fala), ("tela", args.srt_tela)):
            if arq:
                print(f"  legenda de {nome} gravada em {arq}")


if __name__ == "__main__":
    main()
