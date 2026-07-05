#!/usr/bin/env python3
"""Shim. The checker ships with the claim-licensing skill (so the
warrant-officer can self-check at runtime and the dispatcher can
check the boundary); this path is kept so the documented CLI
`python ci/validate_warrant.py <manifest-id> < warrant.md` and CI
imports keep working."""
import runpy
import sys
from pathlib import Path

TARGET = (Path(__file__).resolve().parent.parent / "skills" /
          "claim-licensing" / "validate_warrant.py")

if __name__ == "__main__":
    sys.argv[0] = str(TARGET)
    runpy.run_path(str(TARGET), run_name="__main__")
