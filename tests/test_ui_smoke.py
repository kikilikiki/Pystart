"""Smoke test de l'interface : la fenetre principale se construit et charge les cours.

On force le backend Qt "offscreen" (aucun ecran requis). La verification
d'exercice passe par un thread ; elle est testee separement dans
test_validator.py, on ne la rejoue pas ici.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")


@pytest.fixture
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


def test_main_window_builds_and_lists_courses(qapp):
    from app.core.config import AppConfig
    from app.progress.store import ProgressStore
    from app.ui.main_window import MainWindow

    store = ProgressStore()
    window = MainWindow(AppConfig(), store)
    try:
        assert window._tree.topLevelItemCount() >= 16
        first_course = window._tree.topLevelItem(0)
        assert first_course.childCount() >= 1  # au moins une lecon ou un exercice
        assert "Progression globale" in window.statusBar().currentMessage()
    finally:
        store.close()


def test_about_and_settings_dialogs_build(qapp):
    from app.core.config import AppConfig
    from app.progress.store import ProgressStore
    from app.ui.about_dialog import AboutDialog
    from app.ui.settings_dialog import SettingsDialog

    AboutDialog()
    store = ProgressStore()
    try:
        SettingsDialog(AppConfig(), store)
    finally:
        store.close()
