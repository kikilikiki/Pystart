"""Tests du chargement des cours livres avec l'application."""

from app.core import paths
from app.courses.loader import load_all_courses, load_course_from_dir
from app.exercises.models import ExerciseType


def test_bundled_courses_load():
    courses = load_all_courses()
    assert len(courses) >= 16
    ids = [c.id for c in courses]
    assert "01_hello_world" in ids
    # Les cours sont tries par `order`.
    orders = [c.order for c in courses]
    assert orders == sorted(orders)


def test_hello_world_has_lesson_and_exercise():
    course = load_course_from_dir(paths.default_courses_dir() / "01_hello_world")
    assert course.title.startswith("01")
    assert course.lessons, "le cours doit avoir au moins une lecon"
    assert course.exercises, "le cours doit avoir au moins un exercice"
    first = course.exercises[0]
    assert first.type == ExerciseType.WRITE
    assert first.checks


def test_all_exercises_have_valid_structure():
    for course in load_all_courses():
        for exercise in course.exercises:
            assert exercise.id
            assert exercise.instructions
            assert isinstance(exercise.type, ExerciseType)
            if exercise.type == ExerciseType.PREDICT:
                assert exercise.choices
                assert any(c.kind == "choice_equals" for c in exercise.checks)
