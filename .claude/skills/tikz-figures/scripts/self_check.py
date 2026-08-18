#!/usr/bin/env python3
"""Check a TikZ figure .tex file against the house invariants.

Usage: python self_check.py <path-to.tex> [--no-compile]

Exits 0 if all checks pass, 1 otherwise, printing one reason per failure.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAW_COLOR_RE = re.compile(r"\\(?:node|draw)\[[^\]]*\b(?:fill|draw|color|text)=(#[0-9A-Fa-f]{6}|[0-9A-Fa-f]{6}(?![0-9A-Fa-f]))")


def check_documentclass(text: str) -> str | None:
    if not re.search(r"\\documentclass\[[^\]]*tikz[^\]]*\]\{standalone\}", text):
        return "missing \\documentclass[...,tikz,...]{standalone}"
    if not re.search(r"\\documentclass\[[^\]]*border=", text):
        return "missing a border= option on \\documentclass"
    return None


def check_amsmath(text: str) -> str | None:
    if "\\usepackage{amsmath}" not in text:
        return "missing \\usepackage{amsmath}"
    return None


def check_font(text: str) -> str | None:
    required = [
        r"\usepackage{helvet}",
        r"\renewcommand{\familydefault}{\sfdefault}",
        r"\usepackage{sansmath}",
        r"\sansmath",
    ]
    missing = [r for r in required if r not in text]
    if missing:
        return "missing sans-serif font invariant: " + ", ".join(missing)
    return None


def check_tikzlibrary(text: str) -> str | None:
    matches = re.findall(r"\\usetikzlibrary\{([^}]*)\}", text)
    if not matches:
        return "missing \\usetikzlibrary{...}"
    libs = {lib.strip() for group in matches for lib in group.split(",")}
    required = {"arrows.meta", "positioning"}
    missing = required - libs
    if missing:
        return f"\\usetikzlibrary missing: {', '.join(sorted(missing))}"
    return None


def check_named_colors(text: str) -> str | None:
    m = RAW_COLOR_RE.search(text)
    if m:
        return f"raw color used inline instead of a named \\definecolor/\\colorlet: {m.group(0)!r}"
    return None


def check_named_style(text: str) -> str | None:
    if "\\tikzset{" in text:
        return None
    if re.search(r"\\begin\{tikzpicture\}\s*\[", text):
        return None
    return "no \\tikzset{...} block or bracketed \\begin{tikzpicture}[...] option list found"


def check_compiles(path: Path) -> str | None:
    latexmk = shutil.which("latexmk")
    if not latexmk:
        return "SKIP: latexmk not on PATH, could not verify compilation"
    result = subprocess.run(
        [latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error", path.name],
        cwd=path.parent,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        tail = "\n".join(result.stdout.splitlines()[-15:])
        return f"latexmk failed to compile:\n{tail}"
    return None


CHECKS = [
    check_documentclass,
    check_amsmath,
    check_font,
    check_tikzlibrary,
    check_named_colors,
    check_named_style,
]


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--no-compile"]
    no_compile = "--no-compile" in sys.argv[1:]
    if len(args) != 1:
        print(__doc__)
        return 2
    path = Path(args[0])
    if not path.is_file():
        print(f"not a file: {path}")
        return 2

    text = path.read_text(encoding="utf-8")
    failures = [msg for check in CHECKS if (msg := check(text))]

    if not no_compile:
        compile_msg = check_compiles(path)
        if compile_msg:
            failures.append(compile_msg)

    if failures:
        print(f"FAIL: {path}")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
