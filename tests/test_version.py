"""Tests de comparaison de versions (le piege classique 0.0.9 vs 0.0.10)."""

import pytest

from app.core import version


def test_0_0_10_is_newer_than_0_0_9():
    assert version.is_newer("0.0.10", "0.0.9")
    assert not version.is_newer("0.0.9", "0.0.10")


def test_equal_versions():
    assert version.compare("1.2.3", "1.2.3") == 0
    assert not version.is_newer("1.2.3", "1.2.3")


def test_leading_v_is_tolerated():
    assert version.parse("v0.0.2") == version.parse("0.0.2")


def test_minor_and_major_bumps():
    assert version.is_newer("0.1.0", "0.0.9")
    assert version.is_newer("1.0.0", "0.9.9")


def test_invalid_version_raises_value_error():
    with pytest.raises(ValueError):
        version.parse("pas-une-version")
