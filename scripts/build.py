"""Construit Pystart et l'updater avec PyInstaller.

Usage :
    python scripts/build.py

Produit (dossier `dist/`) :
    dist/Pystart/Pystart.exe          l'application
    dist/Pystart/PystartUpdater.exe   l'updater separe
    dist/Pystart/content/             les cours livres

Sur les plateformes non Windows, le build fonctionne aussi (utile pour tester)
mais l'installeur Inno Setup ne se genere que sous Windows.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import __version__  # noqa: E402

DIST = ROOT / "dist"
BUILD = ROOT / "build"


def _run(args: list[str]) -> None:
    print("$", " ".join(args))
    subprocess.run(args, check=True, cwd=ROOT)


def clean() -> None:
    for path in (DIST, BUILD):
        if path.exists():
            shutil.rmtree(path)


def build() -> None:
    print(f"Construction de Pystart {__version__}")
    clean()

    sep = ";" if sys.platform.startswith("win") else ":"
    common = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean"]

    # 1. Application principale (fenetre, pas de console).
    _run([
        *common,
        "--name", "Pystart",
        "--windowed",
        "--add-data", f"content{sep}content",
        "--collect-submodules", "app",
        str(ROOT / "app" / "__main__.py"),
    ])

    # 2. Updater : un seul fichier (--onefile), petit programme console.
    _run([
        *common,
        "--name", "PystartUpdater",
        "--console",
        "--onefile",
        "--workpath", str(BUILD / "updater"),
        "--specpath", str(BUILD),
        "--distpath", str(BUILD / "updater-dist"),
        str(ROOT / "app" / "updates" / "updater_cli.py"),
    ])

    # On place l'updater a cote de l'executable principal, dans dist/Pystart/.
    exe_name = "PystartUpdater.exe" if sys.platform.startswith("win") else "PystartUpdater"
    updater_exe = BUILD / "updater-dist" / exe_name
    if updater_exe.exists():
        target = DIST / "Pystart" / exe_name
        shutil.copy2(updater_exe, target)
        print(f"Updater copie : {target}")
    else:
        raise SystemExit(f"Updater introuvable apres build : {updater_exe}")

    print(f"\nBuild termine : {DIST / 'Pystart'}")
    print("Etape suivante (Windows) : iscc scripts/Pystart.iss")


if __name__ == "__main__":
    build()
