"""Configuration commune aux tests.

Les tests ne doivent JAMAIS lire ou ecrire les vraies donnees de
l'utilisateur (`%APPDATA%\\Pystart`). On redirige `PYSTART_DATA_DIR` vers un
dossier temporaire, et ce **des la collecte** (`pytest_configure`) : certains
modules de test appellent `load_all_courses()` au niveau module, avant que les
fixtures ne s'executent.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

# Dossier temporaire unique pour toute la session de test, pose avant tout
# import de code applicatif qui lirait la config.
_SESSION_DATA_DIR = Path(tempfile.mkdtemp(prefix="pystart_tests_"))


def pytest_configure(config):  # noqa: ARG001
    import os

    os.environ["PYSTART_DATA_DIR"] = str(_SESSION_DATA_DIR)


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Chaque test a en plus SON propre dossier de donnees, vierge."""
    monkeypatch.setenv("PYSTART_DATA_DIR", str(tmp_path / "data"))
    yield
