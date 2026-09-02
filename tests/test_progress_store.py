"""Tests de la base de progression (SQLite) et de sa persistance."""

from app.core import paths
from app.progress.store import ProgressStore


def test_profile_creation_and_default():
    store = ProgressStore()
    profile = store.ensure_default_profile()
    assert profile.id == 1
    assert store.ensure_default_profile().id == 1  # pas de doublon
    store.close()


def test_attempts_and_completion():
    store = ProgressStore()
    profile = store.create_profile("Eleve", "debutant")

    store.record_attempt(profile.id, "c1.e1", "c1", passed=False)
    assert not store.is_exercise_passed(profile.id, "c1.e1")

    store.record_attempt(profile.id, "c1.e1", "c1", passed=True)
    assert store.is_exercise_passed(profile.id, "c1.e1")

    # Une fois reussi, un echec ulterieur ne "deprecie" pas le succes.
    store.record_attempt(profile.id, "c1.e1", "c1", passed=False)
    assert store.is_exercise_passed(profile.id, "c1.e1")

    stats = store.course_stats(profile.id, "c1", total_exercises=1)
    assert stats.completed
    assert stats.percent == 100
    store.close()


def test_data_survives_reopen():
    path = paths.database_path()
    store = ProgressStore(path)
    profile = store.create_profile("Persistant")
    store.record_attempt(profile.id, "x.y", "x", passed=True)
    store.close()

    reopened = ProgressStore(path)
    assert reopened.is_exercise_passed(profile.id, "x.y")
    reopened.close()


def test_migration_sets_user_version():
    store = ProgressStore()
    version = store._conn.execute("PRAGMA user_version").fetchone()[0]
    assert version >= 1
    store.close()
