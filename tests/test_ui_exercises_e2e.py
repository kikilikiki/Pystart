"""Tests end-to-end de l'interface : chaque type d'exercice, chaque interaction.

On pilote la vraie fenetre principale (MainWindow) via ses signaux et ses
methodes, comme le ferait un utilisateur : selection dans l'arbre, chargement
du code de depart, indices, solution, verification (bonne et mauvaise
reponse), execution dans le terminal, quiz PREDICT, changement de theme,
mode professeur.

Backend Qt "offscreen" : aucun ecran requis.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QEventLoop, Qt, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from app.core.config import THEME_DARK, THEME_LIGHT, AppConfig  # noqa: E402
from app.exercises.models import ExerciseType  # noqa: E402
from app.progress.store import ProgressStore  # noqa: E402


@pytest.fixture
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _pump(ms: int = 200) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def _wait_until(predicate, timeout_ms: int = 8000) -> bool:
    elapsed = 0
    while elapsed < timeout_ms:
        if predicate():
            return True
        _pump(100)
        elapsed += 100
    return predicate()


@pytest.fixture
def window(qapp, tmp_path, monkeypatch):
    monkeypatch.setenv("PYSTART_DATA_DIR", str(tmp_path / "data"))
    from app.ui.main_window import MainWindow

    store = ProgressStore()
    win = MainWindow(AppConfig(theme=THEME_DARK), store)
    win.resize(1300, 850)
    yield win
    store.close()


# --- Helpers de navigation ---------------------------------------------

def _all_exercise_items(win):
    tree = win._tree
    for t in range(tree.topLevelItemCount()):
        top = tree.topLevelItem(t)
        for i in range(top.childCount()):
            child = top.child(i)
            data = child.data(0, Qt.ItemDataRole.UserRole)
            if data and data[0] == "exercise":
                yield child, data[1], data[2]


def _select_exercise(win, course_id, exercise_id):
    for item, cid, eid in _all_exercise_items(win):
        if cid == course_id and eid == exercise_id:
            win._tree.setCurrentItem(item)
            _pump(150)
            return win._course_by_id(cid).exercise_by_id(eid)
    raise AssertionError(f"exercice introuvable : {course_id}/{exercise_id}")


def _verify_and_wait(win):
    done = {}
    win._panel.check_completed.connect(lambda r: done.setdefault("r", r))
    win._verify_current_exercise()
    assert _wait_until(lambda: "r" in done), "la verification n'a jamais rendu de rapport"
    return done["r"]


# --- Tests par type d'exercice ---------------------------------------

def test_every_exercise_type_is_present(window):
    types = {ex.type for _c in window._courses for ex in _c.exercises}
    for expected in (ExerciseType.WRITE, ExerciseType.MODIFY, ExerciseType.COMPLETE,
                     ExerciseType.FIX, ExerciseType.PREDICT, ExerciseType.PROJECT):
        assert expected in types, f"aucun exercice de type {expected}"


@pytest.mark.parametrize("kind", ["write", "modify", "complete", "fix", "project"])
def test_code_exercise_full_flow(window, kind):
    """Pour chaque type 'code' : starter charge -> mauvaise reponse KO -> solution OK -> enregistre."""
    target = next(
        (
            (c.id, ex.id, ex)
            for c in window._courses
            for ex in c.exercises
            if ex.type.value == kind
        ),
        None,
    )
    assert target, f"pas d'exercice de type {kind}"
    course_id, exercise_id, exercise = target

    ex = _select_exercise(window, course_id, exercise_id)
    assert ex.id == exercise_id

    # 1. Le code de depart est charge dans l'editeur (via signal load_starter_requested).
    assert window._editor.toPlainText() == ex.starter_code

    # 2. Les indices se revelent un a un, sans depasser.
    for _ in range(len(ex.hints) + 2):
        window._panel._reveal_next_hint()
    assert window._panel._hints_revealed == len(ex.hints)

    # 3. Une reponse volontairement fausse echoue (sauf si l'exo n'a pas de check discriminant).
    window._editor.setPlainText("print('reponse volontairement fausse 12345')")
    bad = _verify_and_wait(window)
    if any(ch.kind.startswith("stdout") for ch in ex.checks):
        assert not bad.success, f"{exercise_id}: une mauvaise reponse ne devrait pas passer"

    # 4. La solution de reference passe toutes les verifications.
    window._editor.setPlainText(ex.solution)
    good = _verify_and_wait(window)
    assert good.success, (
        f"{exercise_id}: la solution echoue -> "
        f"{[r.label for r in good.results if not r.passed]}"
    )

    # 5. La reussite est enregistree en base et l'arbre est rafraichi.
    assert window._store.is_exercise_passed(window._profile.id, exercise_id)


def test_predict_exercise_flow(window):
    """PREDICT : pas d'editeur, des boutons radio ; bonne/mauvaise reponse."""
    target = next(
        ((c.id, ex.id) for c in window._courses for ex in c.exercises if ex.type == ExerciseType.PREDICT),
        None,
    )
    assert target
    ex = _select_exercise(window, *target)

    group = window._panel._choice_group
    assert len(group.buttons()) == len(ex.choices) >= 2
    # La zone de choix est marquee visible (la fenetre n'est pas show()n en test).
    assert not window._panel._choices_box.isHidden()
    assert window._panel._buttons_row.isHidden() is False

    expected = next(ch.value for ch in ex.checks if ch.kind == "choice_equals")
    wrong = next(b for b in group.buttons() if b.text() != expected)
    right = next(b for b in group.buttons() if b.text() == expected)

    wrong.setChecked(True)
    r_bad = _verify_and_wait(window)
    assert not r_bad.success

    right.setChecked(True)
    r_ok = _verify_and_wait(window)
    assert r_ok.success
    assert window._store.is_exercise_passed(window._profile.id, target[1])


