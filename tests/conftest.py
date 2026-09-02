"""Configuration commune aux tests.

On force `PYSTART_DATA_DIR` vers un dossier temporaire pour que les tests
n'ecrivent jamais dans les vraies donnees de l'utilisateur. Le module
`app.core.paths` relit cette variable a chaque appel, donc un simple
`monkeypatch.setenv` suffit.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("PYSTART_DATA_DIR", str(tmp_path / "data"))
    yield
