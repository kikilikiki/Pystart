"""Tests de l'export / import de cours et de la protection contre les archives piegees."""

import zipfile

import pytest

from app.core import paths
from app.teacher import package
from app.teacher.authoring import create_empty_course


def test_export_then_import_roundtrip():
    course_dir = create_empty_course("Cours de test")
    archive = package.export_course(course_dir, paths.app_data_dir() / "export")
    assert archive.suffix == ".pystart"

    info = package.inspect_package(archive)
    assert info["lessons"] == 1
    assert info["exercises"] == 1

    imported = package.import_package(archive, course_id="cours_importe", overwrite=True)
    assert (imported / "course.json").is_file()


def test_path_traversal_is_rejected(tmp_path):
    evil = tmp_path / "evil.pystart"
    with zipfile.ZipFile(evil, "w") as zf:
        zf.writestr("course.json", '{"title": "x"}')
        zf.writestr("../../escape.json", "{}")
    with pytest.raises(package.PackageError):
        package.inspect_package(evil)


def test_disallowed_extension_is_rejected(tmp_path):
    evil = tmp_path / "script.pystart"
    with zipfile.ZipFile(evil, "w") as zf:
        zf.writestr("course.json", '{"title": "x"}')
        zf.writestr("payload.py", "print('pwned')")
    with pytest.raises(package.PackageError):
        package.inspect_package(evil)
