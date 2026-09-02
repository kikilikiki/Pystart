"""Export / import de cours au format portable `.pystart` (archive ZIP).

Structure d'une archive :

    course.json
    lessons/*.md
    exercises/*.json
    assets/*            (optionnel)

SECURITE : un cours importe est du contenu qui vient de l'exterieur. On ne
lui fait PAS confiance. Avant d'extraire quoi que ce soit, on verifie :

  - pas de chemin absolu ni de ".." (protection contre le path traversal) ;
  - uniquement des extensions autorisees (.json, .md, images, .txt) ;
  - jamais de fichier .py execute automatiquement ;
  - une taille totale raisonnable (protection contre les "zip bombs").
"""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

from app.core import paths

PACKAGE_SUFFIX = ".pystart"

# Extensions autorisees a l'interieur d'une archive de cours.
_ALLOWED_SUFFIXES = {".json", ".md", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".svg"}
# Taille maximale decompressee (50 Mo).
_MAX_TOTAL_BYTES = 50 * 1024 * 1024


class PackageError(Exception):
    """Archive de cours invalide ou dangereuse."""


def _is_safe_member(name: str) -> bool:
    """Rejette les chemins absolus, les remontees `..` et les separateurs Windows."""
    normalized = name.replace("\\", "/")
    if normalized.startswith("/") or ":" in normalized:
        return False
    parts = normalized.split("/")
    return ".." not in parts and "" not in parts[:-1]


def export_course(course_dir: Path, destination: Path) -> Path:
    """Cree une archive `.pystart` a partir d'un dossier de cours."""
    course_dir = Path(course_dir)
    if not (course_dir / "course.json").is_file():
        raise PackageError(f"{course_dir} ne contient pas de course.json")

    if destination.suffix != PACKAGE_SUFFIX:
        destination = destination.with_suffix(PACKAGE_SUFFIX)

    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(course_dir.rglob("*")):
            if path.is_dir():
                continue
            if path.suffix.lower() not in _ALLOWED_SUFFIXES:
                continue
            archive.write(path, path.relative_to(course_dir).as_posix())
    return destination


def inspect_package(archive_path: Path) -> dict:
    """Ouvre l'archive SANS rien extraire et renvoie ses metadonnees.

    Sert a montrer un apercu ("Ce cours contient 3 lecons et 5 exercices,
    voulez-vous l'importer ?") avant toute ecriture sur le disque.
    """
    with zipfile.ZipFile(archive_path) as archive:
        members = archive.namelist()
        _validate_members(archive, members)
        if "course.json" not in members:
            raise PackageError("Archive invalide : course.json manquant.")
        meta = json.loads(archive.read("course.json").decode("utf-8"))

    return {
        "title": meta.get("title", "Cours sans titre"),
        "description": meta.get("description", ""),
        "level": meta.get("level", "debutant"),
        "lessons": sum(1 for m in members if m.startswith("lessons/") and m.endswith(".md")),
        "exercises": sum(1 for m in members if m.startswith("exercises/") and m.endswith(".json")),
    }


def _validate_members(archive: zipfile.ZipFile, members: list[str]) -> None:
    total = 0
    for info in archive.infolist():
        if not _is_safe_member(info.filename):
            raise PackageError(f"Chemin de fichier dangereux dans l'archive : {info.filename!r}")
        if info.filename.endswith("/"):
            continue
        suffix = Path(info.filename).suffix.lower()
        if suffix not in _ALLOWED_SUFFIXES:
            raise PackageError(f"Type de fichier non autorise : {info.filename!r}")
        total += info.file_size
        if total > _MAX_TOTAL_BYTES:
            raise PackageError("Archive trop volumineuse une fois decompressee (>50 Mo).")


def import_package(archive_path: Path, *, course_id: str | None = None, overwrite: bool = False) -> Path:
    """Importe une archive dans le dossier des cours de l'utilisateur.

    Renvoie le dossier du cours importe.
    """
    archive_path = Path(archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        members = archive.namelist()
        _validate_members(archive, members)
        if "course.json" not in members:
            raise PackageError("Archive invalide : course.json manquant.")
        meta = json.loads(archive.read("course.json").decode("utf-8"))

        target_id = course_id or _slugify(meta.get("id") or meta.get("title") or archive_path.stem)
        target_dir = paths.user_courses_dir() / target_id

        if target_dir.exists():
            if not overwrite:
                raise PackageError(
                    f"Un cours nomme {target_id!r} existe deja. "
                    "Choisis un autre nom ou active le remplacement."
                )
            shutil.rmtree(target_dir)

        target_dir.mkdir(parents=True)
        for member in members:
            if member.endswith("/"):
                continue
            # Double protection : on reverifie au moment d'ecrire.
            if not _is_safe_member(member):
                raise PackageError(f"Chemin dangereux : {member!r}")
            out_path = target_dir / member
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(archive.read(member))

    return target_dir


def _slugify(text: str) -> str:
    keep = "".join(c if c.isalnum() or c in " -_" else "" for c in str(text)).strip()
    return keep.lower().replace(" ", "_") or "cours_importe"
