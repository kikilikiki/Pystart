"""Chargement des cours depuis le disque.

Disposition attendue d'un cours :

    <dossier_du_cours>/
        course.json          # metadonnees (titre, description, niveau...)
        lessons/
            01_intro.md      # contenu Markdown, dans l'ordre alphabetique
            02_exemple.md
        exercises/
            01_afficher.json # un exercice par fichier JSON
            02_variable.json

Le loader parcourt d'abord les cours livres avec l'application
(`content/courses/`) puis les cours de l'utilisateur. En cas d'identifiant
identique, le cours de l'utilisateur remplace celui d'origine.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.core import paths
from app.courses.models import Course, Lesson
from app.exercises.models import Exercise

logger = logging.getLogger(__name__)


class CourseLoadError(Exception):
    """Levee quand un dossier de cours est invalide."""


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CourseLoadError(f"JSON invalide dans {path.name} : {error}") from error


def _lesson_title(markdown: str, fallback: str) -> str:
    """Prend le premier titre `# ...` du Markdown, sinon le nom de fichier."""
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def _slug_to_title(filename: str) -> str:
    stem = Path(filename).stem
    # "02_les_variables" -> "Les variables"
    parts = stem.split("_")
    if parts and parts[0].isdigit():
        parts = parts[1:]
    return " ".join(parts).capitalize() or stem


def load_course_from_dir(directory: Path, source: str = "bundled") -> Course:
    """Charge un cours complet (metadonnees + lecons + exercices)."""
    course_json = directory / "course.json"
    if not course_json.is_file():
        raise CourseLoadError(f"Fichier course.json absent dans {directory}")

    course_id = directory.name
    course = Course.meta_from_dict(_read_json(course_json), course_id)
    course.source = source
    course.directory = directory

    # --- Lecons --------------------------------------------------------
    lessons_dir = directory / "lessons"
    if lessons_dir.is_dir():
        for index, md_path in enumerate(sorted(lessons_dir.glob("*.md"))):
            markdown = md_path.read_text(encoding="utf-8")
            course.lessons.append(
                Lesson(
                    id=f"{course_id}:{md_path.stem}",
                    title=_lesson_title(markdown, _slug_to_title(md_path.name)),
                    markdown=markdown,
                    order=index,
                )
            )

    # Compatibilite : un unique fichier course.md a la racine.
    single_md = directory / "course.md"
    if not course.lessons and single_md.is_file():
        markdown = single_md.read_text(encoding="utf-8")
        course.lessons.append(
            Lesson(id=f"{course_id}:course", title=course.title, markdown=markdown)
        )

    # --- Exercices ----------------------------------------------------
    exercises_dir = directory / "exercises"
    if exercises_dir.is_dir():
        for index, ex_path in enumerate(sorted(exercises_dir.glob("*.json"))):
            data = _read_json(ex_path)
            try:
                exercise = Exercise.from_dict(data, course_id)
            except ValueError as error:
                raise CourseLoadError(f"{ex_path.name} : {error}") from error
            if exercise.order == 0:
                exercise.order = index
            course.exercises.append(exercise)

    course.lessons.sort(key=lambda lesson: lesson.order)
    course.exercises.sort(key=lambda exercise: exercise.order)
    return course


def _load_courses_in(root: Path, source: str) -> list[Course]:
    if not root.is_dir():
        return []
    courses: list[Course] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "course.json").is_file():
            continue
        try:
            courses.append(load_course_from_dir(child, source=source))
        except CourseLoadError:
            logger.exception("Impossible de charger le cours %s", child)
    return courses


def load_all_courses() -> list[Course]:
    """Charge tous les cours (livres + utilisateur), tries par `order` puis titre."""
    by_id: dict[str, Course] = {}

    for course in _load_courses_in(paths.default_courses_dir(), source="bundled"):
        by_id[course.id] = course

    # Les cours de l'utilisateur peuvent completer ou remplacer.
    for course in _load_courses_in(paths.user_courses_dir(), source="user"):
        by_id[course.id] = course

    courses = list(by_id.values())
    courses.sort(key=lambda course: (course.order, course.title))
    return courses
