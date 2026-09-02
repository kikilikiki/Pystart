"""Fenetre principale de Pystart.

Disposition (voir Docs/architecture.md) :

    +--------------------------------------------------------------+
    | Menu : Fichier  Executer  Professeur  Aide      [Parametres] |
    +-------------+------------------------------+-----------------+
    | Cours       | Lecon / Exercice             | Editeur Python  |
    | (arbre)     | (Markdown + indices + tests) | (+ Executer)    |
    +-------------+------------------------------+-----------------+
    | Terminal / Sortie                                           |
    +--------------------------------------------------------------+
    | Barre d'etat : progression globale                          |
    +--------------------------------------------------------------+
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app import GITHUB_URL, __version__
from app.core.config import AppConfig
from app.courses.loader import load_all_courses
from app.courses.models import Course
from app.editor.code_editor import CodeEditor
from app.editor.highlighter import PythonHighlighter
from app.execution.process_runner import ProcessRunner
from app.progress.store import ProgressStore
from app.terminal.terminal_widget import TerminalWidget
from app.ui.about_dialog import AboutDialog
from app.ui.exercise_panel import ExercisePanel
from app.ui.settings_dialog import SettingsDialog
from app.ui.theme import apply_theme
from app.ui.updates_dialog import UpdatesDialog

_WELCOME = """
# Bienvenue dans Pystart 👋

Pystart t'apprend **Python en pratiquant**. A gauche, choisis un cours.
Chaque cours suit le meme parcours :

**Explication → Exemple → Petit exercice → Indice → Correction → Exercice plus difficile → Mini-projet.**

1. Lis la lecon dans ce panneau.
2. Ecris ton code dans l'editeur, a droite.
3. Clique sur **Executer** pour voir le resultat dans le terminal, en bas.
4. Pour un exercice, clique sur **Verifier** : Pystart teste ton programme.

