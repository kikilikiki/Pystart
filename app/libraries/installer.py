"""Installation d'un paquet via pip, avec sortie en direct.

Concept Python illustre : lire la sortie d'un sous-processus *au fil de
l'eau* avec `Popen` et `stdout`, plutot que d'attendre la fin.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Iterator

from app.libraries.venv import ensure_user_venv, pip_command

# Un nom de paquet PyPI raisonnable : lettres, chiffres, tirets, underscores,
# points, et eventuellement une contrainte de version simple.
_SAFE_REQUIREMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*(\[[A-Za-z0-9,._-]+\])?([<>=!~]=?[0-9A-Za-z.*-]+)*$")


class InvalidPackageName(ValueError):
    """Nom de paquet refuse (protege contre l'injection d'options pip)."""


def validate_requirement(requirement: str) -> str:
    cleaned = requirement.strip()
    if not cleaned or cleaned.startswith("-") or not _SAFE_REQUIREMENT.match(cleaned):
        raise InvalidPackageName(
            f"Nom de paquet invalide : {requirement!r}. "
            "Exemples valides : pygame, requests==2.31.0, rich>=13"
        )
    return cleaned


def install(requirement: str) -> Iterator[str]:
    """Installe `requirement` et produit les lignes de sortie une par une.

    Utilisation typique dans l'interface :

        for line in install("pygame"):
            terminal.append(line)
    """
    package = validate_requirement(requirement)
    ensure_user_venv()

    command = pip_command("install", "--no-input", package)
    yield f"$ {' '.join(command)}\n"

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    # On relaie chaque ligne des qu'elle arrive (lecture "au fil de l'eau").
    for line in process.stdout:  # noqa: UP028 - forme explicite, plus lisible pour un debutant
        yield line
    process.wait()

    if process.returncode == 0:
        yield f"\n[OK] {package} est installe.\n"
    else:
        yield f"\n[ERREUR] Installation de {package} echouee (code {process.returncode}).\n"
