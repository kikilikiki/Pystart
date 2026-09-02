"""Pystart - une application desktop pour apprendre Python en pratiquant.

Ce fichier est le *point unique* où le numero de version de l'application
est defini. Tous les autres composants (interface "A propos", systeme de
mise a jour, installeur, workflow de release) lisent cette valeur.

Ne definis JAMAIS le numero de version ailleurs a la main.
"""

from __future__ import annotations

# --- Source unique de verite pour la version -------------------------------
# Format : MAJOR.MINOR.PATCH  (voir Docs/updates.md)
__version__ = "0.0.1"

# Nom du depot GitHub officiel, utilise par le systeme de mise a jour.
GITHUB_OWNER = "kikilikiki"
GITHUB_REPO = "Pystart"
GITHUB_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}"
RELEASES_API_URL = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)

# Coordonnees de contact affichees dans la page "A propos".
CONTACT_DISCORD_PSEUDO = "feelsmanvt"
CONTACT_DISCORD_INVITE = "https://discord.gg/haPVTW3Zqs"
CONTACT_EMAIL = "pystartcontact@gmail.com"
AUTHOR = "feelsmanvt"


def get_version() -> str:
    """Retourne la version courante de Pystart sous forme de chaine."""
    return __version__
