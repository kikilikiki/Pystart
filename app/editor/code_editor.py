"""Editeur de code : QPlainTextEdit enrichi.

Fonctionnalites :
  - numeros de lignes (widget dessine a gauche) ;
  - coloration syntaxique (via PythonHighlighter) ;
  - auto-indentation apres `:` et conservation de l'indentation ;
  - Tab / Shift+Tab pour indenter / desindenter une selection ;
  - surlignage de la ligne courante ;
  - police a chasse fixe.

Copier/coller, annuler/retablir et la recherche sont fournis par Qt
(QPlainTextEdit) ; on expose juste des raccourcis dans la fenetre principale.
"""

from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QKeyEvent,
    QPainter,
    QTextCursor,
    QTextFormat,
)
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

INDENT = "    "  # 4 espaces : la convention Python (PEP 8).


class _LineNumberArea(QWidget):
    """Petite bande a gauche de l'editeur qui affiche les numeros de lignes."""

    def __init__(self, editor: CodeEditor) -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:  # noqa: N802
        self._editor.paint_line_numbers(event)


class CodeEditor(QPlainTextEdit):
    """Editeur Python minimaliste mais confortable."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._line_numbers = _LineNumberArea(self)

        font = QFont("Consolas")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(12)
        self.setFont(font)
        self.setTabStopDistance(QFontMetrics(font).horizontalAdvance(" ") * 4)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.blockCountChanged.connect(self._update_margins)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)

        self._update_margins()
        self._highlight_current_line()

    # --- Numeros de lignes ------------------------------------------------
    def line_number_area_width(self) -> int:
        digits = max(2, len(str(self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_margins(self) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._line_numbers.scroll(0, dy)
        else:
            self._line_numbers.update(0, rect.y(), self._line_numbers.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_margins()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        contents = self.contentsRect()
        self._line_numbers.setGeometry(
            QRect(contents.left(), contents.top(), self.line_number_area_width(), contents.height())
        )

    def paint_line_numbers(self, event) -> None:
        painter = QPainter(self._line_numbers)
        painter.fillRect(event.rect(), QColor(0, 0, 0, 20))

        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        painter.setPen(QColor(120, 120, 120))
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.drawText(
                    0,
                    int(top),
                    self._line_numbers.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            number += 1

    # --- Ligne courante -------------------------------------------------
    def _highlight_current_line(self) -> None:
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor(255, 255, 255, 18))
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    # --- Indentation intelligente -------------------------------------
    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        key = event.key()
        cursor = self.textCursor()

        if key == Qt.Key.Key_Tab and not cursor.hasSelection():
            self.insertPlainText(INDENT)
            return

        if key in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab) and cursor.hasSelection():
            self._shift_selection(add=key == Qt.Key.Key_Tab)
            return

        if key == Qt.Key.Key_Backtab:
            self._shift_selection(add=False)
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._insert_newline_with_indent()
            return

        super().keyPressEvent(event)

    def _current_line_text(self) -> str:
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        return cursor.selectedText()

    def _insert_newline_with_indent(self) -> None:
        line = self._current_line_text()
        indent = line[: len(line) - len(line.lstrip())]
        if line.strip().endswith(":"):
            indent += INDENT
        self.textCursor().insertText("\n" + indent)

    def _shift_selection(self, *, add: bool) -> None:
        cursor = self.textCursor()
        start, end = sorted((cursor.selectionStart(), cursor.selectionEnd()))
        cursor.beginEditBlock()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        while cursor.position() <= end:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            if add:
                cursor.insertText(INDENT)
                end += len(INDENT)
            else:
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.KeepAnchor,
                    len(INDENT),
                )
                if cursor.selectedText() == INDENT:
                    cursor.removeSelectedText()
                    end -= len(INDENT)
                else:
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        cursor.endEditBlock()

    # --- Confort ------------------------------------------------------
    def set_font_point_size(self, size: int) -> None:
        font = self.font()
        font.setPointSize(max(8, min(28, size)))
        self.setFont(font)
        self.setTabStopDistance(QFontMetrics(font).horizontalAdvance(" ") * 4)
        self._update_margins()
