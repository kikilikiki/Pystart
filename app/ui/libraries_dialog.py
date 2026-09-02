"""Fenetre "Bibliotheques" : installer des paquets Python (pygame, etc.).

L'installation se fait dans l'environnement virtuel dedie a l'utilisateur,
dans un thread pour ne pas bloquer l'interface.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.libraries import installer, venv


class _InstallWorker(QObject):
    line = Signal(str)
    finished = Signal()

    def __init__(self, requirement: str) -> None:
        super().__init__()
        self._requirement = requirement

    def run(self) -> None:
        try:
            for text in installer.install(self._requirement):
                self.line.emit(text)
        except installer.InvalidPackageName as error:
            self.line.emit(f"[ERREUR] {error}\n")
        self.finished.emit()


class LibrariesDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Bibliotheques Python")
        self.setMinimumSize(560, 440)
        self._thread: QThread | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Installe des bibliotheques externes pour tes projets.\n"
                "Elles sont isolees dans un environnement dedie, sans risque pour Pystart."
            )
        )

        row = QHBoxLayout()
        self._field = QLineEdit(self)
        self._field.setPlaceholderText("Exemple : pygame  ou  requests==2.31.0")
        self._field.returnPressed.connect(self._install)
        self._install_button = QPushButton("Installer")
        self._install_button.setObjectName("primary")
        self._install_button.clicked.connect(self._install)
        row.addWidget(self._field)
        row.addWidget(self._install_button)
        layout.addLayout(row)

        layout.addWidget(QLabel("Deja installe :"))
        self._installed = QListWidget(self)
        layout.addWidget(self._installed)

        self._log = QPlainTextEdit(self)
        self._log.setReadOnly(True)
        layout.addWidget(self._log)

        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self._refresh_installed()

    def _refresh_installed(self) -> None:
        self._installed.clear()
        if not venv.venv_exists():
            self._installed.addItem("(environnement non encore cree)")
            return
        for name, version in venv.list_installed():
            self._installed.addItem(f"{name}  {version}")

    def _install(self) -> None:
        requirement = self._field.text().strip()
        if not requirement:
            return
        self._install_button.setEnabled(False)
        self._log.appendPlainText(f"Installation de {requirement}...")

        worker = _InstallWorker(requirement)
        thread = QThread(self)
        worker.moveToThread(thread)
        worker.setParent(self)
        thread.started.connect(worker.run)
        worker.line.connect(lambda text: self._log.appendPlainText(text.rstrip("\n")))
        worker.finished.connect(thread.quit)
        worker.finished.connect(self._on_finished)
        self._thread = thread
        thread.start()

    def _on_finished(self) -> None:
        self._install_button.setEnabled(True)
        self._refresh_installed()
