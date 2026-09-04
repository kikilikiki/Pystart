"""Construit l'archive portable Pystart-Portable-<version>.zip.

Contrairement a l'installeur (PyInstaller + Inno Setup), cette archive ne
contient QUE les sources + `Pystart.bat`. Elle ne necessite ni compilation,
ni droits administrateur, ni executable non signe : `Pystart.bat` utilise le
Python deja installe sur la machine (voir Docs/installation.md, Option A).

Usage :
    python scripts/build_portable_zip.py
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import __version__  # noqa: E402

# Fichiers et dossiers inclus dans l'archive portable (le strict necessaire
# pour lancer Pystart depuis les sources).
INCLUDE = [
    "Pystart.bat",
    "requirements.txt",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "app",
    "content",
]

# Extensions exclues meme dans les dossiers inclus (fichiers de developpement).
EXCLUDE_SUFFIXES = {".pyc"}
EXCLUDE_DIR_NAMES = {"__pycache__"}


def _iter_files(path: Path):
    if path.is_file():
        yield path
        return
    for child in sorted(path.rglob("*")):
        if child.is_dir():
            continue
        if any(part in EXCLUDE_DIR_NAMES for part in child.parts):
            continue
        if child.suffix in EXCLUDE_SUFFIXES:
            continue
        yield child


def build(dist_dir: Path | None = None) -> Path:
    """Construit l'archive et renvoie son chemin.

    `dist_dir` est parametrable (utilise par les tests) ; par defaut
    `dist/` a la racine du projet.
    """
    dist_dir = Path(dist_dir) if dist_dir else ROOT / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dist_dir / f"Pystart-Portable-{__version__}.zip"

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in INCLUDE:
            source = ROOT / name
            if not source.exists():
                raise SystemExit(f"Manquant : {source}")
            for file_path in _iter_files(source):
                # Tout range sous un dossier racine "Pystart/" dans l'archive,
                # pour que la decompression cree un dossier propre.
                arcname = Path("Pystart") / file_path.relative_to(ROOT)
                archive.write(file_path, arcname.as_posix())

    print(f"Archive portable creee : {archive_path} ({archive_path.stat().st_size:,} octets)")
    return archive_path


if __name__ == "__main__":
    build()
