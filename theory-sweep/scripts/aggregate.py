#!/usr/bin/env python3
"""Optionally combine report scores, bibliography checks, and judge results."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import runpy
import statistics
import sys

SCORE = runpy.run_path(str(Path(__file__).with_name("score_format.py")))
BIB_KEYS = ("match", "partial", "nohit", "no_title", "not_a_citation", "standard_doc")
FINAL_KEYS = ("exists", "bib_error", "content_mismatch", "undetermined", "not_found", "pending")


def discover(specs):
    reports = {}
    for spec in specs:
        model, separator, raw_path = spec.partition("=")
        root = Path(raw_path if separator else spec)
        if not root.is_dir():
            raise ValueError(f"보고 폴더 없음: {root}")
        for path in sorted(root.rglob("*.md")):
            with path.open(encoding="utf-8") as stream:
                first = stream.readline()
            if not first.startswith("# ") or not any(
                    strings["title_marker"] in first for strings in SCORE["STRINGS"].values()):
                continue
            key = (model if separator else path.parent.name, path.stem)
            if key in reports and reports[key].resolve() != path.resolve():
                raise ValueError(f"모델/분야 중복: {key}: {reports[key]}, {path}")
            reports[key] = path
    if not reports:
        raise ValueError("분야 보고를 찾지 못했습니다")
    return reports


def load(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return json.loads(text)


def index(folder, reviewer=False):
    results = {}
    if folder is None:
        return results
    if not folder.is_dir():
        raise ValueError(f"결과 폴더 없음: {folder}")
    for path in sorted(folder.rglob("*")):
        if path.suffix not in (".json", ".jsonl") or "--" not in path.stem:
            continue
        model, slug = path.stem.split("--", 1)
        who = str(path.parent.relative_to(folder)) if path.parent != folder else "default"
        key = (model, slug, who) if reviewer else (model, slug)
        if key in results:
            raise ValueError(f"결과 중복: {key}")
        data = load(path)
        if reviewer:
            if not isinstance(data, dict) or not isinstance(data.get("candidates"), list):
                raise ValueError(f"판정기 candidates 배열 없음: {path}")
        elif not isinstance(data, (dict, list)):
            raise ValueError(f"객체/배열이 아닌 결과: {path}")
        results[key] = data
    return results


def items(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("items", [data] if "source" in data else [])
    return []


def mean(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return round(statistics.mean(values), 2) if values else None


def judge_summary(data):
    candidates = data["candidates"]
    return {"n": len(candidates), "connection": mean([c.get("connection") for c in candidates]),
            "ledger": mean([c.get("ledger") for c in candidates]),
            "one": sum(c.get("connection") == 1 for c in candidates),
            "quote": sum(c.get("quote") in ("present", "있음", "yes", True) for c in candidates),
            "analogy": data.get("analogy_only"), "unknown": data.get("unknown_groups")}


def agreement(left, right):
    # Match candidates by name, not list position.
    def keyed(data):
        rows = data["candidates"]
        mapped = {r.get("name"): r.get("connection") for r in rows}
        return mapped if len(mapped) == len(rows) and None not in mapped else {}
    a, b = keyed(left), keyed(right)
    if not a or set(a) != set(b) or any(not isinstance(v, (int, float)) for v in [*a.values(), *b.values()]):
        return None
    return {"n": len(a), "exact": sum(a[k] == b[k] for k in a) / len(a),
            "within1": sum(abs(a[k] - b[k]) <= 1 for k in a) / len(a)}


def build_row(key, path, bib, recheck, judges):
    model, slug = key
    score = SCORE["score"](path)
    sources = items(bib.get(key))
    by_source = {r.get("source", "").strip(): r for r in items(recheck.get(key))}
    final, bad, unflagged = Counter(), 0, 0
    for row in sources:
        source = row.get("source", "").strip()
        checked = by_source.get(source, {}).get("verdict")
        verdict = checked or ("exists" if row.get("verdict") == "match" else "pending")
        final[verdict] += 1
        if not row.get("flagged_unverified", False):
            unflagged += 1
            bad += verdict in ("bib_error", "content_mismatch", "not_found")
    selected = {who: data for (m, s, who), data in judges.items() if (m, s) == key}
    agreements = []
    names = sorted(selected)
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            same = agreement(selected[first], selected[second])
            if same:
                agreements.append((first + "/" + second, same))
    return {"model": model, "slug": slug, "score": score, "bib_present": key in bib,
            "bib_n": len(sources), "bib": Counter(r.get("verdict", "unknown") for r in sources),
            "network_errors": sum(bool(r.get("error")) for r in sources), "final": final,
            "bad": bad, "unflagged": unflagged,
            "judges": {who: judge_summary(data) for who, data in selected.items()},
            "agreements": agreements}


def table(headers, rows):
    def cell(value):
        return str(value).replace("|", r"\|").replace("\n", " ")
    return "\n".join(["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)] +
                     ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows])


def tallies(counts, keys):
    return "/".join(str(counts[k]) for k in keys)


def judge_cell(judges):
    return "; ".join(f"{who}: 연결={j['connection']}, 장면={j['ledger']}, 연결1점={j['one']}, "
                     f"인용={j['quote']}/{j['n']}, 비유={j['analogy']}, 그룹미상={j['unknown']}"
                     for who, j in sorted(judges.items())) or "-"


def document(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["model"]].append(row)
    summary = []
    for model, selected in sorted(grouped.items()):
        candidates = sum(r["score"]["candidates"] for r in selected)
        scene_present = sum(r["score"]["ledger_scene_present"] for r in selected)
        scene_na = sum(r["score"]["scene_na"] for r in selected)
        bib, final = Counter(), Counter()
        for row in selected:
            bib.update(row["bib"])
            final.update(row["final"])
        summary.append([model, len(selected), candidates,
                        sum(r["score"]["format_ok"] for r in selected),
                        SCORE["scene_cell"](scene_present, candidates, scene_na) if scene_na else scene_present,
                        sum(r["score"]["unverified_title_flags"] for r in selected),
                        sum(r["score"]["unverified_items"] for r in selected),
                        sum(r["score"]["already_met"] for r in selected),
                        f"{sum(r['bib_present'] for r in selected)}/{len(selected)}",
                        tallies(bib, BIB_KEYS), tallies(final, FINAL_KEYS),
                        sum(r["network_errors"] for r in selected),
                        sum(r["bad"] for r in selected) if bib else "-"])
    out = ["# 모델 시험 비교표 (자동 집계)",
           "지위: 기계 채점·서지 1차 대조·판정기 참고값. 채택·효과 입증 아님.", "",
           "서지 열 순서: " + "/".join(BIB_KEYS) + ".",
           "재확인 열 순서: " + "/".join(FINAL_KEYS) + ".",
           "미수집 자료는 0건 확인이 아니다. 서지 수집 범위와 pending을 함께 읽는다.",
           "판정 일치는 후보 이름 집합이 정확히 같을 때만 계산한다. '-'는 미수집 또는 비교 불가다.", "",
           "## 모델별 합산", "",
           table(["모델", "보고", "후보", "형식 통과", "②장면 유무", "미확인 표시", "미확인 절 항목", "이미 충족",
                  "서지 수집 보고", "서지 분류", "재확인 분류", "네트워크 오류", "표시 없이 오류"], summary),
           "", "## 모델별 판정 합산", ""]
    judge_rows = []
    for model, selected in sorted(grouped.items()):
        whos = sorted({who for row in selected for who in row["judges"]})
        for who in whos:
            js = [r["judges"][who] for r in selected if who in r["judges"]]
            judge_rows.append([model, who, f"{len(js)}/{len(selected)}", mean([j["connection"] for j in js]),
                               mean([j["ledger"] for j in js]), sum(j["one"] for j in js),
                               f"{sum(j['quote'] for j in js)}/{sum(j['n'] for j in js)}"])
    out.append(table(["모델", "판정기", "판정 수집 보고", "연결 평균(보고별)", "장면 평균(보고별)", "연결1점", "인용 있음"], judge_rows))
    for slug in sorted({r["slug"] for r in rows}):
        detail = []
        for row in [r for r in rows if r["slug"] == slug]:
            s = row["score"]
            detail.append([row["model"], s["lines"], s["candidates"], "통과" if s["format_ok"] else "실패",
                           SCORE["scene_cell"](s["ledger_scene_present"], s["candidates"], s["scene_na"]), s["unverified_title_flags"],
                           s["unverified_items"], s["already_met"], len(s["groups_touched"]),
                           "; ".join(s["other_sections"]) or "없음",
                           f"{row['bib_n']}/{s['candidates']}",
                           tallies(row["bib"], BIB_KEYS) if row["bib_present"] else "-",
                           tallies(row["final"], FINAL_KEYS) if row["bib_present"] else "-",
                           f"{row['bad']}/{row['unflagged']}" if row["bib_present"] else "-",
                           judge_cell(row["judges"]), "; ".join(
                               f"{name}: {ag['exact']:.2f}/{ag['within1']:.2f} (n={ag['n']})"
                               for name, ag in row["agreements"]) or "-"])
        out.extend(["", f"## {slug}", "", table(
            ["모델", "행", "후보", "형식", "②장면 유무", "미확인 표시", "미확인 절", "이미 충족", "그룹",
             "절 제목 이탈", "서지 수집/후보", "서지 분류", "재확인 분류", "표시 없이 오류/미표시", "판정기", "일치/±1"], detail)])
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", nargs="+", required=True)
    for option in ("judge", "bib", "recheck"):
        parser.add_argument("--" + option, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        reports = discover(args.reports)
        if args.out.resolve() in {p.resolve() for p in reports.values()}:
            raise ValueError("보고 자체를 출력으로 덮어쓸 수 없습니다")
        judges, bib, recheck = index(args.judge, True), index(args.bib), index(args.recheck)
        rows = [build_row(key, path, bib, recheck, judges) for key, path in sorted(reports.items())]
        md = document(rows)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md, encoding="utf-8")
        print(md, end="")
        return 0
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
