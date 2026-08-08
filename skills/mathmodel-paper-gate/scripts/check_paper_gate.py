#!/usr/bin/env python3
"""Hard gate: lock/outline freeze, AI-taste, must_appear numbers, figure paths."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gate_lib import (  # noqa: E402
    collect_paper_files,
    extract_figure_paths,
    extract_must_appear,
    find_ai_taste_hits,
    find_lock_outline,
    paper_blob_with_index,
    parse_yaml_block,
    read_text,
    truthy,
    value_in_paper,
)


def rel_to(root: Path, f: Path) -> str:
    try:
        return str(f.relative_to(root))
    except ValueError:
        return str(f)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument(
        "--pass",
        dest="gate_pass",
        choices=["a", "b", "c", "all"],
        default="all",
        help="a=lock/outline only; b=+numbers+figs; c/all=full incl. AI-taste",
    )
    ap.add_argument("--main", type=Path, default=None, help="Paper entry (.typ/.tex)")
    ap.add_argument("--all-paper", action="store_true", help="Scan backups too")
    ap.add_argument("--skip-numbers", action="store_true")
    ap.add_argument("--allow-draft", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()

    fails: list[str] = []
    warns: list[str] = []

    lock_path, outline_path = find_lock_outline(root)
    if lock_path is None:
        fails.append("MISSING reports/PAPER_FACTS.lock.md")
    if outline_path is None:
        fails.append("MISSING reports/PAPER_OUTLINE.md")

    lock_text = read_text(lock_path) if lock_path else ""
    outline_text = read_text(outline_path) if outline_path else ""

    must: list = []
    figs: list = []
    if lock_path:
        meta = parse_yaml_block(lock_text)
        if not args.allow_draft:
            if meta.get("status", "").lower() != "frozen":
                fails.append(f"LOCK status='{meta.get('status', '?')}' (need frozen)")
            if not truthy(meta.get("confirmed_by_user", "")):
                fails.append("LOCK confirmed_by_user not true")
        must = extract_must_appear(lock_text)
        figs = extract_figure_paths(lock_text)
        if not must:
            warns.append("LOCK has no must_appear=yes rows")

    if outline_path:
        meta = parse_yaml_block(outline_text)
        if not args.allow_draft:
            if meta.get("status", "").lower() != "approved":
                fails.append(f"OUTLINE status='{meta.get('status', '?')}' (need approved)")
            if not truthy(meta.get("confirmed_by_user", "")):
                fails.append("OUTLINE confirmed_by_user not true")
        if not meta.get("style_card"):
            warns.append("OUTLINE missing style_card")

    need_paper = args.gate_pass in {"b", "c", "all"}
    paper_files = collect_paper_files(root, args.main, args.all_paper) if need_paper else []
    paper, index = paper_blob_with_index(paper_files) if paper_files else ("", [])

    print(f"root: {root}")
    print(f"pass: {args.gate_pass}")
    print(f"lock: {lock_path}")
    print(f"outline: {outline_path}")
    print(f"paper files: {len(paper_files)}")
    for f in paper_files[:8]:
        print(f"  - {rel_to(root, f)}")

    def emit_and_exit(code_if_fail: int = 1) -> int:
        for w in warns:
            print(f"WARN: {w}")
        for fmsg in fails:
            print(f"FAIL: {fmsg}")
        if fails:
            print(f"RESULT: FAIL ({len(fails)} errors)")
            return code_if_fail
        print("RESULT: PASS")
        return 0

    if args.gate_pass == "a":
        return emit_and_exit()

    if need_paper and not paper_files:
        warns.append("No active paper entry (expected paper/main.typ or paper_v2/main.typ)")

    if paper_files and args.gate_pass in {"c", "all"}:
        for hit in find_ai_taste_hits(paper, index):
            fails.append(f"AI-taste {hit}")

    if paper_files and not args.skip_numbers and must:
        missing = [f"{rid}={val}" for rid, val in must if not value_in_paper(val, paper)]
        if missing:
            fails.append("must_appear missing in active paper: " + ", ".join(missing[:20]))

    for fid, rel in figs:
        cands = [root / rel, (root / rel).resolve()]
        # also try repo-style figures next to mathmodel_paper
        cands.append(root.parent / "mathmodel_paper" / rel)
        cands.append(root / "mathmodel_paper" / rel)
        if not any(Path(c).exists() for c in cands):
            warns.append(f"figure not found {fid}: {rel} (WARN; embed only if exists)")

    if paper and len(re.findall(r"\d+\.\d+", paper)) < 6:
        warns.append("few decimal numbers in paper; abstract/results may lack quantification")

    return emit_and_exit()


if __name__ == "__main__":
    sys.exit(main())
