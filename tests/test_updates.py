"""Tests du systeme de mise a jour (sans reseau : on simule la reponse GitHub)."""


import pytest

from app import __version__
from app.updates import update_manager
from app.updates.update_manager import UpdateError


class _FakeResponse:
    def __init__(self, payload, status_code=200, text=""):
        self._payload = payload
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"{self.status_code}")

    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self, payload, status_code=200, text="", raises=None):
        self._payload = payload
        self._status = status_code
        self._text = text
        self._raises = raises

    def get(self, *args, **kwargs):
        if self._raises is not None:
            raise self._raises
        return _FakeResponse(self._payload, self._status, self._text)


def _release_payload(tag="0.9.9", notes="", assets=None):
    return {
        "tag_name": tag,
        "body": notes,
        "html_url": f"https://github.com/kikilikiki/Pystart/releases/tag/v{tag}",
        "assets": assets or [],
    }


def test_check_detects_newer_version():
    payload = _release_payload(
        tag="9.9.9",
        notes="Nouveautes\n- test",
        assets=[{
            "name": "Pystart-Setup-9.9.9.exe",
            "browser_download_url": "https://github.com/kikilikiki/Pystart/releases/download/v9.9.9/Pystart-Setup-9.9.9.exe",
            "size": 1234,
        }],
    )
    info = update_manager.check(session=_FakeSession(payload))
    assert info.latest_version == "9.9.9"
    assert info.update_available
    assert info.download_url.startswith("https://github.com/")


def test_check_same_version_means_no_update():
    info = update_manager.check(session=_FakeSession(_release_payload(tag=__version__)))
    assert not info.update_available


def test_non_github_download_url_is_refused():
    payload = _release_payload(
        tag="9.9.9",
        assets=[{
            "name": "Pystart-Setup-9.9.9.exe",
            "browser_download_url": "https://evil.example.com/x.exe",
            "size": 10,
        }],
    )
    with pytest.raises(UpdateError):
        update_manager.check(session=_FakeSession(payload))


def test_sha256_is_parsed_from_notes():
    digest = "a" * 64
    payload = _release_payload(
        tag="9.9.9",
        notes=f"SHA-256: {digest}",
        assets=[{
            "name": "Pystart-Setup-9.9.9.exe",
            "browser_download_url": "https://github.com/kikilikiki/Pystart/releases/download/v9.9.9/Pystart-Setup-9.9.9.exe",
            "size": 10,
        }],
    )
    info = update_manager.check(session=_FakeSession(payload))
    assert info.sha256 == digest


def test_mandatory_flag_from_notes():
    payload = _release_payload(tag="9.9.9", notes="Cette version corrige un bug critique. [mandatory]")
    info = update_manager.check(session=_FakeSession(payload))
    assert info.mandatory


def test_no_release_yet_is_not_an_error():
    """Un depot sans aucune release renvoie 404 sur /releases/latest.

    Ce n'est pas une panne : l'utilisateur est simplement deja a jour.
    """
    session = _FakeSession({}, status_code=404, text='{"message": "Not Found"}')
    info = update_manager.check(session=session)
    assert not info.update_available
    assert info.latest_version == __version__


def test_connection_error_gives_friendly_message():
    import requests

    session = _FakeSession({}, raises=requests.exceptions.ConnectionError("boom"))
    with pytest.raises(UpdateError, match="connexion"):
        update_manager.check(session=session)


def test_ssl_error_gives_friendly_message():
    import requests

    session = _FakeSession({}, raises=requests.exceptions.SSLError("bad cert"))
    with pytest.raises(UpdateError, match="SSL"):
        update_manager.check(session=session)


def test_rate_limit_gives_friendly_message():
    session = _FakeSession({}, status_code=403, text="API rate limit exceeded for ...")
    with pytest.raises(UpdateError, match="quota"):
        update_manager.check(session=session)