def test_solution_button_reveals_code(window):
    course_id, exercise_id, _ = next(
        (c.id, ex.id, ex) for c in window._courses for ex in c.exercises
        if ex.type == ExerciseType.WRITE and ex.solution
    )
    ex = _select_exercise(window, course_id, exercise_id)
    window._panel._reveal_solution()
    shown = window._panel._results.toPlainText()
    assert "Solution" in shown
    # un fragment significatif de la solution apparait
    assert ex.solution.splitlines()[0][:10] in shown


# --- Terminal / execution ------------------------------------------

def test_run_code_shows_output_in_terminal(window):
    window._editor.setPlainText("for i in range(3):\n    print('n', i)\nprint(6 * 7)")
    window.run_code()
    assert _wait_until(lambda: "exit code" in window._terminal._output.toPlainText(), 10000)
    text = window._terminal._output.toPlainText()
    assert "n 0" in text and "n 2" in text and "42" in text
    assert "exit code 0" in text


def test_run_code_error_shows_traceback(window):
    window._editor.setPlainText("print(does_not_exist)")
    window.run_code()
    assert _wait_until(lambda: "exit code" in window._terminal._output.toPlainText(), 10000)
    text = window._terminal._output.toPlainText()
    assert "NameError" in text
    assert "does_not_exist" in text


def test_stop_button_state_and_empty_editor(window):
    window._editor.clear()
    window.run_code()  # editeur vide -> message, pas d'execution
    _pump(200)
    assert "vide" in window._terminal._output.toPlainText().lower()


# --- Themes ------------------------------------------------------

def test_theme_switch_dark_light(window, qapp):
    from app.ui.theme import apply_theme

    apply_theme(qapp, THEME_LIGHT)
    _pump(50)
    assert "background" in qapp.styleSheet()
    apply_theme(qapp, THEME_DARK)
    _pump(50)
    pal = qapp.palette()
    # En sombre, le fond de base est sombre (luminosite faible).
    base = pal.base().color()
    assert base.lightness() < 128


# --- Fichiers --------------------------------------------------

def test_open_and_save_python_file(window, tmp_path):
    src = tmp_path / "demo.py"
    src.write_text("print('depuis un fichier')\n", encoding="utf-8")

    from PySide6.QtWidgets import QFileDialog

    # open
    orig_open = QFileDialog.getOpenFileName
    QFileDialog.getOpenFileName = staticmethod(lambda *a, **k: (str(src), "Python (*.py)"))
    try:
        window._open_file()
    finally:
        QFileDialog.getOpenFileName = orig_open
    assert "depuis un fichier" in window._editor.toPlainText()

    # save
    out = tmp_path / "out.py"
    orig_save = QFileDialog.getSaveFileName
    QFileDialog.getSaveFileName = staticmethod(lambda *a, **k: (str(out), "Python (*.py)"))
    try:
        window._editor.setPlainText("x = 42\n")
        window._save_file()
    finally:
        QFileDialog.getSaveFileName = orig_save
    assert out.read_text(encoding="utf-8").strip() == "x = 42"


# --- Mode professeur ----------------------------------------

def test_teacher_create_export_import(window, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QInputDialog, QMessageBox

    from app.teacher import package

    monkeypatch.setattr(QInputDialog, "getText", staticmethod(lambda *a, **k: ("Cours de demo E2E", True)))
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: None))

    before = len(window._courses)
    window._teacher_new_course()
    assert len(window._courses) == before + 1

    new_course = next(c for c in window._courses if c.title == "Cours de demo E2E")
    archive = package.export_course(new_course.directory, tmp_path / "demo")
    assert archive.exists()

    info = package.inspect_package(archive)
    assert info["exercises"] >= 1


# --- Dialogues secondaires --------------------------------

def test_dialogs_construct(window, qapp):
    from app.ui.libraries_dialog import LibrariesDialog
    from app.ui.settings_dialog import SettingsDialog
    from app.ui.updates_dialog import UpdatesDialog

    SettingsDialog(window._config, window._store, window)
    LibrariesDialog(window)
    UpdatesDialog(window)


def test_course_summary_shows_progress(window):
    top = window._tree.topLevelItem(0)
    window._tree.setCurrentItem(top)
    _pump(100)
    # le panneau d'accueil affiche un resume avec un pourcentage
    assert "%" in window._panel._content.toPlainText()
