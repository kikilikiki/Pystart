"""Tests de l'execution de code dans un processus separe."""

from app.execution.runner import run_script


def test_simple_program_stdout():
    result = run_script('print("bonjour")')
    assert result.ok
    assert result.stdout.strip() == "bonjour"
    assert result.exit_code == 0


def test_program_with_error_is_reported():
    result = run_script("print(inconnu)")
    assert not result.ok
    assert "NameError" in result.stderr


def test_infinite_loop_times_out():
    result = run_script("while True:\n    pass", timeout_seconds=1.0)
    assert result.timed_out
    assert not result.ok


def test_stdin_is_passed():
    result = run_script("print(input())", stdin_text="salut\n")
    assert result.stdout.strip() == "salut"


def test_large_output_is_truncated():
    result = run_script("print('x' * 10_000_000)")
    assert len(result.stdout) <= 200_001
