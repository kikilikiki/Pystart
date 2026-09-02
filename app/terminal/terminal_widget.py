"""Widget "Terminal / Sortie".

Ce n'est pas un vrai shell : c'est une zone de texte qui affiche ce que le
programme de l'utilisateur ecrit (stdout + stderr), plus une ligne de saisie
pour repondre a `input()` pendant l'execution.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QFont, QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class TerminalWidget(QWidget):
    """Zone de sortie + champ d'entree standard."""

    input_submitted = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._output = QPlainTextEdit(self)
        self._output.setReadOnly(True)
        self._output.setMaximumBlockCount(5000)  # borne memoire
        font = QFont("Consolas")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(11)
        self._output.setFont(font)

        self._input = QLineEdit(self)
        self._input.setPlaceholderText("Reponse a input()... (Entree pour envoyer)")
        self._input.returnPressed.connect(self._submit_input)
        self._send_button = QPushButton("Envoyer", self)
        self._send_button.clicked.connect(self._submit_input)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.addWidget(self._input)
        input_row.addWidget(self._send_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self._output)
        layout.addLayout(input_row)

        self.set_input_enabled(False)

    # --- Sortie ------------------------------------------------------
    def append_text(self, text: str, *, error: bool = False) -> None:
        cursor = self._output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        char_format = cursor.charFormat()
        char_format.setForeground(QColor("#e06c75") if error else QColor("#d7dae0"))
        cursor.setCharFormat(char_format)
        cursor.insertText(text)
        self._output.setTextCursor(cursor)
        self._output.ensureCursorVisible()

    def append_system(self, text: str) -> None:
        self.append_text(f"{text}\n")

    def clear(self) -> None:
        self._output.clear()

    # --- Entree ----------------------------------------------------
    def set_input_enabled(self, enabled: bool) -> None:
        self._input.setEnabled(enabled)
        self._send_button.setEnabled(enabled)

    def _submit_input(self) -> None:
        text = self._input.text()
        self._input.clear()
        self.append_text(text + "\n")
        self.input_submitted.emit(text)
