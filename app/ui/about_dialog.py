"""Fenetre "A propos" : presentation de Pystart et coordonnees de contact.

Accessible depuis le menu Aide et depuis les Parametres. Design volontairement
simple : les informations de contact sont accessibles mais pas envahissantes.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app import (
    AUTHOR,
    CONTACT_DISCORD_INVITE,
    CONTACT_DISCORD_PSEUDO,
    CONTACT_EMAIL,
    GITHUB_URL,
    __version__,
)


def _open(url: str) -> None:
    QDesktopServices.openUrl(QUrl(url))


class AboutDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("A propos de Pystart")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("Pystart")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(title)

        pitch = QLabel(
            "Une application gratuite pour apprendre Python en pratiquant "
            "directement dans un environnement simple et accessible."
        )
        pitch.setWordWrap(True)
        layout.addWidget(pitch)

        layout.addWidget(QLabel(f"Cree par : {AUTHOR}"))
        layout.addWidget(QLabel(f"Version : {__version__}"))

        layout.addWidget(_separator())

        # --- Discord ---
        discord_label = QLabel(f"💬 Discord\n\nPseudo : {CONTACT_DISCORD_PSEUDO}")
        layout.addWidget(discord_label)
        discord_button = QPushButton("Rejoindre le serveur Discord")
        discord_button.clicked.connect(lambda: _open(CONTACT_DISCORD_INVITE))
        layout.addWidget(discord_button)

        # --- Email ---
        layout.addWidget(QLabel(f"📧 Email\n\n{CONTACT_EMAIL}"))
        email_button = QPushButton("Contacter par email")
        email_button.clicked.connect(lambda: _open(f"mailto:{CONTACT_EMAIL}"))
        layout.addWidget(email_button)

        layout.addWidget(_separator())

        github_button = QPushButton("Voir le projet sur GitHub")
        github_button.clicked.connect(lambda: _open(GITHUB_URL))
        layout.addWidget(github_button)

        footer = QLabel("© 2026 Pystart")
        footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer.setStyleSheet("color: gray;")
        layout.addWidget(footer)

        close_row = QHBoxLayout()
        close_row.addStretch(1)
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.accept)
        close_row.addWidget(close_button)
        layout.addLayout(close_row)


def _separator() -> QLabel:
    line = QLabel()
    line.setFixedHeight(1)
    line.setStyleSheet("background-color: rgba(128,128,128,0.4);")
    return line
