"""Creation et edition de cours par un professeur (cote fichiers).

Le mode professeur de la V1 reste volontairement simple : Pystart cree la
structure de dossiers et des fichiers d'exemple. Le professeur edite ensuite
les fichiers Markdown / JSON (dans l'application ou avec son editeur habituel).
Une interface d'edition plus riche est prevue pour la version 0.1.x.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.core import paths

_EXAMPLE_LESSON = """# Introduction

Explique ici la notion, avec des mots simples.

## Exemple

```python
print("Bonjour la classe")
```
"""

_EXAMPLE_EXERCISE = {
    "id": "mon_cours.premier_exercice",
    "type": "write",
    "title": "Afficher un message",
    "instructions": "Ecris un programme qui affiche `Bonjour` dans le terminal.",
    "starter_code": "",
    "hints": [
        "Utilise la fonction print().",
        "N'oublie pas les guillemets autour du texte.",
    ],
    "solution": "print(\"Bonjour\")",
    "checks": [
        {"kind": "no_error"},
        {"kind": "stdout_contains", "value": "Bonjour"},
    ],
}


def _slugify(text: str) -> str:
    keep = "".join(c if c.isalnum() or c in " -_" else "" for c in text).strip()
    return keep.lower().replace(" ", "_") or "cours"


def create_empty_course(title: str, *, level: str = "debutant") -> Path:
    """Cree un dossier de cours pret a etre edite. Renvoie ce dossier."""
    course_id = _slugify(title)
    directory = paths.user_courses_dir() / course_id
    suffix = 2
    while directory.exists():
        directory = paths.user_courses_dir() / f"{course_id}_{suffix}"
        suffix += 1

    (directory / "lessons").mkdir(parents=True)
    (directory / "exercises").mkdir(parents=True)

    course_meta = {
        "title": title,
        "description": "Decris ton cours ici.",
        "level": level,
        "order": 100,
        "objectives": [],
        "prerequisites": [],
    }
    (directory / "course.json").write_text(
        json.dumps(course_meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (directory / "lessons" / "01_introduction.md").write_text(_EXAMPLE_LESSON, encoding="utf-8")
    (directory / "exercises" / "01_premier_exercice.json").write_text(
        json.dumps(_EXAMPLE_EXERCISE, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return directory
