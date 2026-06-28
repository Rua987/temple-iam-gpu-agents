"""Run test_offline_agent_validation.py (unittest, no GPU required).

Exit 0 if all offline tests pass; exit 1 otherwise.
"""

import os
import re
import subprocess
import sys


EXPECTED_TESTS = 14


def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_script = os.path.join(repo_root, "test_offline_agent_validation.py")

    proc = subprocess.run(
        [sys.executable, test_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=repo_root,
        encoding="utf-8",
        errors="replace",
    )
    output = proc.stdout or ""
    if output.strip():
        safe = output.strip().encode("ascii", errors="replace").decode("ascii")
        print(safe)

    ran = re.search(r"Ran (\d+) tests", output)
    if not ran:
        print("FAIL: could not parse unittest summary.")
        return 1

    count = int(ran.group(1))
    ok = bool(re.search(r"^OK\s*$", output, re.MULTILINE))
    if ok and count == EXPECTED_TESTS and proc.returncode == 0:
        print(f"OK: {EXPECTED_TESTS} offline tests passed.")
        return 0

    print(
        f"FAIL: expected {EXPECTED_TESTS} passed (OK), "
        f"got Ran {count} tests, exit={proc.returncode}."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
