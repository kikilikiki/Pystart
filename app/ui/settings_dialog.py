"""Fenetre "Parametres" : theme, taille de police, profil, acces aux outils."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.core.config import THEME_DARK, THEME_LIGHT, AppConfig
from app.progress.store import ProgressStore
from app.ui.about_dialog import AboutDialog
from app.ui.libraries_dialog import LibrariesDialog
from app.ui.updates_dialog import UpdatesDialog


class SettingsDialog(QDialog):
    """Regroupe les preferences et les fenetres secondaires."""

    settings_changed = Signal()

    def __init__(self, config: AppConfig, store: ProgressStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Parametres")
        self.setMinimumWidth(420)
        self._config = config
        self._store = store

        form = QFormLayout()

        self._theme = QComboBox(self)
        self._theme.addItem("Sombre", THEME_DARK)
        self._theme.addItem("Clair", THEME_LIGHT)
        self._theme.setCurrentIndex(0 if config.theme == THEME_DARK else 1)
        form.addRow("Theme", self._theme)

        self._font_size = QSpinBox(self)
        self._font_size.setRange(9, 24)
        self._font_size.setValue(config.font_size)
        form.addRow("Taille de police (editeur)", self._font_size)

        self._profile = QComboBox(self)
        self._reload_profiles()
        form.addRow("Profil actif", self._profile)

        new_profile_button = QPushButton("Nouveau profil...")
        new_profile_button.clicked.connect(self._create_profile)
        form.addRow("", new_profile_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)

        tools = QHBoxLayout()
        for label, slot in (
            ("Mises a jour", self._open_updates),
            ("Bibliotheques", self._open_libraries),
            ("A propos", self._open_about),
        ):
            button = QPushButton(label)
            button.clicked.connect(slot)
            tools.addWidget(button)
        layout.addLayout(tools)

        actions = QHBoxLayout()
        actions.addStretch(1)
        save_button = QPushButton("Enregistrer")
        save_button.setObjectName("primary")
        save_button.clicked.connect(self._save)
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        actions.addWidget(cancel_button)
        actions.addWidget(save_button)
        layout.addLayout(actions)

    def _reload_profiles(self) -> None:
        self._profile.clear()
        for profile in self._store.list_profiles():
            self._profile.addItem(f"{profile.name} ({profile.level})", profile.id)
        if self._config.active_profile_id is not None:
            index = self._profile.findData(self._config.active_profile_id)
            if index >= 0:
                self._profile.setCurrentIndex(index)

    def _create_profile(self) -> None:
        name, ok = QInputDialog.getText(self, "Nouveau profil", "Nom du profil :")
        if not ok or not name.strip():
            return
        level, ok = QInputDialog.getItem(
            self, "Niveau", "Ton niveau :", ["debutant", "intermediaire", "avance"], 0, False
        )
        if not ok:
            return
        profile = self._store.create_profile(name.strip(), level)
        self._config.active_profile_id = profile.id
        self._reload_profiles()

    def _save(self) -> None:
        self._config.theme = self._theme.currentData()
        self._config.font_size = self._font_size.value()
        if self._profile.currentData() is not None:
            self._config.active_profile_id = int(self._profile.currentData())
        self._config.save()
        self.settings_changed.emit()
        self.accept()

    def _open_updates(self) -> None:
        UpdatesDialog(self).exec()

    def _open_libraries(self) -> None:
        LibrariesDialog(self).exec()

    def _open_about(self) -> None:
        AboutDialog(self).exec()
