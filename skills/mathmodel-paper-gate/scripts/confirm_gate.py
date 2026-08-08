#!/usr/bin/env python3
"""Flip lock/outline yaml status after user confirmation (explicit flags required)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gate_lib import find_lock_outline, read_text, set_yaml_fields  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--lock", action="store_true", help="Mark PAPER_FACTS.lock frozen + confirmed")
    ap.add_argument("--outline", action="store_true", help="Mark PAPER_OUTLINE approved + confirmed")
    ap.add_argument(
        "--i-confirm",
        action="store_true",
        help="Required safety flag: you (or user) reviewed the content",
    )
    args = ap.parse_args()
    if not args.i_confirm:
        print("Refuse: pass --i-confirm after human review.", file=sys.stderr)
        return 2
    if not args.lock and not args.outline:
        print("Specify --lock and/or --outline", file=sys.stderr)
        return 2

    root = args.root.resolve()
    lock_path, outline_path = find_lock_outline(root)
    if args.lock:
        if not lock_path:
            print("LOCK missing", file=sys.stderr)
            return 1
        text = set_yaml_fields(
            read_text(lock_path),
            {"status": "frozen", "confirmed_by_user": "true"},
        )
        lock_path.write_text(text, encoding="utf-8")
        print(f"updated {lock_path}")
    if args.outline:
        if not outline_path:
            print("OUTLINE missing", file=sys.stderr)
            return 1
        text = set_yaml_fields(
            read_text(outline_path),
            {"status": "approved", "confirmed_by_user": "true"},
        )
        outline_path.write_text(text, encoding="utf-8")
        print(f"updated {outline_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
