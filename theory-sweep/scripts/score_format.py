#!/usr/bin/env python3
"""Score report structure, candidate labels, scenes, and group references."""
import argparse
import json
import re
import sys
import pathlib
import runpy

CONTRACT = runpy.run_path(str(pathlib.Path(__file__).with_name("_strings.py")))
STRINGS = CONTRACT["STRINGS"]
detect_language = CONTRACT["detect_language"]
label_pattern = CONTRACT["label_pattern"]
GROUP_RE = re.compile(r"(?<![\d./-])\b(\d{1,2}-\d{1,2})\b(?![\d./-])")


def section_kind(title, strings):
    for key, name in strings["sections"].items():
        if title == name or (key == "recheck" and re.fullmatch(
                re.escape(name) + r" \(\d{4}-\d{2}-\d{2}\)", title)):
            return name
    return None


def split_title(title):
    # Preserve the optional explicit source boundary used by older reports.
    marked = re.search(r" — (?:Source|출처)\s*[:：]\s*", title, re.I)
    if marked:
        return title[:marked.start()].strip(), title[marked.end():].strip()
    name, _, source = title.partition(" — ")
    return name.strip(), source.strip()


def parse_groups(value):
    path = pathlib.Path(value)
    if "," not in value and path.is_file():
        entries = [part.strip() for line in path.read_text(encoding="utf-8").splitlines()
                   for part in line.split("·") if part.strip()]
        pattern = r"(\d{1,2}-\d{1,2})(?:\s+.+)?"
    else:
        entries = [part.strip() for part in value.split(",")]
        pattern = r"(\d{1,2}-\d{1,2})"
    groups = set()
    for entry in entries:
        match = re.fullmatch(pattern, entry)
        if not match:
            raise ValueError(f"Invalid group number or missing map file: {entry!r}")
        groups.add(match[1])
    if not groups:
        raise ValueError("Group list is empty")
    return groups


def score(path: pathlib.Path, groups=None) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    r = {"file": str(path), "lines": len(lines), "other_sections": [], "auxiliary_sections": []}
    lang = detect_language(text)
    strings = STRINGS[lang or "en"]
    labels_map = strings["labels"]
    patterns = {key: label_pattern(strings, key) for key in labels_map}
    all_labels = "(?:" + "|".join(patterns.values()) + ")"
    r["language"] = lang
    r["reason"] = None if lang else "unknown language"
    r["title_ok"] = bool(lang and lines and lines[0].startswith("# ")
                         and strings["title_marker"] in lines[0])
    r["status_ok"] = bool(lang and len(lines) > 1 and lines[1].strip() == strings["status_line"])
    run_pattern = CONTRACT["template_pattern"](strings["run_line"],
                                               {"model": r"(.+?)", "effort": r"(\S+)"})
    m = re.match(run_pattern, lines[2].strip()) if lang and len(lines) > 2 else None
    r["run_line"] = {"model": m.group(1), "effort": m.group(2)} if m else None
    heads = [(i, l) for i, l in enumerate(lines) if l.startswith("## ")]
    cands = []
    for k, (i, l) in enumerate(heads):
        title = l[3:].strip()
        if section_kind(title, strings):
            r["auxiliary_sections"].append(title)
            continue
        if " — " not in title:
            r.setdefault("other_sections", []).append(title)
            continue
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        body = "\n".join(lines[i + 1:end])
        name, src = split_title(title)
        src = re.sub(r"^(?:Source|출처)\s*[:：]\s*", "", src.strip(), flags=re.I)
        has_label = any(re.search(r"^\s*[-*]\s*\**\s*" + patterns[key], body, re.M) for key in labels_map)
        has_citation = bool(re.search(r'\b(?:1[5-9]\d\d|20\d\d)\b|[「『*“"]', src))
        if not has_label and not has_citation and not re.match(r"(?:(?:Candidate|후보)\s*\d|\d+[.)])", name):
            r["other_sections"].append(title)
            continue
        unverified = (strings["unverified_title_marker"] in title
                      or strings["unverified_item_prefix"] in title)
        labels = {labels_map[key]: bool(re.search(r"^\s*[-*]\s*\**\s*" + patterns[key], body, re.M)) for key in labels_map}

        def label_value(key):
            match = re.search(
                r"^\s*[-*]\s*\**\s*" + patterns[key] + r"\**\s*[:：]?\**(.*?)"
                r"(?=^\s*[-*]\s*\**\s*" + all_labels + r"\**\s*[:：]|\Z)",
                body, re.M | re.S)
            return match.group(1).strip() if match else ""

        gb_text = label_value("scene")
        scene_na = bool(re.fullmatch(r"[.\s]*" + re.escape(strings["no_example_rule"])
                                    + r"[.\s]*", gb_text))
        proposal_text = label_value("proposal")
        proposal_value = proposal_text.replace("**", "").replace("__", "")
        proposal_rest = re.sub(r"[()（）.。]", "", proposal_value.replace(strings["already_met"], "")).strip()
        detected_groups = set(GROUP_RE.findall(body))
        cands.append({
            "name": name.strip(), "source": src.strip(), "unverified_flag": unverified,
            "dash_ok": " — " in title, "labels_ok": all(labels.values()),
            "missing_labels": [k2 for k2, v in labels.items() if not v],
            "ledger_scene_chars": len(gb_text),
            "ledger_scene": "n/a" if scene_na else len(gb_text) >= 40,
            "already_met": strings["already_met"] in body,
            "already_met_full": strings["already_met"] in proposal_text and len(proposal_rest) < 40,
            "groups": sorted(detected_groups if groups is None else detected_groups & groups),
            "unknown_groups": sorted(detected_groups - groups) if groups is not None else [],
        })
    r["candidates"] = len(cands)
    r["count_in_range"] = 3 <= len(cands) <= 6
    r["no_candidates_declared"] = strings["no_candidates"] in text
    r["title_dash_ok"] = all(c["dash_ok"] for c in cands)
    r["sections_ok"] = not r["other_sections"]
    r["labels_all_ok"] = all(c["labels_ok"] for c in cands)
    r["ledger_scene_present"] = sum(c["ledger_scene"] is True for c in cands)
    r["scene_na"] = sum(c["ledger_scene"] == "n/a" for c in cands)
    r["unverified_title_flags"] = sum(1 for c in cands if c["unverified_flag"])
    r["unverified_ratio"] = round(r["unverified_title_flags"] / len(cands), 3) if cands else None
    r["already_met"] = sum(1 for c in cands if c["already_met"])
    r["already_met_full"] = sum(1 for c in cands if c["already_met_full"])
    r["groups_touched"] = sorted({g for c in cands for g in c["groups"]})
    r["groups_validated"] = groups is not None
    r["unknown_groups"] = sorted({g for c in cands for g in c["unknown_groups"]})
    r["groups_ok"] = not r["unknown_groups"] if groups is not None else None
    r["groups_only_1_1_7x"] = all(g.startswith(("1-1", "7-")) for g in r["groups_touched"]) if r["groups_touched"] else None
    mi = [i for i, l in enumerate(lines) if l.strip() == "## " + strings["sections"]["unverified"]]
    mi_end = next((i for i, _ in heads if mi and i > mi[0]), len(lines))
    r["unverified_section"] = bool(mi)
    r["unverified_items"] = len([l for l in lines[mi[0] + 1:mi_end] if l.strip().startswith(("-", "*")) and strings["unverified_item_prefix"] in l]) if mi else 0
    r["format_ok"] = all([r["title_ok"], r["status_ok"], r["count_in_range"] or r["no_candidates_declared"],
                          r["title_dash_ok"], r["labels_all_ok"], r["unverified_section"], r["sections_ok"]])
    r["items"] = cands
    return r


