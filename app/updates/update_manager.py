"""Detection et telechargement des mises a jour depuis GitHub Releases.

Etapes d'une mise a jour en un clic (voir Docs/updates.md) :

    check() -> UpdateInfo
        |
    download(info) -> fichier .exe dans un dossier temporaire
        |
    verify(fichier, info)   (taille + SHA-256 si disponible)
        |
    lancer PystartUpdater.exe puis quitter Pystart
        |
    l'updater remplace/installe la nouvelle version et relance Pystart
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import requests

from app import RELEASES_API_URL, __version__
from app.core import paths, version

# On refuse tout ce qui n'est pas une release GitHub officielle en HTTPS.
_ALLOWED_HOST_PATTERN = re.compile(
    r"^https://(github\.com|objects\.githubusercontent\.com|api\.github\.com)/", re.IGNORECASE
)

# Nom de l'asset Windows attendu dans la release, ex: Pystart-Setup-0.0.2.exe
_SETUP_ASSET_PATTERN = re.compile(r"^Pystart-Setup-.*\.exe$", re.IGNORECASE)

USER_AGENT = f"Pystart-Updater/{__version__}"
REQUEST_TIMEOUT = 20


@dataclass
class UpdateInfo:
    """Informations sur la derniere version disponible."""

    latest_version: str
    current_version: str
    release_notes: str
    download_url: str
    asset_name: str
    asset_size: int
    sha256: str | None = None
    mandatory: bool = False
    html_url: str = ""

    @property
    def update_available(self) -> bool:
        try:
            return version.is_newer(self.latest_version, self.current_version)
        except ValueError:
            return False


class UpdateError(Exception):
    """Erreur pendant la verification ou le telechargement d'une mise a jour."""


def _require_allowed_url(url: str) -> None:
    if not _ALLOWED_HOST_PATTERN.match(url or ""):
        raise UpdateError(f"URL de mise a jour refusee (hors GitHub / non HTTPS) : {url!r}")


def _parse_sha256_from_notes(notes: str, asset_name: str) -> str | None:
    """Cherche une ligne du style `Pystart-Setup-0.0.2.exe  <sha256>` dans les notes."""
    for line in notes.splitlines():
        if asset_name.lower() in line.lower():
            match = re.search(r"\b([a-fA-F0-9]{64})\b", line)
            if match:
                return match.group(1).lower()
    match = re.search(r"sha-?256[^a-f0-9]*([a-fA-F0-9]{64})", notes, re.IGNORECASE)
    return match.group(1).lower() if match else None


def _no_release_info() -> UpdateInfo:
    """Renvoye quand le depot n'a encore aucune release publiee (HTTP 404).

    Ce n'est pas une erreur : l'utilisateur est simplement deja a jour.
    """
    return UpdateInfo(
        latest_version=__version__,
        current_version=__version__,
        release_notes="",
        download_url="",
        asset_name="",
        asset_size=0,
    )


def check(session: requests.Session | None = None) -> UpdateInfo:
    """Interroge l'API GitHub et renvoie les infos de la derniere release.

    Distingue les differents cas d'echec pour afficher un message utile :
    pas de reseau, DNS, certificat SSL, quota GitHub depasse, aucune release.
    """
    http = session or requests.Session()
    try:
        response = http.get(
            RELEASES_API_URL,
            headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.SSLError as error:
        raise UpdateError(
            "Erreur de certificat SSL en contactant GitHub. "
            "Verifie l'horloge systeme et ton antivirus/proxy."
        ) from error
    except requests.exceptions.ConnectionError as error:
        raise UpdateError(
            "Pas de connexion a GitHub. Verifie ta connexion Internet, "
            "puis reessaie."
        ) from error
    except requests.exceptions.Timeout as error:
        raise UpdateError("GitHub ne repond pas (delai depasse). Reessaie plus tard.") from error
    except requests.RequestException as error:
        raise UpdateError(f"Impossible de contacter GitHub : {error}") from error

    # 404 sur /releases/latest = aucune release publiee sur le depot.
    if response.status_code == 404:
        return _no_release_info()
    if response.status_code == 403 and "rate limit" in response.text.lower():
        raise UpdateError(
            "Trop de requetes vers GitHub pour l'instant (quota atteint). "
            "Reessaie dans une heure."
        )

    try:
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, json.JSONDecodeError) as error:
        raise UpdateError(f"Reponse inattendue de GitHub : {error}") from error

    tag = str(payload.get("tag_name", "")).lstrip("vV")
    if not tag:
        # Release sans tag exploitable : on considere qu'il n'y a rien de neuf.
        return _no_release_info()

    notes = str(payload.get("body", "") or "")
    # Une release est "obligatoire" si ses notes contiennent un marqueur explicite.
    lowered = notes.lower()
    mandatory = "[mandatory]" in lowered or "[obligatoire]" in lowered

    setup_asset = None
    for asset in payload.get("assets", []):
        if _SETUP_ASSET_PATTERN.match(str(asset.get("name", ""))):
            setup_asset = asset
            break

    download_url = ""
    asset_name = ""
    asset_size = 0
    if setup_asset:
        download_url = str(setup_asset.get("browser_download_url", ""))
        asset_name = str(setup_asset.get("name", ""))
        asset_size = int(setup_asset.get("size", 0))
        if download_url:
            _require_allowed_url(download_url)

    return UpdateInfo(
        latest_version=tag,
        current_version=__version__,
        release_notes=notes,
        download_url=download_url,
        asset_name=asset_name,
        asset_size=asset_size,
        sha256=_parse_sha256_from_notes(notes, asset_name) if asset_name else None,
        mandatory=mandatory,
        html_url=str(payload.get("html_url", "")),
    )


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(info: UpdateInfo, *, on_progress=None, session: requests.Session | None = None) -> Path:
    """Telecharge l'installeur dans un dossier temporaire et le verifie.

    Renvoie le chemin du fichier telecharge. Ne remplace jamais l'installation
    en place : c'est le role de l'updater separe.
    """
    if not info.download_url:
        raise UpdateError("Aucun installeur Windows (.exe) attache a cette release.")
    _require_allowed_url(info.download_url)

    target_dir = paths.app_data_dir() / "updates"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / (info.asset_name or f"Pystart-Setup-{info.latest_version}.exe")

    http = session or requests.Session()
    try:
        with http.get(
            info.download_url,
            headers={"User-Agent": USER_AGENT},
            stream=True,
            timeout=REQUEST_TIMEOUT,
        ) as response:
            response.raise_for_status()
            total = int(response.headers.get("Content-Length", info.asset_size or 0))
            written = 0
            with target.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    handle.write(chunk)
                    written += len(chunk)
                    if on_progress and total:
                        on_progress(written, total)
    except requests.RequestException as error:
        target.unlink(missing_ok=True)
        raise UpdateError(f"Echec du telechargement : {error}") from error

    _verify_download(target, info)
    return target


def _verify_download(path: Path, info: UpdateInfo) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise UpdateError("Le fichier telecharge est vide.")
    if info.asset_size and abs(path.stat().st_size - info.asset_size) > 4096:
        raise UpdateError(
            f"Taille inattendue : {path.stat().st_size} octets "
            f"au lieu de ~{info.asset_size}."
        )
    if info.sha256:
        actual = sha256_of(path)
        if actual.lower() != info.sha256.lower():
            path.unlink(missing_ok=True)
            raise UpdateError(
                "Empreinte SHA-256 incorrecte : le fichier telecharge est peut-etre "
                "corrompu ou falsifie. Mise a jour annulee."
            )
