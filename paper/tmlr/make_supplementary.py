#!/usr/bin/env python3
"""Build the anonymized OpenReview supplementary zip from a FRESH clone
of the public supporting record (github.com/<org>/decodable-is-not-
learned), for TMLR's double-blind review.

What the snapshot keeps: the committed record as files — the frozen
preregistration documents, every experiment's code, tests, ledgers,
committed probe fits, verdicts and retrospectives, and the paper source
with its figure/table scripts and the anonymous submission PDF.

What it omits (part of the de-anonymized repository linked at camera-
ready, per the paper's anonymous flavour): the git history, the raw
sampled draw streams (`*.draws.jsonl.gz`, ≈ 96 MB), the two named
PDFs, the outreach/metadata files (`paper/af-post.md`,
`paper/arxiv-metadata.txt`) and the provenance apparatus
(`PROVENANCE.md`, `provenance/`).

What it rewrites, in every text file, in this order: noreply and
personal email addresses → `[redacted-email]`; the repository URL →
`[repository-url-withheld]`; the GitHub handle → `[anon]`; the
machine's host name → `[anon-host]`; the author's name → `[AUTHOR]`
(`[AUTHOR]'s` for the possessive); home-directory paths →
`/Users/[anon]`; Zenodo DOIs and URLs → `[doi-withheld]` /
`[archive-url-withheld]`; Claude session URLs → `[session-url-
withheld]`. The README gains a leading review-copy paragraph. After
writing the tree the script SWEEPS it for residuals (text files by
regex, PDFs by text extraction) and refuses to zip if any remain.

Usage:
  git clone --no-local https://github.com/<org>/decodable-is-not-learned.git /tmp/src
  python paper/tmlr/make_supplementary.py --src /tmp/src --out /tmp/supplementary.zip
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {".git", "provenance"}
EXCLUDE_FILES = {"PROVENANCE.md", "paper/tmlr/preprint.pdf", "paper/decodable-is-not-learned.pdf",
                 "paper/af-post.md", "paper/arxiv-metadata.txt",
                 "paper/tmlr/make_supplementary.py"}   # this script names the identity terms
EXCLUDE_SUFFIX = ".draws.jsonl.gz"
TEXT_EXT = {".md", ".py", ".sh", ".txt", ".log", ".json", ".jsonl", ".tex", ".bib", ".sty", ".bst",
            ".gitignore", ".gitkeep", ".yaml", ".yml", ".cfg", ".toml", ".ini"}

# Ordered: the specific before the general, so a handle inside an email
# is redacted as an email, not as a handle.
REPLACEMENTS = [
    (re.compile(r"20031555\+lxman@users\.noreply\.github\.com"), "[redacted-email]"),
    (re.compile(r"jordan\.mymail@gmail\.com"), "[redacted-email]"),
    (re.compile(r"jordan\.mymail"), "[redacted-email]"),
    (re.compile(r"michael\.jordan@metrc\.com"), "[redacted-email]"),
    (re.compile(r"github\.com/lxman/decodable-is-not-learned"), "[repository-url-withheld]"),
    (re.compile(r"lxman"), "[anon]"),
    (re.compile(r"Michaels-Mini"), "[anon-host]"),
    (re.compile(r"/Users/michaeljordan"), "/Users/[anon]"),
    (re.compile(r"michaeljordan"), "[anon]"),
    (re.compile(r"Michael Jordan"), "[AUTHOR]"),
    (re.compile(r"Michael's", re.I), "[AUTHOR]'s"),
    (re.compile(r"Michael", re.I), "[AUTHOR]"),
    (re.compile(r"https?://(?:doi\.org/)?10\.5281/zenodo\.\d+"), "[doi-withheld]"),
    (re.compile(r"10\.5281/zenodo\.\d+"), "[doi-withheld]"),
    (re.compile(r"https?://zenodo\.org/\S+"), "[archive-url-withheld]"),
    (re.compile(r"https://claude\.ai/code/session_[A-Za-z0-9]+"), "[session-url-withheld]"),
]
RESIDUAL = [re.compile(p, re.I) for p in (r"michael", r"jordan", r"lxman", r"mymail", r"metrc",
                                            r"10\.5281", r"zenodo\.org", r"claude\.ai/code",
                                            r"/Users/(?!\[anon\])")]
PDF_RESIDUAL = re.compile(r"michael|jordan|lxman|mymail|metrc|zenodo\.org|10\.5281", re.I)
# Residuals that are not identity, allowlisted by (path regex, token
# regex); every allowed hit is counted and printed.
RESIDUAL_ALLOW = [
    # the country Jordan in the capitals battery and its wordlist
    (re.compile(r"^experiments/exp2b/battery/(items/capital\.json|wordlists\.py)$"), re.compile(r"jordan", re.I)),
    # model-generated Caesar-cipher continuations that happen to spell it
    (re.compile(r"^experiments/exp2[ghi]/results/sweep/.*/caesar[^/]*\.json$"), re.compile(r"jordan", re.I)),
]

README_NOTE = (
    "\n**Review copy (anonymized).** This snapshot of the public supporting record was prepared as "
    "OpenReview supplementary material for double-blind review. Identity-bearing strings are replaced "
    "throughout: the author's name by `[AUTHOR]`, usernames and host names by `[anon]`, email addresses "
    "by `[redacted-email]`, the repository URL, archive URLs and DOIs by `[...-withheld]`. Omitted from "
    "this snapshot, and part of the de-anonymized repository linked in the camera-ready version: the git "
    "history, the raw sampled draw streams (`*.draws.jsonl.gz`), the named PDFs and the provenance "
    "apparatus. Everything else is the record as committed.\n")


def _keep(rel: str) -> bool:
    parts = Path(rel).parts
    if parts and parts[0] in EXCLUDE_DIRS:
        return False
    if rel in EXCLUDE_FILES or rel.endswith(EXCLUDE_SUFFIX):
        return False
    return True


def _is_text(p: Path) -> bool:
    return p.suffix.lower() in TEXT_EXT or p.name in (".gitignore", ".gitkeep")


def scrub_text(s: str, counts: dict) -> str:
    for rx, repl in REPLACEMENTS:
        s, n = rx.subn(repl, s)
        if n:
            counts[rx.pattern] = counts.get(rx.pattern, 0) + n
    return s


def build_tree(src: Path, dst: Path) -> dict:
    if dst.exists():
        shutil.rmtree(dst)
    stats = {"kept": 0, "excluded_draws": 0, "excluded_named": 0, "excluded_dirs": 0, "text": 0,
             "binary": 0, "replacements": {}}
    for p in sorted(src.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(src))
        parts = Path(rel).parts
        if parts[0] in EXCLUDE_DIRS:
            stats["excluded_dirs"] += 1
            continue
        if rel.endswith(EXCLUDE_SUFFIX):
            stats["excluded_draws"] += 1
            continue
        if rel in EXCLUDE_FILES:
            stats["excluded_named"] += 1
            continue
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if _is_text(p):
            s = p.read_text(encoding="utf-8", errors="strict")
            s = scrub_text(s, stats["replacements"])
            if rel == "README.md":
                head, sep, tail = s.partition("\n")
                s = head + sep + README_NOTE + tail
            out.write_text(s, encoding="utf-8")
            stats["text"] += 1
        else:
            shutil.copy2(p, out)
            stats["binary"] += 1
        stats["kept"] += 1
    return stats


def sweep(dst: Path) -> list:
    bad = []
    sweep.allowed = 0
    for p in sorted(dst.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(dst))
        if _is_text(p):
            s = p.read_text(encoding="utf-8", errors="strict")
            allow = next((tok for path_rx, tok in RESIDUAL_ALLOW if path_rx.match(rel)), None)
            for rx in RESIDUAL:
                for m in rx.finditer(s):
                    if allow is not None and allow.fullmatch(m.group(0)):
                        sweep.allowed += 1
                        continue
                    line = s.count("\n", 0, m.start()) + 1
                    bad.append(f"{rel}:{line}: {m.group(0)!r}")
        elif p.suffix.lower() == ".pdf" and shutil.which("pdftotext"):
            txt = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout
            for m in PDF_RESIDUAL.finditer(txt):
                bad.append(f"{rel}: pdf text contains {m.group(0)!r}")
        elif p.suffix.lower() not in (".pdf", ".png", ".gz"):
            bad.append(f"{rel}: unclassified file type (neither text nor known binary)")
    return bad


def make_zip(dst: Path, out: Path) -> int:
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(dst.rglob("*")):
            if p.is_file():
                z.write(p, arcname=str(Path("decodable-is-not-learned-anonymized") / p.relative_to(dst)))
    return out.stat().st_size


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, help="a fresh clone of the public record")
    ap.add_argument("--out", required=True, help="the zip to write")
    ap.add_argument("--work", default=None, help="scratch directory for the scrubbed tree")
    ar = ap.parse_args(argv)
    src, out = Path(ar.src).resolve(), Path(ar.out).resolve()
    work = Path(ar.work).resolve() if ar.work else out.with_suffix(".tree")
    if not (src / "README.md").is_file() or not (src / "paper" / "tmlr" / "main.pdf").is_file():
        print(f"{src} does not look like the public record", file=sys.stderr)
        return 2
    stats = build_tree(src, work)
    print(f"kept {stats['kept']} files ({stats['text']} text scrubbed, {stats['binary']} binary copied); "
          f"excluded {stats['excluded_draws']} draw streams, {stats['excluded_named']} named files, "
          f"{stats['excluded_dirs']} files under {sorted(EXCLUDE_DIRS)}")
    for pat, n in sorted(stats["replacements"].items(), key=lambda kv: -kv[1]):
        print(f"  {n:6d}  {pat}")
    bad = sweep(work)
    if bad:
        print(f"RESIDUALS ({len(bad)}) — refusing to zip:", file=sys.stderr)
        for b in bad[:40]:
            print("  ", b, file=sys.stderr)
        return 3
    size = make_zip(work, out)
    print(f"residual sweep clean (text regex + pdf text; {sweep.allowed} allowlisted non-identity hits); "
          f"wrote {out} ({size / 1048576:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
