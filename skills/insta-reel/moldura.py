#!/usr/bin/env python3
"""
moldura.py - gera um PNG transparente 1080x1920 com a área segura do Reel.

Coloque como camada por cima do vídeo no editor (CapCut: Sobreposição) só
enquanto posiciona os textos, e apague antes de exportar. O que fica na faixa
vermelha é coberto pela interface do Instagram: legenda e nome do perfil
embaixo, botões de curtir/comentar/compartilhar na direita, abas em cima.

Medidas (em pixels, no quadro 1080x1920):
  topo       0 a 230      abas e câmera
  base       1440 a 1920  legenda, perfil, áudio
  direita    850 a 1080   coluna de botões
  quadro verde = onde texto e gancho ficam sempre visíveis

As medidas mudam um pouco entre celulares e atualizações do aplicativo; elas
são uma margem de segurança, não um encaixe exato. Ajuste com as opções.

Uso
  python moldura.py                       # grava moldura-reel-9x16.png aqui
  python moldura.py --saida minha.png --topo 250 --base 1400 --direita 240
"""

import argparse
import struct
import sys
import zlib

L, A = 1080, 1920
VERMELHO = (220, 38, 38, 90)       # faixa coberta, semitransparente
VERDE = (22, 163, 74, 255)         # contorno da área segura
NADA = (0, 0, 0, 0)
LINHA = 4                          # espessura do contorno em pixels


def png(largura, altura, linhas):
    """Escreve PNG RGBA 8 bits sem nenhuma biblioteca externa."""
    def bloco(tipo, dados):
        c = tipo + dados
        return struct.pack(">I", len(dados)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    cru = b"".join(b"\x00" + l for l in linhas)
    return (b"\x89PNG\r\n\x1a\n"
            + bloco(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 6, 0, 0, 0))
            + bloco(b"IDAT", zlib.compress(cru, 9))
            + bloco(b"IEND", b""))


def gerar(topo=230, base=1440, direita=230):
    x_dir = L - direita
    v, g, n = bytes(VERMELHO), bytes(VERDE), bytes(NADA)
    faixa = v * L
    linhas = []
    for y in range(A):
        if y < topo or y >= base:
            linhas.append(faixa)
            continue
        borda_h = y < topo + LINHA or y >= base - LINHA
        if borda_h:
            meio = g * x_dir
        else:
            meio = g * LINHA + n * (x_dir - 2 * LINHA) + g * LINHA
        linhas.append(meio + v * direita)
    return png(L, A, linhas)


def main():
    ap = argparse.ArgumentParser(description="Moldura de área segura para Reels 9:16.")
    ap.add_argument("--saida", default="moldura-reel-9x16.png")
    ap.add_argument("--topo", type=int, default=230)
    ap.add_argument("--base", type=int, default=1440, help="linha onde começa a faixa de baixo")
    ap.add_argument("--direita", type=int, default=230, help="largura da coluna de botões")
    a = ap.parse_args()
    if not (0 <= a.topo < a.base <= A and 0 <= a.direita < L - 2 * LINHA):
        print("medidas inválidas", file=sys.stderr)
        sys.exit(2)
    with open(a.saida, "wb") as f:
        f.write(gerar(a.topo, a.base, a.direita))
    print(f"moldura gravada em {a.saida} (1080x1920, área segura "
          f"x 0-{L - a.direita}, y {a.topo}-{a.base})")


if __name__ == "__main__":
    main()
