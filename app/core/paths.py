"""Emplacement des fichiers de Pystart.

On distingue deux familles de dossiers :

1. Les fichiers *livres avec l'application* (le contenu des cours par defaut,
   les assets). Ils sont en lecture seule et voyagent avec le programme.

2. Les fichiers *de l'utilisateur* (profil, progression, cours perso, projets,
   preferences). Ils vivent dans le dossier de donnees de l'utilisateur et
   NE DOIVENT JAMAIS etre supprimes lors d'une mise a jour.

`APP_DATA_DIR` change selon le systeme d'exploitation :
    Windows : C:/Users/<nom>/AppData/Roaming/Pystart
    Linux   : ~/.local/share/Pystart
    macOS   : ~/Library/Application Support/Pystart

On peut forcer un autre dossier via la variable d'environnement
`PYSTART_DATA_DIR` (tres utile pour les tests et le mode developpement).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Pystart"


def _project_root() -> Path:
    """Racine du projet quand on lance depuis les sources (dossier au-dessus de app/)."""
    return Path(__file__).resolve().parents[2]


def bundled_root() -> Path:
    """Dossier contenant les ressources livrees avec l'application.

    Quand l'application est "gelee" par PyInstaller, les fichiers sont
    extraits dans `sys._MEIPASS`. Sinon, on utilise la racine du projet.
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return _project_root()


def content_dir() -> Path:
    """Dossier `content/` livre avec l'application (cours par defaut)."""
    return bundled_root() / "content"


def default_courses_dir() -> Path:
    """Dossier des cours fournis d'origine."""
    return content_dir() / "courses"


def app_data_dir() -> Path:
    """Dossier de donnees de l'utilisateur (cree s'il n'existe pas)."""
    override = os.environ.get("PYSTART_DATA_DIR")
    if override:
        base = Path(override).expanduser()
    elif sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming")) / APP_NAME
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Application Support" / APP_NAME
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / APP_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def user_courses_dir() -> Path:
    """Cours crees ou importes par l'utilisateur / le professeur."""
    path = app_data_dir() / "courses"
    path.mkdir(parents=True, exist_ok=True)
    return path


def user_projects_dir() -> Path:
    """Projets personnels de l'utilisateur."""
    path = app_data_dir() / "projects"
    path.mkdir(parents=True, exist_ok=True)
    return path


def workspace_dir() -> Path:
    """Dossier de travail temporaire ou l'on ecrit le code a executer."""
    path = app_data_dir() / "workspace"
    path.mkdir(parents=True, exist_ok=True)
    return path


def database_path() -> Path:
    """Fichier SQLite qui contient profils, progression et statistiques."""
    return app_data_dir() / "pystart.db"


def config_path() -> Path:
    """Fichier JSON des preferences (theme, dernier cours ouvert, etc.)."""
    return app_data_dir() / "config.json"


def logs_dir() -> Path:
    path = app_data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path
