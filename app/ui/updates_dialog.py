"""Fenetre "Mises a jour".

Affiche la version courante, permet de verifier la derniere version publiee
sur GitHub, et lance la mise a jour en un clic (telechargement + updater).

Le travail reseau se fait dans un `QThread` pour ne pas geler l'interface.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from app import __version__
from app.updates import update_manager
from app.updates.update_manager import UpdateError, UpdateInfo


class _CheckWorker(QObject):
    done = Signal(object)     # UpdateInfo
    failed = Signal(str)

    def run(self) -> None:
        try:
            self.done.emit(update_manager.check())
        except UpdateError as error:
            self.failed.emit(str(error))


class _DownloadWorker(QObject):
    progress = Signal(int, int)
    done = Signal(str)        # chemin du fichier
    failed = Signal(str)

    def __init__(self, info: UpdateInfo) -> None:
        super().__init__()
        self._info = info

    def run(self) -> None:
        try:
            path = update_manager.download(
                self._info,
                on_progress=lambda done, total: self.progress.emit(done, total),
            )
            self.done.emit(str(path))
        except UpdateError as error:
            self.failed.emit(str(error))


class UpdatesDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Mises a jour")
        self.setMinimumWidth(460)
        self._info: UpdateInfo | None = None
        self._thread: QThread | None = None

        layout = QVBoxLayout(self)
        self._status = QLabel(f"Version actuelle : {__version__}")
        self._status.setStyleSheet("font-weight: 600;")
        layout.addWidget(self._status)

        self._notes = QTextBrowser(self)
        self._notes.setPlaceholderText("Les nouveautes de la derniere version s'afficheront ici.")
        self._notes.setVisible(False)
        layout.addWidget(self._notes)

        self._progress = QProgressBar(self)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        buttons = QHBoxLayout()
        self._check_button = QPushButton("Verifier les mises a jour")
        self._check_button.clicked.connect(self.check_for_updates)
        self._action_button = QPushButton("Mettre a jour")
        self._action_button.setObjectName("primary")
        self._action_button.setVisible(False)
        self._action_button.clicked.connect(self._start_download)
        buttons.addWidget(self._check_button)
        buttons.addWidget(self._action_button)
        buttons.addStretch(1)
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.reject)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    # --- Verification -------------------------------------------------
    def check_for_updates(self) -> None:
        self._check_button.setEnabled(False)
        self._status.setText("Verification en cours...")
        self._run_worker(_CheckWorker(), self._on_check_done, self._on_error)

    def _on_check_done(self, info: UpdateInfo) -> None:
        self._check_button.setEnabled(True)
        self._info = info
        if not info.update_available:
            self._status.setText(f"✓ Vous utilisez la derniere version ({__version__}).")
            self._notes.setVisible(False)
            self._action_button.setVisible(False)
            return

        self._status.setText(
            f"🚀 Nouvelle version disponible\n\n"
            f"Version actuelle : {info.current_version}\n"
            f"Nouvelle version : {info.latest_version}"
            + ("\n\n⚠️ Mise a jour obligatoire." if info.mandatory else "")
        )
        self._notes.setVisible(True)
        self._notes.setMarkdown(info.release_notes or "_Pas de notes de version._")
        self._action_button.setVisible(bool(info.download_url))
        if not info.download_url:
            self._status.setText(
                self._status.text()
                + "\n\n(Aucun installeur Windows attache : telechargez depuis GitHub.)"
            )

    # --- Telechargement ---------------------------------------------
    def _start_download(self) -> None:
        if not self._info:
            return
        self._action_button.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.setRange(0, 100)
        worker = _DownloadWorker(self._info)
        worker.progress.connect(self._on_progress)
        self._run_worker(worker, self._on_download_done, self._on_error)

    def _on_progress(self, done: int, total: int) -> None:
        if total:
            self._progress.setValue(int(100 * done / total))

    def _on_download_done(self, path_text: str) -> None:
        self._status.setText("Telechargement termine et verifie. Lancement de l'installation...")
        self._launch_updater(Path(path_text))

    def _launch_updater(self, installer: Path) -> None:
        """Lance l'updater separe puis ferme Pystart."""
        import subprocess

        updater = _find_updater_executable()
        current_exe = Path(sys.executable)
        args = [
            "--installer", str(installer),
            "--wait-pid", str(os.getpid()),
            "--relaunch", str(current_exe),
        ]
        try:
            if updater:
                subprocess.Popen([str(updater), *args])
            else:
                # Mode developpement : on appelle le module directement.
                subprocess.Popen([sys.executable, "-m", "app.updates.updater_cli", *args])
        except OSError as error:
            self._on_error(f"Impossible de lancer l'updater : {error}")
            return

        # On laisse une seconde a l'updater pour demarrer, puis on quitte.
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication

        QTimer.singleShot(800, QApplication.instance().quit)

    # --- Utilitaires -------------------------------------------------
    def _run_worker(self, worker: QObject, on_done, on_failed) -> None:
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        if hasattr(worker, "done"):
            worker.done.connect(on_done)
            worker.done.connect(thread.quit)
        if hasattr(worker, "failed"):
            worker.failed.connect(on_failed)
            worker.failed.connect(thread.quit)
        thread.finished.connect(lambda: setattr(self, "_thread", None))
        # On garde une reference pour eviter le ramasse-miettes.
        self._thread = thread
        worker.setParent(self)
        thread.start()

    def _on_error(self, message: str) -> None:
        self._check_button.setEnabled(True)
        self._action_button.setEnabled(True)
        self._progress.setVisible(False)
        self._status.setText(f"❌ {message}")


def _find_updater_executable() -> Path | None:
    if not getattr(sys, "frozen", False):
        return None
    candidate = Path(sys.executable).parent / (
        "PystartUpdater.exe" if sys.platform.startswith("win") else "PystartUpdater"
    )
    return candidate if candidate.exists() else None
