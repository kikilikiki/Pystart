"""Panneau central : affiche une lecon OU un exercice.

Pour une lecon : on montre le Markdown (explication + exemple).
Pour un exercice : on montre la consigne, des boutons d'indices progressifs,
un bouton "Voir la solution" (jamais automatique) et la zone de resultats de
la verification. Les exercices de type PREDICT proposent des choix au lieu de
l'editeur.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from app.courses.models import Lesson
from app.exercises.models import Exercise, ExerciseType
from app.exercises.validator import ValidationReport, validate, validate_prediction


class ValidationWorker(QObject):
    """Execute la verification dans un thread pour ne pas geler l'interface."""

    done = Signal(object)  # ValidationReport

    def __init__(self, exercise: Exercise, source: str) -> None:
        super().__init__()
        self._exercise = exercise
        self._source = source

    def run(self) -> None:
        self.done.emit(validate(self._exercise, self._source))


class ExercisePanel(QWidget):
    """Widget affichant le contenu pedagogique et les controles d'exercice."""

    check_requested = Signal()          # l'utilisateur veut verifier son code
    load_starter_requested = Signal(str)  # charger un code de depart dans l'editeur
    hint_used = Signal()                # un indice a ete revele (pour les stats)
    check_completed = Signal(object)    # ValidationReport, apres verification

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._exercise: Exercise | None = None
        self._hints_revealed = 0
        self._thread: QThread | None = None

        self._title = QLabel("Bienvenue dans Pystart")
        self._title.setStyleSheet("font-size: 18px; font-weight: 700;")
        self._title.setWordWrap(True)

        self._content = QTextBrowser(self)
        self._content.setOpenExternalLinks(True)

        # Zone specifique aux exercices PREDICT.
        self._choices_box = QWidget(self)
        self._choices_layout = QVBoxLayout(self._choices_box)
        self._choice_group = QButtonGroup(self)
        self._choices_box.setVisible(False)

        # Barre de boutons d'exercice.
        self._buttons_row = QWidget(self)
        row = QHBoxLayout(self._buttons_row)
        row.setContentsMargins(0, 0, 0, 0)
        self._hint_button = QPushButton("Indice")
        self._hint_button.clicked.connect(self._reveal_next_hint)
        self._solution_button = QPushButton("Voir la solution")
        self._solution_button.clicked.connect(self._reveal_solution)
        self._check_button = QPushButton("Verifier")
        self._check_button.setObjectName("primary")
        self._check_button.clicked.connect(self._on_check_clicked)
        row.addWidget(self._hint_button)
        row.addWidget(self._solution_button)
        row.addStretch(1)
        row.addWidget(self._check_button)
        self._buttons_row.setVisible(False)

        self._results = QTextBrowser(self)
        self._results.setVisible(False)
        self._results.setMaximumHeight(220)

        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._content, stretch=1)
        layout.addWidget(self._choices_box)
        layout.addWidget(self._buttons_row)
        layout.addWidget(self._results)

    # --- Affichage -------------------------------------------------
    def show_welcome(self, markdown: str) -> None:
        self._exercise = None
        self._title.setText("Bienvenue dans Pystart")
        self._content.setMarkdown(markdown)
        self._buttons_row.setVisible(False)
        self._choices_box.setVisible(False)
        self._results.setVisible(False)

    def show_lesson(self, lesson: Lesson) -> None:
        self._exercise = None
        self._title.setText(lesson.title)
        self._content.setMarkdown(lesson.markdown)
        self._buttons_row.setVisible(False)
        self._choices_box.setVisible(False)
        self._results.setVisible(False)

    def show_exercise(self, exercise: Exercise) -> None:
        self._exercise = exercise
        self._hints_revealed = 0
        self._title.setText(f"Exercice — {exercise.title}")

        body = [f"**Type :** {exercise.type.value}", "", exercise.instructions]
        if exercise.type in (ExerciseType.MODIFY, ExerciseType.COMPLETE, ExerciseType.FIX):
            body += ["", "```python", exercise.starter_code, "```"]
        self._content.setMarkdown("\n".join(body))

        self._results.setVisible(False)
        self._results.clear()

        is_predict = exercise.type == ExerciseType.PREDICT
        self._setup_choices(exercise if is_predict else None)
        self._buttons_row.setVisible(True)
        self._hint_button.setVisible(bool(exercise.hints))
        self._hint_button.setText(f"Indice (0/{len(exercise.hints)})")
        self._solution_button.setVisible(bool(exercise.solution) and not is_predict)

        if not is_predict:
            self.load_starter_requested.emit(exercise.starter_code)

    def _setup_choices(self, exercise: Exercise | None) -> None:
        for button in list(self._choice_group.buttons()):
            self._choice_group.removeButton(button)
            button.deleteLater()
        while self._choices_layout.count():
            item = self._choices_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if exercise is None:
            self._choices_box.setVisible(False)
            return

        self._choices_layout.addWidget(QLabel("Choisis la sortie que produira ce programme :"))
        for choice in exercise.choices:
            radio = QRadioButton(choice)
            self._choice_group.addButton(radio)
            self._choices_layout.addWidget(radio)
        self._choices_box.setVisible(True)

    # --- Indices / solution ---------------------------------------
    def _reveal_next_hint(self) -> None:
        if not self._exercise or self._hints_revealed >= len(self._exercise.hints):
            return
        hint = self._exercise.hints[self._hints_revealed]
        self._hints_revealed += 1
        self._hint_button.setText(f"Indice ({self._hints_revealed}/{len(self._exercise.hints)})")
        self._append_result(f"💡 **Indice {self._hints_revealed} :** {hint}")
        self.hint_used.emit()
        if self._hints_revealed >= len(self._exercise.hints):
            self._hint_button.setEnabled(False)

    def _reveal_solution(self) -> None:
        if not self._exercise:
            return
        self._append_result(
            "✅ **Solution proposee :**\n\n```python\n" + self._exercise.solution + "\n```"
        )

    # --- Verification --------------------------------------------
    def _on_check_clicked(self) -> None:
        if self._exercise and self._exercise.type == ExerciseType.PREDICT:
            self._check_prediction()
        else:
            self.check_requested.emit()

    def _check_prediction(self) -> None:
        checked = self._choice_group.checkedButton()
        if not checked:
            self._append_result("Choisis une reponse avant de verifier.")
            return
        report = validate_prediction(self._exercise, checked.text())
        self.render_report(report)

    def run_check_with_source(self, source: str) -> None:
        """Lance la verification du code fourni (appelee par la fenetre principale)."""
        if not self._exercise:
            return
        self._check_button.setEnabled(False)
        self._append_result("⏳ Verification en cours...")

        worker = ValidationWorker(self._exercise, source)
        thread = QThread(self)
        worker.moveToThread(thread)
        worker.setParent(self)
        thread.started.connect(worker.run)
        worker.done.connect(self._on_check_done)
        worker.done.connect(thread.quit)
        self._thread = thread
        thread.start()

    def _on_check_done(self, report: ValidationReport) -> None:
        self._check_button.setEnabled(True)
        self.render_report(report)

    def render_report(self, report: ValidationReport) -> None:
        lines: list[str] = []
        if report.total_count:
            lines.append(f"### Resultat : {report.passed_count}/{report.total_count} verifications")
        for result in report.results:
            mark = "✓" if result.passed else "✗"
            lines.append(f"- {mark} {result.label}")
            if result.detail and not result.passed:
                lines.append(f"  ```\n  {result.detail}\n  ```")

        if report.friendly_error:
            lines += [
                "",
                f"❌ {report.friendly_error.summary}",
                f"💡 {report.friendly_error.hint}",
                "",
                "<details><summary>Traceback complet</summary>",
                "```\n" + report.friendly_error.raw_traceback + "\n```",
                "</details>",
            ]

        if report.success:
            lines.append("\n🎉 **Bravo, l'exercice est reussi !**")

        self._results.setVisible(True)
        self._results.setMarkdown("\n".join(lines))
        self.last_report = report
        self.check_completed.emit(report)

    # --- Utilitaires --------------------------------------------
    def _append_result(self, markdown_text: str) -> None:
        self._results.setVisible(True)
        existing = self._results.toMarkdown().strip()
        combined = (existing + "\n\n" + markdown_text) if existing else markdown_text
        self._results.setMarkdown(combined)

    @property
    def current_exercise(self) -> Exercise | None:
        return self._exercise
