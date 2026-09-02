"""Tests du systeme de mise a jour (sans reseau : on simule la reponse GitHub)."""


import pytest

from app import __version__
from app.updates import update_manager
from app.updates.update_manager import UpdateError


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self, payload):
        self._payload = payload

    def get(self, *args, **kwargs):
        return _FakeResponse(self._payload)


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
