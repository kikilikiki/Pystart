"""Execution *interactive* d'un script, pilotee par l'interface.

Concept Qt illustre : `QProcess`. C'est l'equivalent Qt de `subprocess`,
mais integre a la boucle d'evenements : on recoit des signaux quand le
processus ecrit sur stdout/stderr ou se termine, sans bloquer l'interface.

Le runner :
  - ecrit le code dans `workspace/main.py` ;
  - lance `python -I main.py` dans un processus separe ;
  - transmet stdout / stderr ligne par ligne via des signaux ;
  - applique un timeout ;
  - peut etre arrete par l'utilisateur (bouton Stop).
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

from app.core import paths
from app.execution.runner import NoPythonError, _python_executable

MAX_OUTPUT_CHARS = 200_000


class ProcessRunner(QObject):
    """Lance et supervise un unique processus Python a la fois."""

    output_received = Signal(str)   # texte (stdout ou stderr melanges, comme un terminal)
    started = Signal()
    finished = Signal(int, bool)    # (code de sortie, timed_out)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._process: QProcess | None = None
        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._on_timeout)
        self._timed_out = False
        self._output_budget = MAX_OUTPUT_CHARS

    # --- API publique -------------------------------------------------
    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.state() != QProcess.ProcessState.NotRunning

    def run(self, source_code: str, *, timeout_seconds: float = 15.0, stdin_text: str = "") -> None:
        if self.is_running:
            self.stop()

        script_path = paths.workspace_dir() / "main.py"
        script_path.write_text(source_code, encoding="utf-8")

        self._timed_out = False
        self._output_budget = MAX_OUTPUT_CHARS

        process = QProcess(self)
        process.setWorkingDirectory(str(paths.workspace_dir()))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        process.readyReadStandardOutput.connect(self._on_ready_read)
        process.finished.connect(self._on_finished)
        process.errorOccurred.connect(self._on_error)

        try:
            python = _python_executable()
        except NoPythonError as error:
            self._process = None
            self.output_received.emit(f"[Pystart] {error}\n")
            self.finished.emit(-1, False)
            return

        self._process = process
        process.start(python, ["-I", "-u", str(script_path)])
        if stdin_text:
            process.write(stdin_text.encode("utf-8"))
        process.closeWriteChannel()

        if timeout_seconds > 0:
            self._timeout_timer.start(int(timeout_seconds * 1000))
        self.started.emit()

    def stop(self) -> None:
        self._timeout_timer.stop()
        if self._process and self.is_running:
            self._process.kill()
            self._process.waitForFinished(2000)

    def send_input(self, text: str) -> None:
        """Envoie du texte sur l'entree standard d'un programme en cours."""
        if self._process and self.is_running:
            self._process.write((text + "\n").encode("utf-8"))

    # --- Slots internes ---------------------------------------------
    def _on_ready_read(self) -> None:
        if not self._process:
            return
        raw = bytes(self._process.readAllStandardOutput()).decode("utf-8", "replace")
        if self._output_budget <= 0:
            return
        if len(raw) > self._output_budget:
            raw = raw[: self._output_budget] + "\n[Pystart] Sortie trop longue, coupee.\n"
        self._output_budget -= len(raw)
        self.output_received.emit(raw)

    def _on_timeout(self) -> None:
        self._timed_out = True
        self.output_received.emit(
            "\n[Pystart] Delai depasse : le programme a ete arrete.\n"
        )
        self.stop()

    def _on_error(self, error: QProcess.ProcessError) -> None:
        if error == QProcess.ProcessError.FailedToStart:
            self.output_received.emit(
                "\n[Pystart] Impossible de lancer l'interpreteur Python.\n"
            )

    def _on_finished(self, exit_code: int, _status) -> None:
        self._timeout_timer.stop()
        self.finished.emit(exit_code, self._timed_out)
        self._process = None
