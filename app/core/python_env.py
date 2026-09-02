"""Trouver un interpreteur Python utilisable pour executer le code des eleves.

Cas simple (lancement depuis les sources) : c'est `sys.executable`.

Cas de l'application installee (gelee par PyInstaller) : `sys.executable`
pointe vers `Pystart.exe`, qui n'est PAS un interpreteur Python. On cherche
alors un Python du systeme :
  - l'environnement virtuel dedie a l'utilisateur, s'il existe ;
  - le lanceur `py -3` (Windows) ;
  - `python3` / `python` dans le PATH.

Si rien n'est trouve, `find_python()` renvoie None et l'interface affiche un
message clair (voir Docs/execution.md : limitation connue de la 0.0.x).
"""

from __future__ import annotations

import functools
import shutil
import subprocess
import sys


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def _works(candidate: list[str]) -> bool:
    try:
        result = subprocess.run(
            [*candidate, "-c", "import sys; print(sys.version_info[0])"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip().startswith("3")
    except (OSError, subprocess.SubprocessError):
        return False


@functools.lru_cache(maxsize=1)
def find_python() -> str | None:
    """Renvoie une commande (chemin) vers un Python 3 utilisable, ou None."""
    # 1. Environnement virtuel de l'utilisateur.
    try:
        from app.libraries.venv import user_python_executable, venv_exists

        if venv_exists():
            candidate = str(user_python_executable())
            if _works([candidate]):
                return candidate
    except Exception:  # pragma: no cover - defensif
        pass

    # 2. Depuis les sources : l'interpreteur courant.
    if not _is_frozen() and _works([sys.executable]):
        return sys.executable

    # 3. Application installee : chercher un Python du systeme.
    for name in ("python3", "python"):
        found = shutil.which(name)
        if found and _works([found]):
            return found

    if sys.platform.startswith("win"):
        try:
            result = subprocess.run(
                ["py", "-3", "-c", "import sys; print(sys.executable)"],
                capture_output=True, text=True, timeout=10, check=False,
            )
            path = result.stdout.strip()
            if result.returncode == 0 and path and _works([path]):
                return path
        except (OSError, subprocess.SubprocessError):
            pass

    return None
