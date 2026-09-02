"""Comparaison de numeros de version.

Pourquoi un module dedie ? Parce qu'il ne faut JAMAIS comparer des versions
comme de simples chaines de caracteres :

    "0.0.9" < "0.0.10"   # Faux si on compare lettre par lettre !

On s'appuie sur la bibliotheque `packaging`, qui implemente la norme des
versions Python (PEP 440) et sait comparer correctement 0.0.9 et 0.0.10.
"""

from __future__ import annotations

from packaging.version import InvalidVersion, Version


def parse(version_text: str) -> Version:
    """Transforme une chaine ("1.2.3") en objet Version comparable.

    Leve `ValueError` si la chaine n'est pas une version valide, afin que
    l'appelant puisse afficher un message clair.
    """
    text = version_text.strip().lstrip("vV")
    try:
        return Version(text)
    except InvalidVersion as error:
        raise ValueError(f"Version invalide : {version_text!r}") from error


def is_newer(candidate: str, current: str) -> bool:
    """Retourne True si `candidate` est une version plus recente que `current`."""
    return parse(candidate) > parse(current)


def compare(left: str, right: str) -> int:
    """Retourne -1, 0 ou 1 selon que `left` est <, == ou > `right`."""
    a, b = parse(left), parse(right)
    if a < b:
        return -1
    if a > b:
        return 1
    return 0
