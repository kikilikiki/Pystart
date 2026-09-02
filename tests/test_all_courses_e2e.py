"""Verifie que CHAQUE cours / lecon / exercice s'ouvre correctement dans l'interface.

Ce module se concentre sur la NAVIGATION et l'AFFICHAGE (rapide) :
selection dans l'arbre, rendu du panneau, chargement du code de depart,
zone de choix pour les quiz.

La verification effective des solutions (execution en sous-processus) est
couverte par :
  - tests/test_validator.py::test_reference_solution_passes  (les 27 solutions)
  - tests/test_course_content.py                             (invariants + mauvaise reponse)
  - tests/test_ui_exercises_e2e.py                           (flux complet, 1 par type)
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QEventLoop, Qt, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from app.core import paths  # noqa: E402
from app.core.config import THEME_DARK, AppConfig  # noqa: E402
from app.courses.loader import load_course_from_dir  # noqa: E402
from app.exercises.models import ExerciseType  # noqa: E402
from app.progress.store import ProgressStore  # noqa: E402


def _bundled_courses():
    courses = []
    for child in sorted(paths.default_courses_dir().iterdir()):
        if (child / "course.json").is_file():
            courses.append(load_course_from_dir(child))
    return courses


_COURSES = _bundled_courses()
_ALL_EXERCISES = [(c.id, ex.id) for c in _COURSES for ex in c.exercises]
_ALL_LESSONS = [(c.id, les.id) for c in _COURSES for les in c.lessons]


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def window(qapp, tmp_path_factory):
    os.environ["PYSTART_DATA_DIR"] = str(tmp_path_factory.mktemp("data"))
    from app.ui.main_window import MainWindow

    store = ProgressStore()
    win = MainWindow(AppConfig(theme=THEME_DARK), store)
    win.resize(1300, 850)
    yield win
    store.close()


def _pump(ms: int = 40) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def _find_item(win, kind, course_id, item_id):
    tree = win._tree
    for t in range(tree.topLevelItemCount()):
        top = tree.topLevelItem(t)
        for i in range(top.childCount()):
            child = top.child(i)
            if child.data(0, Qt.ItemDataRole.UserRole) == (kind, course_id, item_id):
                return child
    raise AssertionError(f"introuvable dans l'arbre : {(kind, course_id, item_id)}")


def test_tous_les_cours_dans_l_arbre(window):
    assert window._tree.topLevelItemCount() == len(_COURSES) >= 16
    for course in _COURSES:
        assert course.lessons and course.exercises


@pytest.mark.parametrize(
    "course_id,lesson_id", _ALL_LESSONS,
    ids=[f"{c}:{lid.split(':')[-1]}" for c, lid in _ALL_LESSONS],
)
def test_chaque_lecon_s_affiche(window, course_id, lesson_id):
    window._tree.setCurrentItem(_find_item(window, "lesson", course_id, lesson_id))
    _pump()
    assert len(window._panel._content.toPlainText().strip()) > 50
    assert window._panel._title.text()


@pytest.mark.parametrize(
    "course_id,exercise_id", _ALL_EXERCISES,
    ids=[eid for _cid, eid in _ALL_EXERCISES],
)
def test_chaque_exercice_s_ouvre(window, course_id, exercise_id):
    window._tree.setCurrentItem(_find_item(window, "exercise", course_id, exercise_id))
    _pump()

    ex = window._panel.current_exercise
    assert ex is not None and ex.id == exercise_id
    assert window._panel._content.toPlainText().strip()
    # boutons d'exercice visibles
    assert not window._panel._buttons_row.isHidden()

    if ex.type == ExerciseType.PREDICT:
        assert not window._panel._choices_box.isHidden()
        assert len(window._panel._choice_group.buttons()) == len(ex.choices) >= 2
    else:
        assert window._panel._choices_box.isHidden()
        # le code de depart est charge tel quel dans l'editeur
        assert window._editor.toPlainText() == ex.starter_code
    # l'exercice est marque "vu" en base
    assert exercise_id in _seen_ids(window)


def _seen_ids(win):
    rows = win._store._conn.execute(
        "SELECT exercise_id FROM exercise_progress WHERE profile_id = ?",
        (win._profile.id,),
    ).fetchall()
    return {r[0] for r in rows}
