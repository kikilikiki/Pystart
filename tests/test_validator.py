"""Tests du verificateur d'exercices + verification des solutions de reference."""

import pytest

from app.core import paths
from app.courses.loader import load_course_from_dir
from app.exercises.models import Check, Exercise, ExerciseType
from app.exercises.validator import validate, validate_prediction


def _bundled_courses():
    out = []
    for child in sorted(paths.default_courses_dir().iterdir()):
        if (child / "course.json").is_file():
            out.append(load_course_from_dir(child))
    return out


_BUNDLED = _bundled_courses()


def _exercise(**kwargs) -> Exercise:
    base = dict(
        id="t.ex",
        course_id="t",
        type=ExerciseType.WRITE,
        title="Test",
        instructions="...",
    )
    base.update(kwargs)
    return Exercise(**base)


def test_stdout_equals_pass_and_fail():
    ex = _exercise(checks=[Check("stdout_equals", "42")])
    assert validate(ex, "print(42)").success
    assert not validate(ex, "print(41)").success


def test_no_error_check():
    ex = _exercise(checks=[Check("no_error")])
    assert validate(ex, "x = 1").success
    assert not validate(ex, "boom").success


def test_source_contains_check():
    ex = _exercise(checks=[Check("source_contains", "for ")])
    assert validate(ex, "for i in range(3):\n    print(i)").success
    assert not validate(ex, "print(0)\nprint(1)\nprint(2)").success


def test_empty_editor_is_rejected():
    ex = _exercise(checks=[Check("no_error")])
    assert not validate(ex, "   ").success


def test_prediction_check():
    ex = _exercise(type=ExerciseType.PREDICT, choices=["A", "B"], checks=[Check("choice_equals", "B")])
    assert validate_prediction(ex, "B").success
    assert not validate_prediction(ex, "A").success


@pytest.mark.parametrize("course_id,exercise_id", [
    (c.id, e.id) for c in _BUNDLED for e in c.exercises
])
def test_reference_solution_passes(course_id, exercise_id):
    course = next(c for c in _BUNDLED if c.id == course_id)
    exercise = course.exercise_by_id(exercise_id)
    if exercise.type == ExerciseType.PREDICT:
        expected = next(c.value for c in exercise.checks if c.kind == "choice_equals")
        report = validate_prediction(exercise, expected)
    else:
        report = validate(exercise, exercise.solution)
    assert report.success, [r.label for r in report.results if not r.passed]
