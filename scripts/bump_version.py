"""Change le numero de version de Pystart (source unique + CHANGELOG).

Usage :
    python scripts/bump_version.py 0.0.2

Ce script :
  1. verifie que le nouveau numero est bien superieur a l'actuel ;
  2. remplace `__version__` dans app/__init__.py ;
  3. ajoute (si besoin) une section `## [X.Y.Z] - AAAA-MM-JJ` dans CHANGELOG.md.

Il NE fait PAS le commit / tag / push : voir Docs/updates.md.
"""

from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT_FILE = ROOT / "app" / "__init__.py"
CHANGELOG = ROOT / "CHANGELOG.md"


def _current_version() -> str:
    text = INIT_FILE.read_text(encoding="utf-8")
    match = re.search(r'^__version__ = "([^"]+)"', text, re.MULTILINE)
    if not match:
        raise SystemExit("Impossible de trouver __version__ dans app/__init__.py")
    return match.group(1)


def _is_semver(value: str) -> bool:
    return re.fullmatch(r"\d+\.\d+\.\d+", value) is not None


def _tuple(value: str) -> tuple[int, int, int]:
    a, b, c = value.split(".")
    return int(a), int(b), int(c)


def bump(new_version: str) -> None:
    if not _is_semver(new_version):
        raise SystemExit(f"Version invalide : {new_version!r} (attendu MAJOR.MINOR.PATCH)")

    current = _current_version()
    if _tuple(new_version) <= _tuple(current):
        raise SystemExit(
            f"La nouvelle version ({new_version}) doit etre superieure a l'actuelle ({current})."
        )

    # 1. app/__init__.py
    text = INIT_FILE.read_text(encoding="utf-8")
    text = re.sub(
        r'^__version__ = "[^"]+"',
        f'__version__ = "{new_version}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    INIT_FILE.write_text(text, encoding="utf-8")
    print(f"app/__init__.py : {current} -> {new_version}")

    # 2. CHANGELOG.md
    changelog = CHANGELOG.read_text(encoding="utf-8")
    if f"## [{new_version}]" not in changelog:
        today = dt.date.today().isoformat()
        section = (
            f"## [{new_version}] - {today}\n\n"
            "### Added\n\n- \n\n### Changed\n\n- \n\n### Fixed\n\n- \n\n"
        )
        changelog = changelog.replace(
            "## [Non publie]\n", f"## [Non publie]\n\n{section}", 1
        )
        CHANGELOG.write_text(changelog, encoding="utf-8")
        print(f"CHANGELOG.md : section [{new_version}] ajoutee (a completer)")
    else:
        print(f"CHANGELOG.md : section [{new_version}] deja presente")

    print("\nEtapes suivantes :")
    print("  1. Completer la section du CHANGELOG.")
    print("  2. pytest")
    print(f'  3. git add -A && git commit -m "release: v{new_version}"')
    print(f"  4. git tag v{new_version} && git push origin HEAD --tags")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage : python scripts/bump_version.py X.Y.Z")
    bump(sys.argv[1])
