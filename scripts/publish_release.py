"""Publie une GitHub Release a partir d'un installeur construit localement.

A utiliser quand on ne veut pas passer par GitHub Actions (par ex. pas de
runner Windows disponible). Le token GitHub est lu depuis le gestionnaire
d'identifiants git (`git credential`) et n'est jamais affiche.

Prerequis :
  1. `python scripts/build.py`  puis  `iscc scripts/Pystart.iss`
     -> dist/Pystart-Setup-<version>.exe
  2. etre authentifie a GitHub (un simple `git push` doit fonctionner)

Usage :
  python scripts/publish_release.py            # publie la version courante
  python scripts/publish_release.py --draft    # cree un brouillon de release
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import GITHUB_OWNER, GITHUB_REPO, __version__  # noqa: E402

API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"


def _token() -> str:
    out = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for line in out.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    raise SystemExit("Aucun token GitHub trouve (fais `git push` une fois pour t'authentifier).")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publie la GitHub Release de Pystart.")
    parser.add_argument("--draft", action="store_true", help="cree un brouillon (non public)")
    args = parser.parse_args(argv)

    tag = f"v{__version__}"
    setup = ROOT / "dist" / f"Pystart-Setup-{__version__}.exe"
    if not setup.is_file():
        raise SystemExit(
            f"Installeur introuvable : {setup}\n"
            "Construis-le d'abord : python scripts/build.py && iscc scripts/Pystart.iss"
        )

    headers = {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "pystart-release",
    }

    digest = _sha256(setup)
    sums = ROOT / "dist" / "SHA256SUMS.txt"
    sums.write_text(f"{digest}  {setup.name}\n", encoding="utf-8")
    print(f"{setup.name}  ({setup.stat().st_size} octets)\nSHA-256: {digest}")

    existing = requests.get(f"{API}/releases/tags/{tag}", headers=headers, timeout=30)
    if existing.status_code == 200:
        release = existing.json()
        print(f"Release {tag} deja presente : {release['html_url']}")
    else:
        body = (
            f"**Installation (Windows)** : telecharge `{setup.name}`, double-clique, "
            f"suis l'assistant. Les mises a jour suivantes se font depuis "
            f"l'application (Aide > Mises a jour).\n\n"
            f"SHA-256 (`{setup.name}`) :\n```\n{digest}\n```\n\n"
            f"Details : voir le CHANGELOG."
        )
        response = requests.post(
            f"{API}/releases",
            headers=headers,
            timeout=30,
            json={
                "tag_name": tag,
                "target_commitish": "main",
                "name": f"Pystart {tag}",
                "body": body,
                "draft": args.draft,
                "prerelease": False,
            },
        )
        response.raise_for_status()
        release = response.json()
        print(f"Release creee : {release['html_url']}")

    upload_base = release["upload_url"].split("{", 1)[0]
    present = {a["name"]: a["id"] for a in release.get("assets", [])}
    for path, ctype in ((setup, "application/octet-stream"), (sums, "text/plain")):
        if path.name in present:
            requests.delete(
                f"{API}/releases/assets/{present[path.name]}", headers=headers, timeout=30
            )
        with path.open("rb") as handle:
            up = requests.post(
                f"{upload_base}?name={path.name}",
                headers={**headers, "Content-Type": ctype},
                data=handle,
                timeout=600,
            )
        up.raise_for_status()
        print(f"  asset : {up.json()['browser_download_url']}")

    print("\nVerification...")
    latest = requests.get(f"{API}/releases/latest", headers=headers, timeout=30).json()
    ok = latest.get("tag_name") == tag and any(
        a["name"] == setup.name for a in latest.get("assets", [])
    )
    print("OK - la release est publiee et telechargeable." if ok else "A VERIFIER manuellement.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
