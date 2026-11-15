"""Run all tests in test_analog_explorer.py directly."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SERVER_DIR))

spec = importlib.util.spec_from_file_location(
    "test_analog_explorer", SERVER_DIR / "tests" / "test_analog_explorer.py"
)
assert spec is not None and spec.loader is not None
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def main() -> None:
    test_funcs = [
        getattr(t, name)
        for name in dir(t)
        if name.startswith("test_") and callable(getattr(t, name))
    ]
    print(f"Running {len(test_funcs)} test suites...")
    for fn in test_funcs:
        fn()
        print(f"  [PASS] {fn.__name__}")
    print("All backend tests passed successfully!")


if __name__ == "__main__":
    main()
