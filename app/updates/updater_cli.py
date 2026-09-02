"""Updater separe : PystartUpdater(.exe).

Pourquoi un programme separe ? Sous Windows, un programme en cours
d'execution ne peut pas se remplacer lui-meme (ses fichiers sont
verrouilles). L'updater est un tout petit programme independant qui :

    1. attend que Pystart soit ferme ;
    2. lance l'installeur telecharge (mode silencieux si possible) ;
    3. relance Pystart ;
    4. en cas d'echec, ne touche pas a l'installation existante.

Il est volontairement minimal et sans dependance lourde.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def _wait_for_process_exit(pid: int, timeout: float = 30.0) -> None:
    """Attend la fin du processus `pid` (au plus `timeout` secondes)."""
    if pid <= 0:
        return
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not _process_is_running(pid):
            return
        time.sleep(0.5)


def _process_is_running(pid: int) -> bool:
    if sys.platform.startswith("win"):
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True,
            check=False,
        )
        return str(pid) in result.stdout
    try:
        import os

        os.kill(pid, 0)
    except OSError:
        return False
    return True


def run_update(installer: Path, wait_pid: int, relaunch: Path | None) -> int:
    """Execute la mise a jour. Renvoie un code de sortie (0 = succes)."""
    if not installer.is_file():
        print(f"[updater] Installeur introuvable : {installer}", file=sys.stderr)
        return 2

    _wait_for_process_exit(wait_pid)

    # `/SILENT` et `/NORESTART` sont les options d'Inno Setup.
    command = [str(installer), "/SILENT", "/NORESTART"]
    print(f"[updater] Lancement de l'installeur : {command}")
    try:
        completed = subprocess.run(command, check=False)
    except OSError as error:
        print(f"[updater] Echec du lancement de l'installeur : {error}", file=sys.stderr)
        return 3

    if completed.returncode != 0:
        print(
            f"[updater] L'installeur s'est termine avec le code {completed.returncode}. "
            "L'ancienne version reste en place.",
            file=sys.stderr,
        )
        return completed.returncode

    if relaunch and relaunch.exists():
        print(f"[updater] Redemarrage de Pystart : {relaunch}")
        subprocess.Popen([str(relaunch)])  # noqa: S603  (chemin fourni par Pystart)

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="PystartUpdater", description="Updater de Pystart")
    parser.add_argument("--installer", required=True, type=Path, help="Chemin de l'installeur .exe")
    parser.add_argument("--wait-pid", type=int, default=0, help="PID de Pystart a attendre")
    parser.add_argument("--relaunch", type=Path, default=None, help="Executable a relancer apres")
    args = parser.parse_args(argv)
    return run_update(args.installer, args.wait_pid, args.relaunch)


if __name__ == "__main__":
    raise SystemExit(main())
