"""Execution *synchrone* d'un script Python dans un processus separe.

Utilise par le verificateur d'exercices (qui tourne dans un thread de
travail). Pour l'execution *interactive* depuis l'interface, voir
`process_runner.py` qui s'appuie sur QProcess.

Concept Python illustre : `subprocess`. Ce module lance un autre programme
(ici un nouvel interpreteur Python) et permet de recuperer sa sortie
standard, sa sortie d'erreur et son code de retour.
"""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.core.python_env import find_python

# Longueur maximale de sortie capturee (protege l'interface d'un programme
# qui ecrirait des gigaoctets dans la console).
MAX_OUTPUT_CHARS = 200_000


class NoPythonError(RuntimeError):
    """Aucun interpreteur Python 3 utilisable n'a ete trouve sur le systeme."""


@dataclass
class ExecutionResult:
    """Resultat de l'execution d'un script."""

    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    duration_seconds: float

    @property
    def ok(self) -> bool:
        """True si le programme s'est termine normalement (code 0, sans timeout)."""
        return self.exit_code == 0 and not self.timed_out


def _python_executable() -> str:
    """Interpreteur a utiliser pour executer le code utilisateur.

    Delegue a `app.core.python_env.find_python` (venv utilisateur, interpreteur
    courant depuis les sources, ou Python du systeme si l'app est installee).
    Leve `NoPythonError` si rien n'est disponible.
    """
    python = find_python()
    if not python:
        raise NoPythonError(
            "Aucun interpreteur Python 3 n'a ete trouve. Installe Python depuis "
            "https://www.python.org/downloads/ puis relance Pystart."
        )
    return python


def run_script(
    source_code: str,
    *,
    stdin_text: str = "",
    timeout_seconds: float = 8.0,
    working_dir: Path | None = None,
    extra_files: dict[str, str] | None = None,
) -> ExecutionResult:
    """Ecrit `source_code` dans un fichier temporaire et l'execute.

    Parametres
    ----------
    source_code    : le code Python a executer.
    stdin_text     : texte fourni sur l'entree standard (pour input()).
    timeout_seconds: delai au-dela duquel le processus est tue.
    working_dir    : dossier de travail (par defaut : un dossier temporaire).
    extra_files    : fichiers annexes {nom: contenu} ecrits a cote du script
                     (par exemple un fichier de test).
    """
    import time

    created_temp = working_dir is None
    work = Path(working_dir) if working_dir else Path(tempfile.mkdtemp(prefix="pystart_"))
    work.mkdir(parents=True, exist_ok=True)

    script_path = work / "main.py"
    script_path.write_text(source_code, encoding="utf-8")

    for name, content in (extra_files or {}).items():
        (work / name).write_text(content, encoding="utf-8")

    # `-I` : mode isole. Ignore les variables d'environnement PYTHON*, le
    # dossier courant dans sys.path et le site des utilisateurs. C'est une
    # premiere barriere (pas une sandbox).
    try:
        command = [_python_executable(), "-I", str(script_path)]
    except NoPythonError as error:
        if created_temp:
            _safe_rmtree(work)
        return ExecutionResult(
            stdout="",
            stderr=f"[Pystart] {error}",
            exit_code=-1,
            timed_out=False,
            duration_seconds=0.0,
        )

    start = time.perf_counter()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            input=stdin_text,
            capture_output=True,
            text=True,
            cwd=str(work),
            timeout=timeout_seconds,
            check=False,
        )
        stdout, stderr, exit_code = completed.stdout, completed.stderr, completed.returncode
    except subprocess.TimeoutExpired as expired:
        timed_out = True
        stdout = expired.stdout or ""
        stderr = (expired.stderr or "") + (
            f"\n[Pystart] Programme interrompu : delai de {timeout_seconds:g}s depasse."
        )
        exit_code = -1
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", "replace")
    finally:
        duration = time.perf_counter() - start
        if created_temp:
            _safe_rmtree(work)

    return ExecutionResult(
        stdout=stdout[:MAX_OUTPUT_CHARS],
        stderr=stderr[:MAX_OUTPUT_CHARS],
        exit_code=exit_code,
        timed_out=timed_out,
        duration_seconds=duration,
    )


def _safe_rmtree(path: Path) -> None:
    import shutil

    try:
        shutil.rmtree(path, ignore_errors=True)
    except OSError:
        pass
