"""Run the whole test suite, and say how much of it ran.

The tests here are plain modules: a module full of `test_*` functions,
most with a `_run_all()` for running one file on its own. There is no
pytest and adding one is not wanted -- `WEB-BUILD.md` says not to grow a
second runner. So this is the runner: it imports each module and calls
each `test_*` function in it.

    python tools/run_tests.py

The last line is the one that matters:

    modules: 192 of 192
    no failures

**Read the module count, not just the failure line.** A module that
fails to *import* never contributes a test, and a runner that only
reported failures would call that silence success. That is not
hypothetical: `test_treasure_handoffs` imported pytest and had been
quietly running zero tests for days while the suite looked green. The
count is what catches it, which is why it is printed even when
everything passes.

Options:

    --jobs N     worker processes (default 4)
    --quiet      failures only, no per-test lines
    <name>...    run only these modules, e.g. test_save_registry

Exits non-zero if anything failed or failed to import, so it can gate a
commit.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

# test_tilemap is much slower than the rest, so it gets a worker to
# itself rather than making one shard the long pole.
SLOW = ("test_tilemap",)


def discover() -> list[str]:
    names = sorted(
        path.stem for path in TESTS.glob("test_*.py") if path.is_file()
    )
    return names


def run_modules(names: list[str], quiet: bool) -> int:
    """Worker: import each module, call each test in it. Returns failures."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    sys.path[:0] = [str(ROOT), str(TESTS), str(ROOT / "tools")]

    import importlib

    failures = 0
    for name in names:
        try:
            module = importlib.import_module(name)
        except Exception:                      # noqa: BLE001 - report, continue
            failures += 1
            print(f"FAIL-IMPORT {name}", flush=True)
            traceback.print_exc()
            continue
        for attribute in sorted(dir(module)):
            if not attribute.startswith("test_"):
                continue
            function = getattr(module, attribute)
            if not callable(function):
                continue
            try:
                function()
                if not quiet:
                    print(f"  pass {attribute}", flush=True)
            except Exception:                  # noqa: BLE001 - as above
                failures += 1
                print(f"FAIL {name}.{attribute}", flush=True)
                traceback.print_exc()
        print(f"done {name}", flush=True)
    return failures


def shard(names: list[str], jobs: int) -> list[list[str]]:
    """Split into `jobs` shards, with the slow modules given their own."""
    slow = [name for name in names if name in SLOW]
    rest = [name for name in names if name not in SLOW]
    shards: list[list[str]] = [[] for _ in range(max(1, jobs - bool(slow)))]
    for index, name in enumerate(rest):
        shards[index % len(shards)].append(name)
    if slow:
        shards.append(slow)
    return [chunk for chunk in shards if chunk]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modules", nargs="*", help="modules to run")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--worker", action="store_true",
                        help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.worker:
        return 1 if run_modules(args.modules, args.quiet) else 0

    names = args.modules or discover()
    if not names:
        print("no test modules found", file=sys.stderr)
        return 1

    processes = []
    for chunk in shard(names, args.jobs):
        command = [sys.executable, "-u", __file__, "--worker", *chunk]
        if args.quiet:
            command.insert(3, "--quiet")
        processes.append(subprocess.Popen(
            command, cwd=ROOT, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8",
            errors="replace"))

    output = []
    for process in processes:
        out, _ = process.communicate()
        output.append(out or "")

    combined = "".join(output)
    if not args.quiet:
        print(combined, end="")

    ran = sum(1 for line in combined.splitlines() if line.startswith("done "))
    failed = [line for line in combined.splitlines()
              if line.startswith(("FAIL ", "FAIL-IMPORT "))]

    if args.quiet and failed:
        print("\n".join(failed))
    print(f"modules: {ran} of {len(names)}")
    if failed:
        print("\n".join(failed) if not args.quiet else "")
        return 1
    if ran != len(names):
        print("a module neither finished nor reported a failure")
        return 1
    print("no failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