def scene_cell(present, candidates, scene_na, lang="en"):
    no_rule = STRINGS[lang]["no_example_rule"]
    if scene_na and scene_na == candidates:
        return no_rule
    value = f"{present}/{candidates - scene_na}"
    return value + f" ({no_rule}: {scene_na})" if scene_na else value


def table(rows, lang="en"):
    heads = (["보고", "형식 통과", "후보 수", "장면 유무", "미확인 표시", "미확인 절", "이미 충족(전부)", "그룹 수", "절 제목 이탈", "목록 밖 그룹"]
             if lang == "ko" else ["Report", "Format", "Candidates", "Scenes", "Unverified flags", "Unverified section",
                                   "Already met (fully/any)", "Groups", "Other sections", "Unknown groups"])
    passed, failed = ("통과", "실패") if lang == "ko" else ("pass", "fail")
    yes, no, unvalidated = ("있음", "없음", "검증 안 함") if lang == "ko" else ("yes", "none", "not validated")
    out = ["| " + " | ".join(heads) + " |", "|" + "---|" * len(heads)]
    for r in rows:
        verdict = passed if r["format_ok"] else failed
        if r.get("reason"):
            verdict += f' ({r["reason"]})'
        cells = [r["file"], verdict, r["candidates"],
                 scene_cell(r["ledger_scene_present"], r["candidates"], r["scene_na"], lang), r["unverified_title_flags"],
                 (yes if r["unverified_section"] else no) + f' ({r["unverified_items"]})',
                 f'{r["already_met_full"]}/{r["already_met"]}', len(r["groups_touched"]), "; ".join(r["other_sections"]) or no,
                 ", ".join(r["unknown_groups"]) or (no if r["groups_validated"] else unvalidated)]
        out.append("| " + " | ".join(str(x).replace("|", r"\|") for x in cells) + " |")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="+", type=pathlib.Path)
    parser.add_argument("--format", choices=("json", "table"), default="json")
    parser.add_argument("--groups", help="Group map file or comma-separated IDs; omit to skip validation")
    parser.add_argument("--lang-table", choices=("en", "ko"), default="en", help="Table language (default: en)")
    args = parser.parse_args()
    try:
        groups = parse_groups(args.groups) if args.groups is not None else None
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Error: --groups: {exc}", file=sys.stderr)
        return 1
    rows, failed = [], False
    for path in args.reports:
        try:
            rows.append(score(path, groups))
        except (OSError, UnicodeError) as exc:
            print(f"Error: {path}: {exc}", file=sys.stderr)
            failed = True
    print(table(rows, args.lang_table) if args.format == "table" else "\n".join(json.dumps(r, ensure_ascii=False) for r in rows))
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
