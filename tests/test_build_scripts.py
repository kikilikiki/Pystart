"""Tests des scripts de build (rapides, sans PyInstaller ni Inno Setup).

`scripts/build.py` (PyInstaller) et `scripts/Pystart.iss` (Inno Setup) ne sont
pas testes ici : ils necessitent des outils externes et sont couverts par le
workflow `release.yml`. Ce module teste uniquement l'archive portable, qui ne
depend que de la bibliotheque standard.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_portable_zip  # noqa: E402

from app import __version__  # noqa: E402


def test_portable_zip_contains_expected_files(tmp_path):
    archive_path = build_portable_zip.build(dist_dir=tmp_path)

    assert archive_path.name == f"Pystart-Portable-{__version__}.zip"
    assert archive_path.is_file()

    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()

    assert "Pystart/Pystart.bat" in names
    assert "Pystart/requirements.txt" in names
    assert "Pystart/README.md" in names
    assert any(n.startswith("Pystart/app/") for n in names)
    assert any(n.startswith("Pystart/content/courses/01_hello_world/") for n in names)


def test_portable_zip_excludes_dev_files(tmp_path):
    archive_path = build_portable_zip.build(dist_dir=tmp_path)
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()

    assert not any(n.startswith("Pystart/tests/") for n in names)
    assert not any(n.startswith("Pystart/.github/") for n in names)
    assert not any(n.startswith("Pystart/scripts/") for n in names)
    assert not any("__pycache__" in n for n in names)
    assert not any(n.endswith(".pyc") for n in names)


def test_portable_zip_bat_uses_requirements_and_app_module():
    """Verifie que Pystart.bat installe bien requirements.txt et lance `-m app`."""
    bat_text = (ROOT / "Pystart.bat").read_text(encoding="utf-8")
    assert "requirements.txt" in bat_text
    assert "-m app" in bat_text
    assert "venv" in bat_text.lower()
