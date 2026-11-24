#!/usr/bin/env python3
"""
carrossel.py - confere o texto de um carrossel e gera os PNG 1080x1350.

Entrada: slides separados por uma linha `---`. A primeira linha de cada slide
é o título; o resto é o apoio.

  TÍTULO DA CAPA
  Uma linha de promessa.
  ---
  Outro título
  Até 25 palavras de apoio.

Os PNG são gerados com o Chrome ou Edge já instalado, sem internet.
Sem navegador, sobra o HTML de cada slide.

Uso
  python carrossel.py slides.txt                       # só confere
  python carrossel.py slides.txt --saida pasta --perfil @meuperfil --cor "#FF7A00"
"""

import argparse
import html
import os
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import tempfile

MODELO = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}html,body{{width:1080px;height:1350px;overflow:hidden}}
body{{background:{fundo};color:{texto};font-family:"Segoe UI",Roboto,Arial,sans-serif;padding:130px 120px;
display:flex;flex-direction:column;justify-content:center;position:relative}}
h1{{font-size:{tam}px;line-height:1.08;font-weight:800;overflow-wrap:anywhere}}
p{{font-size:46px;line-height:1.35;margin-top:44px;white-space:pre-line}}
i{{display:block;width:120px;height:12px;background:{cor};margin-bottom:44px}}
footer{{position:absolute;left:120px;right:120px;bottom:70px;display:flex;justify-content:space-between;
font-size:32px;opacity:.8}}
</style></head><body><i></i><h1>{titulo}</h1><p>{apoio}</p>
<footer><span>{perfil}</span><span>{num}</span></footer></body></html>"""


def ler(texto):
    slides = []
    for bloco in re.split(r"(?m)^---[ \t]*$", texto.lstrip("﻿")):
        linhas = [l.strip() for l in bloco.strip().splitlines()]
        if linhas:
            slides.append({"titulo": linhas[0], "apoio": "\n".join(linhas[1:]).strip()})
    return slides


def conferir(slides):
    """Lista de (nível, mensagem)."""
    out, n = [], len(slides)
    if n > 20:
        out.append(("FALHA", f"{n} slides: o limite é 20"))
    elif not 6 <= n <= 10:
        out.append(("AVISO", f"{n} slides: de 6 a 10 é a faixa recomendada"))
    if slides and len(slides[0]["titulo"].split()) > 6:
        out.append(("AVISO", "capa com mais de 6 palavras: difícil de ler na grade"))
    for i, s in enumerate(slides, 1):
        if i > 1 and len(s["titulo"].split()) > 9:
            out.append(("AVISO", f"slide {i}: título longo (até 7 palavras)"))
        apoio = len(s["apoio"].split())
        if apoio > 25 and i != n - 1:      # o penúltimo é o resumo
            out.append(("FALHA", f"slide {i}: {apoio} palavras de apoio (até 25); divida em dois"))
        elif apoio > 60:
            out.append(("FALHA", f"slide {i}: resumo com {apoio} palavras (até 60)"))
        if re.search(r"\{\{.+?\}\}", s["titulo"] + s["apoio"]):
            out.append(("FALHA", f"slide {i}: ainda tem campo por preencher"))
    return out


def navegador():
    for nome in ("google-chrome", "chromium", "chrome", "msedge"):
        if shutil.which(nome):
            return shutil.which(nome)
    for raiz in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        for rel in (r"Google\Chrome\Application\chrome.exe", r"Microsoft\Edge\Application\msedge.exe"):
            base = os.environ.get(raiz)
            if base and os.path.exists(os.path.join(base, rel)):
                return os.path.join(base, rel)
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    return mac if os.path.exists(mac) else None


def pagina(s, i, n, perfil, cor, fundo, texto):
    tam = 112 if i == 1 else 80
    if len(s["titulo"]) > 45:
        tam = int(tam * 0.75)
    return MODELO.format(titulo=html.escape(s["titulo"]), apoio=html.escape(s["apoio"]),
                         perfil=html.escape(perfil), num=f"{i}/{n}", tam=tam,
                         cor=cor, fundo=fundo, texto=texto)


def gerar(slides, pasta, perfil="", cor="#FF7A00", fundo="#0F1B2D", texto="#FFFFFF"):
    os.makedirs(pasta, exist_ok=True)
    nav, feitos = navegador(), []
    for i, s in enumerate(slides, 1):
        h = os.path.abspath(os.path.join(pasta, f"slide-{i:02d}.html"))
        with open(h, "w", encoding="utf-8") as f:
            f.write(pagina(s, i, len(slides), perfil, cor, fundo, texto))
        if not nav:
            feitos.append(h)
            continue
        png = h[:-5] + ".png"
        if os.path.exists(png):
            os.remove(png)
        # Perfil temporário: não encosta no Chrome aberto da pessoa.
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as perfil_tmp:
            subprocess.run([nav, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                            f"--user-data-dir={perfil_tmp}", "--force-device-scale-factor=1",
                            "--window-size=1080,1350", f"--screenshot={png}", pathlib.Path(h).as_uri()],
                           check=True, timeout=60, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(png, "rb") as f:
            if struct.unpack(">II", f.read(24)[16:24]) != (1080, 1350):
                raise RuntimeError(f"{png} não saiu em 1080x1350")
        os.remove(h)
        feitos.append(png)
    return feitos


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Confere e gera os slides de um carrossel.")
    ap.add_argument("entrada")
    ap.add_argument("--saida")
    ap.add_argument("--perfil", default="")
    ap.add_argument("--cor", default="#FF7A00")
    ap.add_argument("--fundo", default="#0F1B2D")
    ap.add_argument("--texto", default="#FFFFFF")
    args = ap.parse_args()
    for c in (args.cor, args.fundo, args.texto):
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", c):
            ap.error(f"cor inválida: {c} (use #RRGGBB)")
    with open(args.entrada, encoding="utf-8") as f:
        slides = ler(f.read())
    if not slides:
        ap.error("nenhum slide no arquivo")
    for i, s in enumerate(slides, 1):
        print(f"  {i}/{len(slides)}  {s['titulo']}")
    avisos = conferir(slides)
    for nivel, msg in avisos:
        print(f"  {nivel}  {msg}")
    if any(n == "FALHA" for n, _ in avisos):
        sys.exit(1)
    if args.saida:
        for p in gerar(slides, args.saida, args.perfil, args.cor, args.fundo, args.texto):
            print("  gerado", p)


if __name__ == "__main__":
    main()
