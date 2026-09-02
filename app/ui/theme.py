"""Themes clair et sombre.

Deux mecanismes Qt sont combines :

1. `QPalette` : les *roles* de couleur (fond de fenetre, fond des zones de
   saisie, texte, selection...). C'est ce que respectent les widgets riches
   comme `QTextBrowser` quand ils affichent du Markdown. Une simple feuille de
   style ne suffit pas pour eux : il faut la palette.

2. `QSS` (feuille de style, facon CSS) : les details visuels (coins arrondis,
   boutons colores, marges).

Le choix clair/sombre est sauvegarde dans la config (`AppConfig.theme`).
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QPalette

from app.core.config import THEME_DARK, THEME_LIGHT


@dataclass(frozen=True)
class Palette:
    window: str
    base: str          # fond des editeurs / listes / navigateurs
    text: str
    dim_text: str
    border: str
    accent: str
    accent_text: str = "#ffffff"


DARK = Palette(
    window="#1e2127",
    base="#23262d",
    text="#d7dae0",
    dim_text="#8b929e",
    border="#3a3f4b",
    accent="#2f6feb",
)

LIGHT = Palette(
    window="#f5f6f8",
    base="#ffffff",
    text="#1c1e21",
    dim_text="#6b7280",
    border="#d0d3d9",
    accent="#2f6feb",
)


def _qpalette(colors: Palette) -> QPalette:
    qp = QPalette()
    window = QColor(colors.window)
    base = QColor(colors.base)
    text = QColor(colors.text)
    accent = QColor(colors.accent)

    qp.setColor(QPalette.ColorRole.Window, window)
    qp.setColor(QPalette.ColorRole.WindowText, text)
    qp.setColor(QPalette.ColorRole.Base, base)
    qp.setColor(QPalette.ColorRole.AlternateBase, window)
    qp.setColor(QPalette.ColorRole.Text, text)
    qp.setColor(QPalette.ColorRole.ToolTipBase, base)
    qp.setColor(QPalette.ColorRole.ToolTipText, text)
    qp.setColor(QPalette.ColorRole.Button, window)
    qp.setColor(QPalette.ColorRole.ButtonText, text)
    qp.setColor(QPalette.ColorRole.BrightText, QColor("#ff5555"))
    qp.setColor(QPalette.ColorRole.Highlight, accent)
    qp.setColor(QPalette.ColorRole.HighlightedText, QColor(colors.accent_text))
    qp.setColor(QPalette.ColorRole.PlaceholderText, QColor(colors.dim_text))
    qp.setColor(QPalette.ColorRole.Link, accent)

    disabled = QColor(colors.dim_text)
    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
    ):
        qp.setColor(QPalette.ColorGroup.Disabled, role, disabled)
    return qp


_QSS_TEMPLATE = """
* {{ font-family: "Segoe UI", "Noto Sans", sans-serif; }}
QMainWindow::separator {{ width: 3px; height: 3px; background: {border}; }}
QSplitter::handle {{ background: {border}; }}

QPushButton {{
    padding: 6px 14px;
    border-radius: 6px;
    border: 1px solid {border};
    background: {base};
    color: {text};
}}
QPushButton:hover {{ border-color: {accent}; }}
QPushButton:disabled {{ color: {dim_text}; border-color: {border}; }}
QPushButton#primary {{ background: {accent}; color: {accent_text}; border: none; font-weight: 600; }}
QPushButton#primary:hover {{ background: {accent}; }}
QPushButton#primary:disabled {{ background: {border}; color: {dim_text}; }}
QPushButton#danger {{ background: #d9534f; color: white; border: none; }}

QListWidget, QTreeWidget, QPlainTextEdit, QTextEdit, QTextBrowser, QLineEdit, QSpinBox, QComboBox {{
    border: 1px solid {border};
    border-radius: 6px;
    background: {base};
    color: {text};
}}
QTreeWidget::item, QListWidget::item {{ padding: 2px 0; }}
QMenuBar {{ background: {window}; color: {text}; }}
QMenuBar::item:selected {{ background: {accent}; color: {accent_text}; }}
QMenu {{ background: {base}; color: {text}; border: 1px solid {border}; }}
QMenu::item:selected {{ background: {accent}; color: {accent_text}; }}
QStatusBar {{ background: {window}; color: {dim_text}; }}
QScrollBar:vertical {{ background: {window}; width: 12px; }}
QScrollBar::handle:vertical {{ background: {border}; border-radius: 5px; min-height: 24px; }}
QScrollBar:horizontal {{ background: {window}; height: 12px; }}
QScrollBar::handle:horizontal {{ background: {border}; border-radius: 5px; min-width: 24px; }}
QToolTip {{ background: {base}; color: {text}; border: 1px solid {border}; }}
"""


def _colors_for(theme: str) -> Palette:
    return DARK if theme == THEME_DARK else LIGHT


def stylesheet_for(theme: str) -> str:
    c = _colors_for(theme)
    return _QSS_TEMPLATE.format(
        window=c.window, base=c.base, text=c.text, dim_text=c.dim_text,
        border=c.border, accent=c.accent, accent_text=c.accent_text,
    )


def apply_theme(app, theme: str) -> None:
    """Applique le theme (palette + feuille de style) a toute l'application."""
    if theme not in (THEME_DARK, THEME_LIGHT):
        theme = THEME_DARK
    app.setPalette(_qpalette(_colors_for(theme)))
    app.setStyleSheet(stylesheet_for(theme))
