#!/usr/bin/env python3
"""Shared helpers for mathmodel-paper-gate scripts."""
from __future__ import annotations

import re
from pathlib import Path

AI_TASTE_PATTERNS: list[str] = [
    r"看板",
    r"文字版",
    r"以\s*CSV\s*为准",
    r"写作自检",
    r"为便于快速浏览",
    r"浓缩一次",
    r"对审稿",
    r"对评委最有效",
    r"答辩口头",
    r"范畴错误",
    r"改稿提示",
    r"答辩材料提示",
    r"CLAUDE\.md",
    r"TODO:",
    r"FIXME",
    r"lorem ipsum",
]

# Prefer active entry trees; skip known draft/backup names unless --all-paper
DEFAULT_ENTRY_CANDIDATES = [
    "paper_v2/main.typ",
    "paper/main.typ",
    "paper/main.tex",
    "paper_v2/main.tex",
]

BACKUP_NAME_RE = re.compile(
    r"(Thematic_|MetaAgent_|_backup|_old|_draft|rebuild_|fix_|hard_fix)",
    re.I,
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def find_reports_dir(root: Path) -> Path | None:
    for d in (root / "reports", root / "mathmodel_paper" / "reports"):
        if d.is_dir():
            return d
    return None


def find_lock_outline(root: Path) -> tuple[Path | None, Path | None]:
    lock = outline = None
    for d in (root / "reports", root / "mathmodel_paper" / "reports"):
        if (d / "PAPER_FACTS.lock.md").exists():
            lock = d / "PAPER_FACTS.lock.md"
        if (d / "PAPER_OUTLINE.md").exists():
            outline = d / "PAPER_OUTLINE.md"
    return lock, outline


def parse_yaml_block(text: str) -> dict[str, str]:
    m = re.search(r"```yaml\s*(.*?)```", text, re.S | re.I)
    block = m.group(1) if m else text[:1200]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().split("#")[0].strip().strip('"').strip("'")
    return out


def set_yaml_fields(text: str, updates: dict[str, str]) -> str:
    m = re.search(r"(```yaml\s*)(.*?)(```)", text, re.S | re.I)
    if not m:
        raise ValueError("No ```yaml block found")
    body = m.group(2)
    lines = body.splitlines()
    keys_done = set()
    new_lines = []
    for line in lines:
        if ":" in line and not line.strip().startswith("#"):
            k = line.split(":", 1)[0].strip()
            if k in updates:
                # preserve indent
                indent = line[: len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}{k}: {updates[k]}")
                keys_done.add(k)
                continue
        new_lines.append(line)
    for k, v in updates.items():
        if k not in keys_done:
            new_lines.insert(0, f"{k}: {v}")
    new_body = "\n".join(new_lines)
    if not new_body.endswith("\n"):
        new_body += "\n"
    return text[: m.start()] + m.group(1) + new_body + m.group(3) + text[m.end() :]


def truthy(v: str) -> bool:
    return v.strip().lower() in {"true", "yes", "1"}


def extract_must_appear(lock_text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in lock_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 7:
            continue
        if cells[0].lower() in {"id", "----"} or set(cells[0]) <= {"-"}:
            continue
        if cells[6].lower() not in {"yes", "y", "true", "是"}:
            continue
        if cells[3] in {"", "…", "..."}:
            continue
        rows.append((cells[0], cells[3]))
    return rows


def extract_figure_paths(lock_text: str) -> list[tuple[str, str]]:
    """Return (fig_id, path) from charts section tables with a path-like cell."""
    rows = []
    in_figs = False
    for line in lock_text.splitlines():
        if line.strip().startswith("## 5") or "图表槽" in line:
            in_figs = True
            continue
        if in_figs and line.startswith("## "):
            break
        if not in_figs or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        if cells[0].lower() in {"fig_id", "----"} or set(cells[0]) <= {"-"}:
            continue
        path = cells[1]
        if path.endswith((".pdf", ".png", ".svg")) or path.startswith("figures/"):
            rows.append((cells[0], path))
    return rows


def extract_forbidden_lines(lock_text: str) -> list[str]:
    lines = []
    in_sec = False
    for line in lock_text.splitlines():
        if "不可说" in line or "FORBIDDEN" in line:
            in_sec = True
            continue
        if in_sec and line.startswith("## "):
            break
        if in_sec and line.strip().startswith("-"):
            t = line.strip().lstrip("-").strip()
            if t:
                lines.append(t)
    return lines


def value_in_paper(value: str, paper: str) -> bool:
    v = value.strip().lstrip("~≈")
    if not v:
        return False
    variants = {v, v.replace("±", "+-"), v.replace("+-", "±")}
    m = re.match(r"^[+-]?\d+\.\d+", v)
    if m:
        try:
            f = float(m.group(0))
            variants.update(
                {
                    m.group(0),
                    f"{f:.4f}".rstrip("0").rstrip("."),
                    f"{f:.3f}",
                    f"{f:.2f}",
                }
            )
        except ValueError:
            pass
    return any(c and c in paper for c in variants)


def resolve_includes(entry: Path, seen: set[Path] | None = None) -> list[Path]:
    """Collect entry + typst/latex includes relative to entry parent."""
    seen = seen or set()
    entry = entry.resolve()
    if entry in seen or not entry.exists():
        return []
    seen.add(entry)
    out = [entry]
    text = read_text(entry)
    parent = entry.parent
    patterns = [
        r'#include\("([^"]+)"\)',
        r"#include\('([^']+)'\)",
        r"\\input\{([^}]+)\}",
        r"\\include\{([^}]+)\}",
    ]
    for pat in patterns:
        for rel in re.findall(pat, text):
            cand = (parent / rel).resolve()
            if not cand.exists() and not cand.suffix:
                for ext in (".typ", ".tex"):
                    if (parent / f"{rel}{ext}").exists():
                        cand = (parent / f"{rel}{ext}").resolve()
                        break
            out.extend(resolve_includes(cand, seen))
    return out


def collect_paper_files(root: Path, main: Path | None = None, all_paper: bool = False) -> list[Path]:
    root = root.resolve()
    if main is not None:
        return resolve_includes(main if main.is_absolute() else root / main)

    if not all_paper:
        for rel in DEFAULT_ENTRY_CANDIDATES:
            p = root / rel
            if p.exists():
                return resolve_includes(p)

    files: list[Path] = []
    for pattern in ("paper/**/*.typ", "paper/**/*.tex", "paper_v2/**/*.typ", "paper_v2/**/*.tex"):
        files.extend(root.glob(pattern))
    uniq = sorted({f.resolve() for f in files if f.is_file()})
    if all_paper:
        return uniq
    return [f for f in uniq if not BACKUP_NAME_RE.search(f.name)]


def paper_blob_with_index(files: list[Path]) -> tuple[str, list[tuple[Path, int, int]]]:
    """Return concatenated text and list of (path, start_offset, end_offset)."""
    chunks: list[str] = []
    index: list[tuple[Path, int, int]] = []
    pos = 0
    for f in files:
        t = read_text(f)
        start = pos
        chunks.append(t)
        pos += len(t) + 1  # + newline joiner
        index.append((f, start, pos - 1))
        chunks.append("\n")
    return "".join(chunks), index


def offset_to_location(offset: int, index: list[tuple[Path, int, int]]) -> tuple[Path, int]:
    for path, start, end in index:
        if start <= offset < end:
            local = offset - start
            line = read_text(path)[:local].count("\n") + 1
            return path, line
    if index:
        return index[-1][0], 1
    return Path("?"), 0


def find_ai_taste_hits(paper: str, index: list[tuple[Path, int, int]]) -> list[str]:
    hits: list[str] = []
    for pat in AI_TASTE_PATTERNS:
        for m in re.finditer(pat, paper, re.I):
            path, line = offset_to_location(m.start(), index)
            snippet = paper[max(0, m.start() - 12) : m.end() + 24].replace("\n", " ")
            hits.append(f"{path.name}:{line}: /{pat}/ …{snippet}…")
    return hits
