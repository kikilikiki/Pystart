"""Modeles de donnees pour les cours et les lecons."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.exercises.models import Exercise


@dataclass
class Lesson:
    """Une lecon = un bloc de contenu pedagogique en Markdown.

    Le parcours type est : explication -> exemple -> exercice. Le Markdown
    de la lecon porte l'explication et l'exemple ; les exercices sont des
    objets separes (voir `Course.exercises`).
    """

    id: str
    title: str
    markdown: str
    order: int = 0


@dataclass
class Course:
    """Un cours regroupe des lecons et des exercices autour d'un theme."""

    id: str
    title: str
    description: str
    level: str = "debutant"
    order: int = 0
    objectives: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    lessons: list[Lesson] = field(default_factory=list)
    exercises: list[Exercise] = field(default_factory=list)
    # D'ou vient le cours : "bundled" (livre) ou "user" (cree/importe).
    source: str = "bundled"
    # Dossier d'origine sur le disque (utile pour les assets).
    directory: Path | None = None

    @property
    def exercise_count(self) -> int:
        return len(self.exercises)

    def exercise_by_id(self, exercise_id: str) -> Exercise | None:
        for exercise in self.exercises:
            if exercise.id == exercise_id:
                return exercise
        return None

    @classmethod
    def meta_from_dict(cls, data: dict[str, Any], course_id: str) -> Course:
        """Cree un cours SANS lecons ni exercices (charges ensuite par le loader)."""
        return cls(
            id=course_id,
            title=str(data.get("title", course_id)),
            description=str(data.get("description", "")),
            level=str(data.get("level", "debutant")),
            order=int(data.get("order", 0)),
            objectives=[str(o) for o in data.get("objectives", [])],
            prerequisites=[str(p) for p in data.get("prerequisites", [])],
        )
