"""Verification automatique du code de l'utilisateur.

Le validateur :
1. execute le code dans un processus separe (via `execution.runner`) ;
2. applique chaque `Check` de l'exercice ;
3. renvoie un rapport lisible ( reussi / echoue + explications).

Il ne donne JAMAIS la solution automatiquement.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.execution.runner import ExecutionResult, run_script
from app.exercises.errors import FriendlyError, explain
from app.exercises.models import Check, Exercise, ExerciseType


@dataclass
class CheckResult:
    """Resultat d'une verification unitaire."""

    passed: bool
    label: str
    detail: str = ""


@dataclass
class ValidationReport:
    """Rapport complet renvoye a l'interface."""

    success: bool
    results: list[CheckResult] = field(default_factory=list)
    execution: ExecutionResult | None = None
    friendly_error: FriendlyError | None = None

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def total_count(self) -> int:
        return len(self.results)


def _normalize(text: str) -> str:
    """Compare les sorties sans se soucier des espaces/retours en trop."""
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").strip().splitlines())


def _apply_check(check: Check, source: str, execution: ExecutionResult) -> CheckResult:
    stdout = execution.stdout
    kind = check.kind

    if kind == "no_error":
        passed = execution.ok
        detail = "" if passed else (execution.stderr.strip().splitlines() or [""])[-1]
        return CheckResult(passed, check.message or "Le programme s'execute sans erreur", detail)

    if kind == "stdout_equals":
        passed = _normalize(stdout) == _normalize(check.value)
        detail = ""
        if not passed:
            detail = f"Attendu : {check.value!r}\nObtenu  : {stdout!r}"
        return CheckResult(passed, check.message or "La sortie est correcte", detail)

    if kind == "stdout_contains":
        passed = _normalize(check.value) in _normalize(stdout)
        detail = "" if passed else f"La sortie ne contient pas : {check.value!r}"
        return CheckResult(passed, check.message or f"La sortie contient {check.value!r}", detail)

    if kind == "stdout_not_contains":
        passed = _normalize(check.value) not in _normalize(stdout)
        detail = "" if passed else f"La sortie ne devrait pas contenir : {check.value!r}"
        return CheckResult(passed, check.message or "La sortie evite le texte interdit", detail)

    if kind == "stdout_matches":
        passed = re.search(check.value, stdout, re.MULTILINE) is not None
        detail = "" if passed else f"La sortie ne correspond pas au motif : {check.value}"
        return CheckResult(passed, check.message or "La sortie a le bon format", detail)

    if kind == "source_contains":
        passed = check.value in source
        detail = "" if passed else f"Ton code devrait utiliser : {check.value!r}"
        return CheckResult(passed, check.message or f"Le code utilise {check.value!r}", detail)

    if kind == "source_not_contains":
        passed = check.value not in source
        detail = "" if passed else f"Ton code ne devrait pas utiliser : {check.value!r}"
        return CheckResult(passed, check.message or "Le code respecte la contrainte", detail)

    # kind == "choice_equals" est gere separement (exercices PREDICT).
    return CheckResult(False, f"Verification non applicable : {kind}", "")


def validate(exercise: Exercise, source_code: str) -> ValidationReport:
    """Execute le code et applique les verifications de l'exercice."""
    if not source_code.strip():
        return ValidationReport(
            success=False,
            results=[CheckResult(False, "Ton editeur est vide", "Ecris du code avant de valider.")],
        )

    execution = run_script(
        source_code,
        stdin_text=exercise.stdin,
        timeout_seconds=exercise.timeout_seconds,
    )

    results = [_apply_check(check, source_code, execution) for check in exercise.checks]

    # Si le programme a plante et qu'aucune verification "no_error" n'existe,
    # on ajoute quand meme un diagnostic clair.
    friendly = None
    if not execution.ok:
        friendly = explain(execution.stderr)

    # S'il n'y a aucune verification, on considere reussi si le code tourne.
    if not results:
        results.append(
            CheckResult(execution.ok, "Le programme s'execute", "" if execution.ok else "Erreur a l'execution")
        )

    success = all(r.passed for r in results)
    return ValidationReport(
        success=success,
        results=results,
        execution=execution,
        friendly_error=friendly,
    )


def validate_prediction(exercise: Exercise, chosen: str) -> ValidationReport:
    """Verifie la reponse d'un exercice de type PREDICT (quiz sans execution)."""
    expected = next(
        (c.value for c in exercise.checks if c.kind == "choice_equals"),
        None,
    )
    if expected is None:
        return ValidationReport(
            success=False,
            results=[CheckResult(False, "Exercice mal configure", "Aucune bonne reponse definie.")],
        )
    passed = _normalize(chosen) == _normalize(expected)
    detail = "" if passed else "Relis le programme ligne par ligne et refais le calcul."
    return ValidationReport(
        success=passed,
        results=[CheckResult(passed, "Bonne reponse" if passed else "Reponse incorrecte", detail)],
    )


__all__ = [
    "CheckResult",
    "ValidationReport",
    "validate",
    "validate_prediction",
    "ExerciseType",
]
