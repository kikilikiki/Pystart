"""Gestion de l'environnement virtuel dedie au code de l'utilisateur.

Concept Python illustre : le module `venv`. Un environnement virtuel est un
dossier contenant un interpreteur Python isole et ses propres paquets. On en
cree un pour l'utilisateur afin que ses `pip install` n'affectent pas
Pystart.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from app.core import paths


def user_venv_dir() -> Path:
    """Dossier de l'environnement virtuel de l'utilisateur."""
    return paths.app_data_dir() / "user-venv"


def user_python_executable() -> Path:
    """Chemin de l'interpreteur Python dans l'environnement de l'utilisateur."""
    base = user_venv_dir()
    if sys.platform.startswith("win"):
        return base / "Scripts" / "python.exe"
    return base / "bin" / "python"


def venv_exists() -> bool:
    return user_python_executable().exists()


def ensure_user_venv() -> Path:
    """Cree l'environnement virtuel s'il n'existe pas encore. Renvoie l'interpreteur.

    On appelle `python -m venv` via un sous-processus (et non le module `venv`
    directement) : quand Pystart est installe, le processus courant n'est pas
    un interpreteur Python mais `Pystart.exe`.
    """
    if venv_exists():
        return user_python_executable()

    from app.core.python_env import find_python

    base_python = find_python() or sys.executable
    subprocess.run(
        [base_python, "-m", "venv", str(user_venv_dir())],
        check=True,
        capture_output=True,
        text=True,
    )
    return user_python_executable()


def pip_command(*args: str) -> list[str]:
    """Construit une commande `python -m pip ...` visant l'environnement utilisateur."""
    python = user_python_executable()
    if not python.exists():
        python = Path(sys.executable)
    return [str(python), "-m", "pip", *args]


def list_installed() -> list[tuple[str, str]]:
    """Renvoie la liste (nom, version) des paquets installes dans l'environnement."""
    if not venv_exists():
        return []
    result = subprocess.run(
        pip_command("list", "--format=freeze"),
        capture_output=True,
        text=True,
        check=False,
    )
    packages: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if "==" in line:
            name, _, ver = line.partition("==")
            packages.append((name.strip(), ver.strip()))
    return packages
