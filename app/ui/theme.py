"""Themes clair et sombre, appliques via une feuille de style Qt (QSS).

QSS ressemble a du CSS. On l'applique a toute l'application avec
`QApplication.setStyleSheet(...)`. Le choix est sauvegarde dans la config.
"""

from __future__ import annotations

from app.core.config import THEME_DARK, THEME_LIGHT

_COMMON = """
* { font-family: "Segoe UI", "Noto Sans", sans-serif; }
QMainWindow::separator { width: 3px; height: 3px; }
QSplitter::handle { background: palette(mid); }
QPushButton {
    padding: 6px 14px;
    border-radius: 6px;
    border: 1px solid palette(mid);
}
QPushButton:hover { border-color: palette(highlight); }
QPushButton:disabled { color: palette(mid); }
QPushButton#primary {
    background: #2f6feb; color: white; border: none; font-weight: 600;
}
QPushButton#primary:hover { background: #4b86f0; }
QPushButton#danger { background: #d9534f; color: white; border: none; }
QListWidget, QTreeWidget { border: 1px solid palette(mid); border-radius: 6px; }
QPlainTextEdit, QTextEdit, QTextBrowser {
    border: 1px solid palette(mid); border-radius: 6px;
}
QTabBar::tab { padding: 6px 12px; }
"""

_DARK = """
QWidget { background-color: #1e2127; color: #d7dae0; }
QPlainTextEdit, QTextEdit, QTextBrowser, QLineEdit { background-color: #23262d; }
QMenuBar, QMenu { background-color: #23262d; }
QMenu::item:selected { background-color: #2f6feb; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #2f6feb; color: white; }
"""

_LIGHT = """
QWidget { background-color: #fafafa; color: #1c1e21; }
QPlainTextEdit, QTextEdit, QTextBrowser, QLineEdit { background-color: #ffffff; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #2f6feb; color: white; }
"""


def stylesheet_for(theme: str) -> str:
    palette = _DARK if theme == THEME_DARK else _LIGHT
    return _COMMON + palette


def apply_theme(app, theme: str) -> None:
    """Applique le theme demande a l'application Qt."""
    if theme not in (THEME_DARK, THEME_LIGHT):
        theme = THEME_DARK
    app.setStyleSheet(stylesheet_for(theme))
