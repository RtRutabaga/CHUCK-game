"""Windows packaging and frozen-runtime path regression tests."""

import sys
from pathlib import Path
from unittest.mock import patch

from main import crash_log_path
from src.core import config


def test_source_crash_log_stays_beside_main() -> None:
    expected = Path(__file__).resolve().parents[1] / "crash_log.txt"
    assert crash_log_path() == expected


def test_frozen_crash_log_stays_beside_shared_executable() -> None:
    executable = r"C:\Users\friend\Desktop\CHUCK-demo.exe"
    with patch.object(sys, "frozen", True, create=True), patch.object(
        sys, "executable", executable
    ):
        assert crash_log_path() == Path(executable).with_name("crash_log.txt")


def test_bundle_resource_roots_are_relative_to_project_root() -> None:
    assert config.ASSETS_DIR == config.PROJECT_ROOT / "assets"
    assert config.DATA_DIR == config.PROJECT_ROOT / "data"


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All packaging tests passed.")


if __name__ == "__main__":
    _run_all()