Commence par le cours **01 — Hello World**.
"""


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig, store: ProgressStore) -> None:
        super().__init__()
        self._config = config
        self._store = store
        self._profile = self._resolve_profile()
        self._courses: list[Course] = []
        self._runner = ProcessRunner(self)
        # Brouillons de code, un par exercice (voir _load_starter_code).
        self._drafts: dict[str, str] = self._load_drafts()
        self._active_draft_id: str | None = None

        self.setWindowTitle(f"Pystart {__version__}")
        self.resize(1280, 820)

        self._build_ui()
        self._build_menu()
        self._connect_runner()
        self.reload_courses()
        self._apply_editor_font()
        self._update_progress_label()

    # --- Construction de l'interface --------------------------------
    def _build_ui(self) -> None:
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setMinimumWidth(220)
        self._tree.currentItemChanged.connect(self._on_tree_selection)

        self._panel = ExercisePanel()
        self._panel.check_requested.connect(self._verify_current_exercise)
        self._panel.load_starter_requested.connect(self._load_starter_code)
        self._panel.hint_used.connect(self._on_hint_used)
        self._panel.check_completed.connect(self._record_last_result)

        self._editor = CodeEditor()
        self._highlighter = PythonHighlighter(self._editor.document())

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        button_row = QWidget()
        row_layout = QVBoxLayout(button_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        from PySide6.QtWidgets import QHBoxLayout

        buttons = QHBoxLayout()
        self._run_button = QPushButton("▶ Executer")
        self._run_button.setObjectName("primary")
        self._run_button.clicked.connect(self.run_code)
        self._stop_button = QPushButton("■ Stop")
        self._stop_button.setObjectName("danger")
        self._stop_button.clicked.connect(self._runner.stop)
        self._stop_button.setEnabled(False)
        self._verify_button = QPushButton("✓ Verifier l'exercice")
        self._verify_button.clicked.connect(self._verify_current_exercise)
        buttons.addWidget(self._run_button)
        buttons.addWidget(self._stop_button)
        buttons.addStretch(1)
        buttons.addWidget(self._verify_button)
        row_layout.addLayout(buttons)

        editor_layout.addWidget(button_row)
        editor_layout.addWidget(self._editor, stretch=1)

        self._terminal = TerminalWidget()
        self._terminal.input_submitted.connect(self._runner.send_input)

        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        top_splitter.addWidget(self._tree)
        top_splitter.addWidget(self._panel)
        top_splitter.addWidget(editor_container)
        top_splitter.setStretchFactor(0, 0)
        top_splitter.setStretchFactor(1, 3)
        top_splitter.setStretchFactor(2, 3)
        top_splitter.setSizes([240, 480, 520])

        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(self._terminal)
        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([600, 200])

        self.setCentralWidget(main_splitter)
        self._panel.show_welcome(_WELCOME)

        self._progress_label = self.statusBar()
        self._update_progress_label()

    def _build_menu(self) -> None:
        menu = self.menuBar()

        file_menu = menu.addMenu("&Fichier")
        self._add_action(file_menu, "Nouveau fichier", "Ctrl+N", self._new_file)
        self._add_action(file_menu, "Ouvrir un fichier .py...", "Ctrl+O", self._open_file)
        self._add_action(file_menu, "Enregistrer sous...", "Ctrl+S", self._save_file)
        file_menu.addSeparator()
        self._add_action(file_menu, "Quitter", "Ctrl+Q", self.close)

        run_menu = menu.addMenu("&Executer")
        self._add_action(run_menu, "Lancer le programme", "F5", self.run_code)
        self._add_action(run_menu, "Arreter", "Shift+F5", self._runner.stop)
        self._add_action(run_menu, "Verifier l'exercice", "Ctrl+Return", self._verify_current_exercise)
        run_menu.addSeparator()
        self._add_action(run_menu, "Recharger le code de depart", None, self._reload_starter_code)
        self._add_action(run_menu, "Effacer le terminal", None, self._terminal.clear)

        teacher_menu = menu.addMenu("&Professeur")
        self._add_action(teacher_menu, "Nouveau cours...", None, self._teacher_new_course)
        self._add_action(teacher_menu, "Importer un cours (.pystart)...", None, self._teacher_import)
        self._add_action(teacher_menu, "Exporter un cours...", None, self._teacher_export)
        teacher_menu.addSeparator()
        self._add_action(teacher_menu, "Ouvrir le dossier des cours", None, self._open_courses_folder)

        help_menu = menu.addMenu("&Aide")
        self._add_action(help_menu, "Parametres...", "Ctrl+,", self._open_settings)
        self._add_action(help_menu, "Mises a jour...", None, lambda: UpdatesDialog(self).exec())
        self._add_action(help_menu, "Depot GitHub", None, self._open_github)
        help_menu.addSeparator()
        self._add_action(help_menu, "A propos de Pystart", None, lambda: AboutDialog(self).exec())

    def _add_action(self, menu, text: str, shortcut: str | None, slot) -> QAction:
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    # --- Chargement des cours -------------------------------------
    def reload_courses(self) -> None:
        self._courses = load_all_courses()
        self._tree.clear()
        for course in self._courses:
            course_item = QTreeWidgetItem([course.title])
            course_item.setData(0, Qt.ItemDataRole.UserRole, ("course", course.id, None))
            for lesson in course.lessons:
                lesson_item = QTreeWidgetItem([f"  📖 {lesson.title}"])
                lesson_item.setData(0, Qt.ItemDataRole.UserRole, ("lesson", course.id, lesson.id))
                course_item.addChild(lesson_item)
            passed = self._store.passed_exercise_ids(self._profile.id)
            for exercise in course.exercises:
                mark = "✓" if exercise.id in passed else "•"
                ex_item = QTreeWidgetItem([f"  {mark} {exercise.title}"])
                ex_item.setData(0, Qt.ItemDataRole.UserRole, ("exercise", course.id, exercise.id))
                course_item.addChild(ex_item)
            self._tree.addTopLevelItem(course_item)
            course_item.setExpanded(True)

    def reload_theme(self) -> None:
        from PySide6.QtWidgets import QApplication

        apply_theme(QApplication.instance(), self._config.theme)
        self._apply_editor_font()

    def _apply_editor_font(self) -> None:
        self._editor.set_font_point_size(self._config.font_size)

    # --- Navigation dans l'arbre --------------------------------
    def _course_by_id(self, course_id: str) -> Course | None:
        return next((c for c in self._courses if c.id == course_id), None)

    def _on_tree_selection(self, current: QTreeWidgetItem | None, _previous) -> None:
        if current is None:
            return
        data = current.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        kind, course_id, item_id = data
        course = self._course_by_id(course_id)
        if course is None:
            return

        # On quitte peut-etre un exercice : sauvegarde son brouillon.
        if kind != "exercise":
            self._save_active_draft()
            self._active_draft_id = None

        if kind == "course":
            summary = self._course_summary(course)
            self._panel.show_welcome(summary)
        elif kind == "lesson":
            lesson = next((les for les in course.lessons if les.id == item_id), None)
            if lesson:
                self._panel.show_lesson(lesson)
        elif kind == "exercise":
            exercise = course.exercise_by_id(item_id)
            if exercise:
                self._store.mark_exercise_seen(self._profile.id, exercise.id, course.id)
                self._panel.show_exercise(exercise)
                self._config.last_course_id = course.id
                self._config.last_exercise_id = exercise.id
                self._config.save()

    def _course_summary(self, course: Course) -> str:
        stats = self._store.course_stats(self._profile.id, course.id, course.exercise_count)
        lines = [
            f"# {course.title}",
            "",
            course.description,
            "",
            f"**Niveau :** {course.level}  •  **Progression :** {stats.percent}% "
            f"({stats.exercises_done}/{stats.total_exercises} exercices)",
        ]
        if course.objectives:
            lines += ["", "## Objectifs", *[f"- {o}" for o in course.objectives]]
        if course.prerequisites:
            lines += ["", "## Prerequis", *[f"- {p}" for p in course.prerequisites]]
        lines += ["", "Choisis une lecon ou un exercice dans la liste de gauche."]
        return "\n".join(lines)

    # --- Editeur / brouillons par exercice ----------------------
    #
    # Chaque exercice garde son propre "brouillon" : le code que l'utilisateur
    # a ecrit. Quand on change d'exercice, on sauvegarde le brouillon courant
    # et on recharge celui de l'exercice choisi (ou son code de depart la
    # premiere fois). Les brouillons sont aussi ecrits sur disque
    # (drafts.json) pour survivre a une fermeture de l'application.

    def _save_active_draft(self) -> None:
        if self._active_draft_id is not None:
            self._drafts[self._active_draft_id] = self._editor.toPlainText()
            self._persist_drafts()

    def _load_starter_code(self, code: str) -> None:
        exercise = self._panel.current_exercise
        if exercise is None:
            return
        if self._active_draft_id and self._active_draft_id != exercise.id:
            self._drafts[self._active_draft_id] = self._editor.toPlainText()
        self._active_draft_id = exercise.id
        self._editor.setPlainText(self._drafts.get(exercise.id, code))
        self._persist_drafts()

    def _reload_starter_code(self) -> None:
        """Menu : revenir au code de depart de l'exercice courant."""
        exercise = self._panel.current_exercise
        if exercise is None:
            self._editor.clear()
            return
        answer = QMessageBox.question(
            self,
            "Recharger le code de depart",
            "Remplacer ton code par le code de depart d'origine de l'exercice ?",
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._editor.setPlainText(exercise.starter_code)

    def _drafts_path(self):
        from app.core import paths

        return paths.app_data_dir() / "drafts.json"

    def _load_drafts(self) -> dict[str, str]:
        import json

        path = self._drafts_path()
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _persist_drafts(self) -> None:
        import json

        try:
            self._drafts_path().write_text(
                json.dumps(self._drafts, ensure_ascii=False, indent=1), encoding="utf-8"
            )
        except OSError:
            pass

    def _new_file(self) -> None:
        self._editor.clear()

    def _open_file(self) -> None:
        path_text, _ = QFileDialog.getOpenFileName(self, "Ouvrir", "", "Python (*.py)")
        if path_text:
            self._editor.setPlainText(Path(path_text).read_text(encoding="utf-8"))

    def _save_file(self) -> None:
        path_text, _ = QFileDialog.getSaveFileName(self, "Enregistrer", "main.py", "Python (*.py)")
        if path_text:
            Path(path_text).write_text(self._editor.toPlainText(), encoding="utf-8")

    def run_code(self) -> None:
        source = self._editor.toPlainText()
        if not source.strip():
            self._terminal.append_system("[Pystart] L'editeur est vide.")
            return
        self._terminal.clear()
        self._terminal.append_system("$ python main.py")
        self._runner.run(source, timeout_seconds=20.0)

    def _connect_runner(self) -> None:
        self._runner.started.connect(self._on_run_started)
        self._runner.output_received.connect(lambda text: self._terminal.append_text(text))
        self._runner.finished.connect(self._on_run_finished)

    def _on_run_started(self) -> None:
        self._run_button.setEnabled(False)
        self._stop_button.setEnabled(True)
        self._terminal.set_input_enabled(True)

    def _on_run_finished(self, exit_code: int, timed_out: bool) -> None:
        self._run_button.setEnabled(True)
        self._stop_button.setEnabled(False)
        self._terminal.set_input_enabled(False)
        if timed_out:
            self._terminal.append_system("\n[Pystart] Programme interrompu (delai depasse).")
        else:
            self._terminal.append_system(f"\nProcess finished with exit code {exit_code}")

    # --- Verification d'exercice -------------------------------
    def _verify_current_exercise(self) -> None:
        exercise = self._panel.current_exercise
        if exercise is None:
            QMessageBox.information(self, "Pystart", "Selectionne un exercice a gauche d'abord.")
            return
        # `verify()` aiguille : quiz PREDICT (choix radio) ou verification du code.
        self._panel.verify(self._editor.toPlainText())

    def _record_last_result(self, report) -> None:
        """Appele (signal check_completed) quand une verification se termine."""
        exercise = self._panel.current_exercise
        if report is None or exercise is None:
            return
        self._store.record_attempt(
            self._profile.id, exercise.id, exercise.course_id, passed=report.success
        )
        self.reload_courses()
        self._update_progress_label()

    def _on_hint_used(self) -> None:
        exercise = self._panel.current_exercise
        if exercise:
            self._store.record_hint_used(self._profile.id, exercise.id, exercise.course_id)

    # --- Professeur -------------------------------------------
    def _teacher_new_course(self) -> None:
        from app.teacher.authoring import create_empty_course

        title, ok = QInputDialog.getText(self, "Nouveau cours", "Titre du cours :")
        if not ok or not title.strip():
            return
        directory = create_empty_course(title.strip())
        QMessageBox.information(
            self,
            "Cours cree",
            f"Cours cree dans :\n{directory}\n\n"
            "Ajoute des fichiers Markdown dans lessons/ et des JSON dans exercises/.",
        )
        self.reload_courses()

    def _teacher_import(self) -> None:
        from app.teacher import package

        path_text, _ = QFileDialog.getOpenFileName(
            self, "Importer un cours", "", "Cours Pystart (*.pystart *.zip)"
        )
        if not path_text:
            return
        try:
            preview = package.inspect_package(Path(path_text))
        except package.PackageError as error:
            QMessageBox.critical(self, "Import impossible", str(error))
            return
        answer = QMessageBox.question(
            self,
            "Importer ce cours ?",
            f"Titre : {preview['title']}\n"
            f"Niveau : {preview['level']}\n"
            f"Lecons : {preview['lessons']}  •  Exercices : {preview['exercises']}\n\n"
            "Importer ce cours ?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            package.import_package(Path(path_text), overwrite=False)
        except package.PackageError as error:
            QMessageBox.critical(self, "Import impossible", str(error))
            return
        self.reload_courses()

    def _teacher_export(self) -> None:
        from app.teacher import package

        item = self._tree.currentItem()
        course_id = None
        if item and item.data(0, Qt.ItemDataRole.UserRole):
            course_id = item.data(0, Qt.ItemDataRole.UserRole)[1]
        course = self._course_by_id(course_id) if course_id else None
        if course is None or course.directory is None:
            QMessageBox.information(self, "Export", "Selectionne d'abord un cours a gauche.")
            return
        path_text, _ = QFileDialog.getSaveFileName(
            self, "Exporter", f"{course.id}.pystart", "Cours Pystart (*.pystart)"
        )
        if not path_text:
            return
        result = package.export_course(course.directory, Path(path_text))
        QMessageBox.information(self, "Export termine", f"Cours exporte :\n{result}")

    def _open_courses_folder(self) -> None:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        from app.core import paths

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(paths.user_courses_dir())))

    # --- Divers ---------------------------------------------
    def _open_settings(self) -> None:
        dialog = SettingsDialog(self._config, self._store, self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()

    def _on_settings_changed(self) -> None:
        self._profile = self._resolve_profile()
        self.reload_theme()
        self.reload_courses()
        self._update_progress_label()

    def _open_github(self) -> None:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        QDesktopServices.openUrl(QUrl(GITHUB_URL))

    def _resolve_profile(self):
        if self._config.active_profile_id is not None:
            try:
                return self._store.get_profile(self._config.active_profile_id)
            except KeyError:
                pass
        profile = self._store.ensure_default_profile()
        self._config.active_profile_id = profile.id
        self._config.save()
        return profile

    def _total_exercises(self) -> int:
        return sum(c.exercise_count for c in self._courses)

    def _update_progress_label(self) -> None:
        total = self._total_exercises()
        percent = self._store.overall_progress(self._profile.id, total)
        done = len(self._store.passed_exercise_ids(self._profile.id))
        self.statusBar().showMessage(
            f"Profil : {self._profile.name}  •  Progression globale : {percent}% "
            f"({done}/{total} exercices reussis)"
        )

    def closeEvent(self, event) -> None:  # noqa: N802
        self._runner.stop()
        self._save_active_draft()
        self._config.save()
        super().closeEvent(event)
