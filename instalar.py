#!/usr/bin/env python3
"""
instalar.py - copia as skills insta-* para ~/.claude/skills.

Rode de novo depois de um `git pull`. Só mexe em pastas insta-* que existem
neste repositório. A cópia anterior vai para ~/instagram-dados/copias-antigas.

  python instalar.py            # instala ou atualiza
  python instalar.py --listar   # só mostra o que faria
"""

import os
import shutil
import sys
import time

ORIGEM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
CASA = os.path.join(os.path.expanduser("~"), ".claude")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    listar = "--listar" in sys.argv[1:]
    destino = os.path.join(CASA, "skills")
    antigas = os.path.join(os.path.expanduser("~"), "instagram-dados", "copias-antigas", time.strftime("%Y%m%d-%H%M%S"))
    for nome in sorted(os.listdir(ORIGEM)):
        alvo = os.path.join(destino, nome)
        if not nome.startswith("insta-"):
            continue
        existe = os.path.lexists(alvo)
        print(("atualizar " if existe else "instalar  ") + nome)
        if listar:
            continue
        if existe:
            os.makedirs(antigas, exist_ok=True)
            shutil.move(alvo, os.path.join(antigas, nome))
        shutil.copytree(os.path.join(ORIGEM, nome), alvo,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


if __name__ == "__main__":
    main()
