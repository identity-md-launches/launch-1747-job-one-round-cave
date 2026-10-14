#!/usr/bin/env python3
"""Check ordered JSON deliverables with the shared offline contract engine."""
import importlib.util
import sys
from pathlib import Path

if __name__ == "__main__":
    engine_path = Path(__file__).resolve().parent.parent / "json-contract" / "check.py"
    if not engine_path.resolve().is_relative_to(Path.cwd().resolve()):
        print('{"error": "run from a workspace containing both tool folders"}')
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("contract_engine", engine_path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    sys.exit(engine.main())
