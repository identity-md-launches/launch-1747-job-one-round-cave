#!/usr/bin/env python3
"""Compatibility entry point for the bounded public-read RPC snapshot tool."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent /
                       "bounded-rpc-snapshot" / "snapshot.py"), run_name="__main__")
