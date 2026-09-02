"""Rendre les erreurs Python comprehensibles pour un debutant.

On ne cache jamais le vrai traceback (il faut apprendre a le lire), mais on
ajoute une explication en francais et un indice cible.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# (motif recherche dans stderr) -> (explication, indice)
_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(r"NameError: name '(?P<name>[^']+)' is not defined"),
        "Tu utilises un nom (`{name}`) qui n'existe pas encore.",
        "Verifie l'orthographe, ou assure-toi d'avoir cree cette variable avant de l'utiliser.",
    ),
    (
        re.compile(r"SyntaxError: (?P<msg>.+)"),
        "Python n'arrive pas a lire ton programme : il y a une erreur de syntaxe.",
        "Regarde la ligne indiquee : parentheses, guillemets ou deux-points manquants ?",
    ),
    (
        re.compile(r"IndentationError: (?P<msg>.+)"),
        "Ton code est mal aligne (probleme d'indentation).",
        "En Python, l'interieur d'un bloc (if, for, def...) doit etre decale de 4 espaces.",
    ),
    (
        re.compile(r"IndexError: (?P<msg>.+)"),
        "Tu essaies d'acceder a un element qui n'existe pas dans la liste.",
        "Rappelle-toi que les indices commencent a 0 et que le dernier vaut len(liste) - 1.",
    ),
    (
        re.compile(r"KeyError: (?P<key>.+)"),
        "Tu demandes une cle ({key}) qui n'est pas dans le dictionnaire.",
        "Verifie l'orthographe de la cle, ou utilise .get() pour une valeur par defaut.",
    ),
    (
        re.compile(r"TypeError: (?P<msg>.+)"),
        "Tu melanges des types incompatibles (par exemple un texte et un nombre).",
        "Utilise int(), str() ou float() pour convertir avant de combiner les valeurs.",
    ),
    (
        re.compile(r"ZeroDivisionError"),
        "Tu divises par zero, ce qui est impossible en mathematiques.",
        "Verifie le denominateur avant de faire la division.",
    ),
    (
        re.compile(r"ModuleNotFoundError: No module named '(?P<mod>[^']+)'"),
        "Le module `{mod}` n'est pas installe.",
        "Ouvre Parametres > Bibliotheques pour l'installer, ou verifie le nom de l'import.",
    ),
    (
        re.compile(r"ValueError: (?P<msg>.+)"),
        "Une fonction a recu une valeur du bon type mais impossible a traiter.",
        "Exemple courant : int(\"abc\"). Verifie ce que tu passes a la fonction.",
    ),
]


@dataclass
class FriendlyError:
    """Explication lisible d'une erreur, en plus du traceback brut."""

    summary: str
    hint: str
    raw_traceback: str


def explain(stderr_text: str) -> FriendlyError | None:
    """Analyse une sortie d'erreur et renvoie une explication, si reconnue."""
    if not stderr_text.strip():
        return None
    for pattern, summary_tpl, hint in _PATTERNS:
        match = pattern.search(stderr_text)
        if match:
            fields = {k: v for k, v in match.groupdict().items() if v is not None}
            return FriendlyError(
                summary=summary_tpl.format(**fields),
                hint=hint,
                raw_traceback=stderr_text.strip(),
            )
    return FriendlyError(
        summary="Ton programme s'est arrete a cause d'une erreur.",
        hint="Lis la derniere ligne du traceback : elle donne le type et le message de l'erreur.",
        raw_traceback=stderr_text.strip(),
    )
