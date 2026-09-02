"""Modeles de donnees pour les exercices.

Concept Python illustre : les `dataclass`. Un decorateur `@dataclass`
genere automatiquement `__init__`, `__repr__`, `__eq__`... a partir des
attributs annotes. C'est parfait pour representer des donnees simples.

Concept Python illustre : les `Enum`. Une enumeration donne un nom lisible
a un ensemble fini de valeurs (ici les 6 types d'exercices).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExerciseType(str, Enum):
    """Les six familles d'exercices supportees par Pystart."""

    WRITE = "write"          # Type 1 : ecrire un programme a partir de rien
    MODIFY = "modify"        # Type 2 : modifier un programme existant
    COMPLETE = "complete"    # Type 3 : completer un programme a trous
    FIX = "fix"              # Type 4 : corriger un programme qui contient un bug
    PREDICT = "predict"      # Type 5 : predire la sortie (quiz, sans execution)
    PROJECT = "project"      # Type 6 : projet plus libre

    @classmethod
    def from_text(cls, value: str) -> ExerciseType:
        try:
            return cls(value.strip().lower())
        except ValueError as error:
            raise ValueError(
                f"Type d'exercice inconnu : {value!r}. "
                f"Valeurs valides : {[t.value for t in cls]}"
            ) from error


# --- Verifications automatiques -------------------------------------------

# Types de verification reconnus par le validateur (voir validator.py).
CHECK_KINDS = {
    "stdout_equals",       # la sortie doit etre exactement egale a `value`
    "stdout_contains",     # la sortie doit contenir `value`
    "stdout_not_contains", # la sortie ne doit PAS contenir `value`
    "stdout_matches",      # la sortie doit correspondre a l'expression reguliere `value`
    "no_error",            # le programme ne doit pas planter (code de sortie 0)
    "source_contains",     # le code source doit contenir `value`
    "source_not_contains", # le code source ne doit PAS contenir `value`
    "choice_equals",       # (type PREDICT) l'option choisie doit valoir `value`
}


@dataclass
class Check:
    """Une verification unitaire appliquee au programme de l'utilisateur."""

    kind: str
    value: str = ""
    # Message pedagogique affiche quand la verification echoue.
    message: str = ""
    # Message affiche quand elle reussit (optionnel).
    success_message: str = ""

    def __post_init__(self) -> None:
        if self.kind not in CHECK_KINDS:
            raise ValueError(
                f"Verification inconnue : {self.kind!r}. "
                f"Valeurs valides : {sorted(CHECK_KINDS)}"
            )


@dataclass
class Exercise:
    """Represente un exercice complet.

    Contient tout ce qu'il faut pour :
    - afficher la consigne et le code de depart ;
    - donner des indices progressifs ;
    - lancer la verification automatique ;
    - reveler la solution en dernier recours.
    """

    id: str
    course_id: str
    type: ExerciseType
    title: str
    instructions: str
    starter_code: str = ""
    hints: list[str] = field(default_factory=list)
    solution: str = ""
    checks: list[Check] = field(default_factory=list)
    # Entree standard fournie au programme (pour les exercices utilisant input()).
    stdin: str = ""
    # Delai maximum d'execution en secondes.
    timeout_seconds: float = 8.0
    # Pour les exercices de type PREDICT : les options proposees.
    choices: list[str] = field(default_factory=list)
    # Ordre d'affichage dans la liste des exercices du cours.
    order: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any], course_id: str) -> Exercise:
        """Construit un Exercise a partir du contenu d'un fichier JSON.

        On valide au passage : un fichier de cours importe ne doit jamais
        etre accepte aveuglement (voir Docs/exercises.md).
        """
        missing = [key for key in ("id", "type", "title", "instructions") if key not in data]
        if missing:
            raise ValueError(f"Exercice incomplet, champs manquants : {missing}")

        checks = [
            Check(
                kind=str(raw["kind"]),
                value=str(raw.get("value", "")),
                message=str(raw.get("message", "")),
                success_message=str(raw.get("success_message", "")),
            )
            for raw in data.get("checks", [])
        ]

        return cls(
            id=str(data["id"]),
            course_id=course_id,
            type=ExerciseType.from_text(str(data["type"])),
            title=str(data["title"]),
            instructions=str(data["instructions"]),
            starter_code=str(data.get("starter_code", "")),
            hints=[str(h) for h in data.get("hints", [])],
            solution=str(data.get("solution", "")),
            checks=checks,
            stdin=str(data.get("stdin", "")),
            timeout_seconds=float(data.get("timeout_seconds", 8.0)),
            choices=[str(c) for c in data.get("choices", [])],
            order=int(data.get("order", 0)),
        )
