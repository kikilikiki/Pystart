"""Coloration syntaxique Python.

Concept Qt illustre : `QSyntaxHighlighter`. Qt appelle `highlightBlock()`
pour chaque ligne de texte. On y applique des formats (couleur, gras...) sur
des portions de la ligne reperees par des expressions regulieres.

On reste volontairement simple : mots-cles, chaines, nombres, commentaires,
noms de fonctions/classes et fonctions integrees. Pas d'analyse complete.
"""

from __future__ import annotations

import builtins
import keyword
import re

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


def _fmt(color: str, *, bold: bool = False, italic: bool = False) -> QTextCharFormat:
    text_format = QTextCharFormat()
    text_format.setForeground(QColor(color))
    if bold:
        text_format.setFontWeight(QFont.Weight.Bold)
    if italic:
        text_format.setFontItalic(True)
    return text_format


# Palette inspiree des themes "One Dark". Lisible en clair comme en sombre.
PALETTE = {
    "keyword": _fmt("#c678dd", bold=True),
    "builtin": _fmt("#56b6c2"),
    "string": _fmt("#98c379"),
    "number": _fmt("#d19a66"),
    "comment": _fmt("#7f848e", italic=True),
    "definition": _fmt("#61afef", bold=True),
    "decorator": _fmt("#e5c07b"),
    "self": _fmt("#e06c75", italic=True),
}


class PythonHighlighter(QSyntaxHighlighter):
    """Applique des couleurs au code Python d'un `QTextDocument`."""

    def __init__(self, document) -> None:
        super().__init__(document)
        self._rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self._build_rules()
        # Etat multi-lignes pour les chaines triples \"\"\" ... \"\"\".
        self._triple_single = QRegularExpression(r"'''")
        self._triple_double = QRegularExpression(r'"""')

    def _build_rules(self) -> None:
        for word in keyword.kwlist:
            self._rules.append(
                (QRegularExpression(rf"\b{word}\b"), PALETTE["keyword"])
            )
        builtin_names = [name for name in dir(builtins) if not name.startswith("_")]
        self._rules.append(
            (QRegularExpression(rf"\b({'|'.join(map(re.escape, builtin_names))})\b"), PALETTE["builtin"])
        )
        self._rules.append((QRegularExpression(r"\bself\b"), PALETTE["self"]))
        self._rules.append(
            (QRegularExpression(r"\b[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?\b"), PALETTE["number"])
        )
        # def <nom>  /  class <nom>
        self._rules.append(
            (QRegularExpression(r"(?<=\bdef\s)[A-Za-z_][A-Za-z0-9_]*"), PALETTE["definition"])
        )
        self._rules.append(
            (QRegularExpression(r"(?<=\bclass\s)[A-Za-z_][A-Za-z0-9_]*"), PALETTE["definition"])
        )
        self._rules.append((QRegularExpression(r"^\s*@[A-Za-z_][\w.]*"), PALETTE["decorator"]))
        # Chaines simples et doubles (non triples).
        self._rules.append((QRegularExpression(r"'[^'\\\n]*(\\.[^'\\\n]*)*'"), PALETTE["string"]))
        self._rules.append((QRegularExpression(r'"[^"\\\n]*(\\.[^"\\\n]*)*"'), PALETTE["string"]))
        # Commentaires (en dernier pour recouvrir le reste).
        self._rules.append((QRegularExpression(r"#[^\n]*"), PALETTE["comment"]))

    def highlightBlock(self, text: str) -> None:  # noqa: N802 (methode Qt)
        for pattern, text_format in self._rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), text_format)

        self._highlight_triple_strings(text)

    def _highlight_triple_strings(self, text: str) -> None:
        """Gere les chaines sur plusieurs lignes via l'etat de bloc."""
        self.setCurrentBlockState(0)
        for state, delimiter in ((1, self._triple_single), (2, self._triple_double)):
            start = 0
            if self.previousBlockState() != state:
                match = delimiter.match(text)
                start = match.capturedStart() if match.hasMatch() else -1
            while start >= 0:
                match = delimiter.match(text, start + 3)
                if match.hasMatch():
                    length = match.capturedEnd() - start
                    self.setCurrentBlockState(0)
                else:
                    self.setCurrentBlockState(state)
                    length = len(text) - start
                self.setFormat(start, length, PALETTE["string"])
                next_match = delimiter.match(text, start + length)
                start = next_match.capturedStart() if next_match.hasMatch() else -1
