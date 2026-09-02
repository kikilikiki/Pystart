"""Preferences de l'application, sauvegardees dans un simple fichier JSON.

Concept Python illustre ici : la serialisation JSON.
`json.dump` transforme un dictionnaire Python en texte ; `json.load` fait
l'operation inverse. C'est le moyen le plus simple de garder des reglages
entre deux lancements.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from app.core import paths

# Valeurs de theme acceptees par l'interface.
THEME_LIGHT = "light"
THEME_DARK = "dark"


@dataclass
class AppConfig:
    """Ensemble des preferences modifiables par l'utilisateur."""

    theme: str = THEME_DARK
    font_size: int = 13
    last_course_id: str | None = None
    last_exercise_id: str | None = None
    active_profile_id: int | None = None
    check_updates_on_startup: bool = True
    # Champ libre pour de futures options sans casser le format.
    extra: dict[str, Any] = field(default_factory=dict)

    # --- Chargement / sauvegarde -----------------------------------------
    @classmethod
    def load(cls) -> AppConfig:
        path = paths.config_path()
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # Fichier corrompu : on repart sur les valeurs par defaut
            # plutot que de planter au demarrage.
            return cls()
        known = {f: data[f] for f in cls.__dataclass_fields__ if f in data}
        return cls(**known)

    def save(self) -> None:
        path = paths.config_path()
        path.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
