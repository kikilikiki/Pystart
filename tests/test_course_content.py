"""Invariants de contenu pour TOUS les cours (rapide, sans interface).

Complete test_validator.py (qui verifie deja que chaque solution de reference
passe). Ici on verifie la coherence pedagogique de chaque exercice et on
s'assure qu'une mauvaise reponse est bien rejetee.
"""

from __future__ import annotations

import pytest

from app.core import paths
from app.courses.loader import load_course_from_dir
from app.exercises.models import ExerciseType
from app.exercises.validator import validate, validate_prediction


def _bundled_courses():
    """Uniquement les cours livres avec l'application (deterministe : ignore les
    cours utilisateur qui pourraient trainer dans %APPDATA% pendant les tests)."""
    out = []
    for child in sorted(paths.default_courses_dir().iterdir()):
        if (child / "course.json").is_file():
            out.append(load_course_from_dir(child))
    return out


_COURSES = _bundled_courses()
_EXERCISES = [(c.id, ex) for c in _COURSES for ex in c.exercises]
_WRONG_CODE = 'print("XXX mauvaise reponse volontaire 99999")'


@pytest.mark.parametrize("course", _COURSES, ids=[c.id for c in _COURSES])
def test_course_has_lesson_with_content(course):
    assert course.title and course.description
    assert course.lessons, f"{course.id}: aucune lecon"
    for lesson in course.lessons:
        assert lesson.title, f"{course.id}/{lesson.id}: lecon sans titre"
        assert len(lesson.markdown.strip()) > 120, f"{course.id}/{lesson.id}: lecon trop courte"
    assert course.exercises, f"{course.id}: aucun exercice"


@pytest.mark.parametrize("course_id,ex", _EXERCISES, ids=[e.id for _c, e in _EXERCISES])
def test_exercise_is_well_formed(course_id, ex):
    assert ex.instructions.strip()
    assert ex.hints, f"{ex.id}: aucun indice"
    assert all(h.strip() for h in ex.hints), f"{ex.id}: indice vide"

    if ex.type == ExerciseType.PREDICT:
        assert len(ex.choices) >= 2, f"{ex.id}: moins de 2 choix"
        correct = [ch.value for ch in ex.checks if ch.kind == "choice_equals"]
        assert len(correct) == 1, f"{ex.id}: doit avoir exactement 1 bonne reponse"
        assert correct[0] in ex.choices, f"{ex.id}: la bonne reponse absente des choix"
        return

    assert ex.solution.strip(), f"{ex.id}: pas de solution de reference"
    if ex.type == ExerciseType.COMPLETE:
        assert "____" in ex.starter_code, f"{ex.id}: complete sans '____'"
        assert "____" not in ex.solution, f"{ex.id}: '____' dans la solution"
    if ex.type == ExerciseType.FIX:
        assert ex.starter_code.strip() != ex.solution.strip(), f"{ex.id}: fix, starter == solution"
    if ex.type in (ExerciseType.MODIFY, ExerciseType.COMPLETE, ExerciseType.FIX):
        assert ex.starter_code.strip(), f"{ex.id}: {ex.type.value} sans code de depart"


@pytest.mark.parametrize("course_id,ex", _EXERCISES, ids=[e.id for _c, e in _EXERCISES])
def test_wrong_answer_is_rejected(course_id, ex):
    """Une reponse manifestement fausse ne doit jamais passer un exercice."""
    if ex.type == ExerciseType.PREDICT:
        correct = next(ch.value for ch in ex.checks if ch.kind == "choice_equals")
        wrong = next(x for x in ex.choices if x != correct)
        assert not validate_prediction(ex, wrong).success, f"{ex.id}: mauvaise reponse acceptee"
        return

    # On ne teste que si l'exercice a des verifications discriminantes.
    if not any(ch.kind.startswith(("stdout", "source")) for ch in ex.checks):
        pytest.skip("pas de check discriminant")
    report = validate(ex, _WRONG_CODE)
    assert not report.success, f"{ex.id}: du code bidon passe les verifications"
