"""Tests de validation des noms de paquets (protection contre l'injection pip)."""

import pytest

from app.libraries.installer import InvalidPackageName, validate_requirement


@pytest.mark.parametrize("value", ["pygame", "requests==2.31.0", "rich>=13", "pytest-qt", "typing_extensions"])
def test_valid_requirements(value):
    assert validate_requirement(value) == value


@pytest.mark.parametrize("value", [
    "--upgrade",
    "-r requirements.txt",
    "pygame; rm -rf /",
    "pygame && echo hack",
    "",
    "http://evil/pkg.tar.gz",
])
def test_invalid_requirements(value):
    with pytest.raises(InvalidPackageName):
        validate_requirement(value)
