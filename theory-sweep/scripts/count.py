#!/usr/bin/env python3
"""Count field reports and compare six metrics with a synthesis header table."""
import argparse
from pathlib import Path
import re
import runpy
import sys

SCORE = runpy.run_path(str(Path(__file__).with_name("score_format.py")))
STRINGS = SCORE["STRINGS"]
METRICS = tuple(STRINGS["en"]["synthesis_metrics"])


def reports_in(folder):
    if not folder.is_dir():
        raise ValueError(f"Report folder not found: {folder}")
    for path in sorted(folder.glob("*.md")):
        with path.open(encoding="utf-8") as stream:
            first = stream.readline()
        if first.startswith("# ") and any(s["title_marker"] in first for s in STRINGS.values()):
            yield path


def number(cell):
    cell = cell.strip().replace("**", "").replace("`", "")
    match = re.fullmatch(r"([\d,]+)\s*(?:개|건)?", cell)
    return int(match[1].replace(",", "")) if match else None


def expected_counts(path):
    text = path.read_text(encoding="utf-8")
    lang = SCORE["detect_language"](text, allow_title=False)
    if lang is None:
        raise ValueError("cannot compare: unknown language")
    found, header = {}, None
    keys = {re.sub(r"\s+", "", label): key
            for key, label in STRINGS[lang]["synthesis_metrics"].items()}

    def record(key, value):
        if key in found and found[key] != value:
            raise ValueError(f"Conflicting header table values: {key}")
        found[key] = value

    for line in text.splitlines()[:100]:
        if not line.strip().startswith("|"):
            header = None
            continue
        cells = [x.strip().replace("**", "").replace("`", "")
                 for x in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", x) for x in cells):
            continue
        labels = [re.sub(r"\s+", "", x) for x in cells]
        # Identify vertical metric rows directly, independent of header wording.
        if len(cells) == 2 and labels[0] in keys and number(cells[1]) is not None:
            record(keys[labels[0]], number(cells[1]))
            header = None
        elif any(x in keys for x in labels):
            header = labels
        elif header and len(header) == len(cells):
            for key, cell in zip(header, cells):
                value = number(cell)
                if key in keys and value is not None:
                    record(keys[key], value)
            header = None
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", type=Path)
    parser.add_argument("--expect", type=Path, help="Compare against a synthesis header table")
    args = parser.parse_args()
    try:
        rows = []
        for path in reports_in(args.reports):
            result = SCORE["score"](path)
            if result["language"] is None:
                raise ValueError(f"{path}: unknown language")
            marker = STRINGS[result["language"]]["recheck_marker"].split("{", 1)[0]
            rows.append((path.stem, result, sum(marker in item["source"] for item in result["items"])))
        if not rows:
            raise ValueError("No field reports found")
        actual = {"fields": len(rows), "reports": len(rows),
                  "candidates": sum(r["candidates"] for _, r, _ in rows),
                  "already_met_any": sum(r["already_met"] for _, r, _ in rows),
                  "already_met_full": sum(r["already_met_full"] for _, r, _ in rows),
                  "unverified": sum(r["unverified_title_flags"] for _, r, _ in rows)}
        names = STRINGS["en"]["synthesis_metrics"]
        print(" / ".join(f"{names[key]}: {value}" for key, value in actual.items()))
        print(f"Recheck markers: {sum(n for _, _, n in rows)} (at most one per candidate heading)")
        print("| Field (slug) | Reports | Candidates | Unverified flags | Recheck markers | Already met (any) | Already met (fully) |")
        print("|---|---|---|---|---|---|---|")
        for slug, result, recheck in rows:
            print(f"| {slug} | 1 | {result['candidates']} | {result['unverified_title_flags']} | {recheck} | {result['already_met']} | {result['already_met_full']} |")
        if not args.expect:
            return 0
        expected = expected_counts(args.expect)
        missing = [key for key in METRICS if key not in expected]
        if missing:
            print("cannot compare: missing numeric synthesis metrics: " + ", ".join(missing))
        failed = bool(missing)
        for key, value in expected.items():
            ok = actual[key] == value
            print(f"{'match' if ok else 'mismatch'}: {key} reports={actual[key]}, synthesis={value}")
            failed |= not ok
        return int(failed)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
