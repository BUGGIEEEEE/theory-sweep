# Field report format

This is the fixed format of one investigator report. The investigator prompt (`field-prompt.md`) gives the investigator the same rules. Read this file in the quality check, source check and synthesis steps to check a rule and its reason.

Fixed strings appear below as `{s.<key>}` placeholders. Their English and Korean values are in the table in §9, so a person can read a report in either language. The scripts accept either language and detect it from the status line or the title.

Each rule carries a "why". The reason is one of three. **Counts**: `scripts/count.py` totals. **Machine check**: `scripts/score_format.py` and `scripts/bib_check.py`. **Judge**: `judge-rubric.md`.

## 1. First three lines

```
# <field> — {s.title_suffix}
{s.status_line}
{s.run_line}
```

- Line 1 contains `{s.title_marker}`. Why: counts. `count.py` treats a file as a report only if its first line contains this marker.
- Line 2 is never changed by even one character. Why: machine check. The scorer matches it as an exact string, and it also tells the scripts the report language. It keeps the result status identical across all reports.
- Line 3 records the model and effort. Why: machine check. When the same field runs on several models, the report alone shows its run conditions.

One or two lines such as "ranges read" may follow the first three lines. Do not use a `## ` heading there.

## 2. Candidate title line

```
{s.candidate_heading}
```

- Always give the work title. Italicize books and standards with `*asterisks*`; put papers and chapters in `"double quotes"` (「」 and 『』 are also accepted). Why: machine check. `bib_check.py` finds the work title by these marks; without them it classifies the line as `no_title` and cannot check it automatically.
- Never use the form that has only author and year in parentheses, such as `(Lakatos, 1970)`. Why: machine check. In the model trial this form made 22 automatic citation checks fail (`evidence.md` §2).
- Use " — " exactly once, between candidate name and source. Never inside the candidate name. Why: machine check. The scorer treats a `## ` line with " — " as a candidate and splits at the first " — ".
- Do not use bare numbered names such as "Candidate 1". Why: judge. The synthesis and judge records refer to candidates by name.
- For standards and institutional documents, give the body, year, document number and title. Example: `IAASB 2009, *ISA 530 Audit Sampling*`. Why: machine check. Standards are classified `standard_doc`, skip the automatic check and go to the recheck.

## 3. Six candidate items

Write them in this order without renaming. Why: machine check. The scorer finds the items by their label strings. A renamed item counts as missing.

| Item | Content |
|---|---|
| `- {s.labels.meaning}:` | Two or three sentences |
| `- {s.labels.problem}:` | Group number and a quoted design sentence (file and line). Why: the judge checks the quotation inside the given line ranges |
| `- {s.labels.proposal}:` | What to change or add. Follow the "already met" rule in §4 |
| `- {s.labels.scene}:` | Scene per the common example rule. Without a rule, `{s.no_example_rule}` |
| `- {s.labels.limits}:` | Assumptions that break when moved to AI. If the effect is unproven, say so |
| `- {s.labels.status}:` | `{s.status_value}` |

## 4. "Already met" marking

- Content the design already holds must be marked `{s.already_met}`. If the design holds only part, write `{s.already_met}: <the part it holds>` first and then the addition separately.
- Why: judge. In the model trial, the common reason both judges gave a connection score of 2 (loose) was "the design already holds this, but the report did not say already met" (`evidence.md` §2). Also counts: `count.py` counts candidates whose body contains the marker.

## 5. Candidate count

- 3–6. If there are none, write `{s.no_candidates}` with a reason (0 candidates).
- Why: counts. Outside the range the scorer reports a format failure. More candidates is not better.

## 6. Fixed section titles

| Section title | Written by | Required |
|---|---|---|
| `## {s.sections.not_proposed}` | Investigator | Optional |
| `## {s.sections.unverified}` | Investigator | Required; the last section the investigator writes |
| `## {s.sections.recheck} (YYYY-MM-DD)` | Parent session in step 3 (source check) | Only after a recheck |

- The parent session appends `## {s.sections.recheck} (YYYY-MM-DD)` after `## {s.sections.unverified}` in step 3. Then `## {s.sections.unverified}` no longer needs to be the last section.
- Create no `## ` section other than these three. Why: machine check and counts. In an earlier 52-report run, the "excluded" section title was spelled more than 20 different ways and could not be collected by machine (`evidence.md` §5). The scorer reports other titles as `other_sections` and flags a format deviation.

## 7. Unverified markers

- Title line: if the investigator could not verify a source directly, the title line ends with `{s.unverified_title_marker}`. Why: counts. `count.py` and the scorer count the marker in title lines, and pairing it with the citation check gives "errors written without a marker".
- Unverified section: one item per line, `{s.unverified_item_format}`. Why: counts. The scorer counts list lines that start with `{s.unverified_item_prefix}`. In the model trial, a model that left this section nearly empty was judged to show no restraint signal (`evidence.md` §2).
- If nothing is unverified, the section holds `{s.nothing_unverified}` and one line of reason, without `{s.unverified_item_prefix}`.
- Recheck marker: after step 3, the parent session keeps the original wording and appends `{s.recheck_marker}` to the end of the title line, with the date and verdict filled in. The original `## {s.sections.unverified}` section stays as the record of the time of writing. Why: counts. `count.py` counts recheck markers. Keeping the original marking separates the investigator's restraint from the recheck result.
- Synthesis markers: the synthesis report (`synthesis-template.md`) adds two symbols after candidate names. Why: counts. Synthesis §4 counts the investigator's own flags and the recheck verdicts separately.

| Symbol | Candidates | Decided by |
|---|---|---|
| † | Title line carries `{s.unverified_title_marker}` | Investigator's own flag |
| ‡ | Step 3 recheck verdict is `bib_error`, `content_mismatch` or `not_found` | Rechecker's verdict |

- A recheck verdict of `undetermined` adds no ‡ and keeps †. † is the investigator's flag, so no recheck result removes it. If both apply, write †‡.

## 8. Chat reply

The investigator's chat reply ends with `{s.chat_end.investigator}`. Why: the parent session can tell a normal finish from the completion notice alone. Judges end with `{s.chat_end.judge}`, recheckers with `{s.chat_end.rechecker}`.

## 9. Fixed strings in English and Korean

Generated from `strings/en.json` and `strings/ko.json`. If the JSON files change, regenerate this table; the JSON files are the source of truth. Placeholders inside values (`{date}`, `{model}`, `{effort}`, `{verdict}`) are filled at render time or by the parent session.

| Placeholder | English | Korean |
|---|---|---|
| `{s.title_suffix}` | `Theory integration candidates (theory sweep, {date})` | `이론 접목 후보 (theory sweep, {date})` |
| `{s.title_marker}` | `Theory integration candidates` | `이론 접목 후보` |
| `{s.status_line}` | `Status: AI survey and comparison proposal. Not adopted; effectiveness not proven.` | `지위: AI 조사·비교 제안. 채택·효과 입증 아님.` |
| `{s.run_line}` | `Run: model {model}, reasoning {effort}` | `실행 조건: 모델 {model}, 추론 {effort}` |
| `{s.candidate_heading}` | `## <candidate name> — <author> <year>, <work title>` | `## <후보 이름> — <저자> <연도>, <문헌 제목>` |
| `{s.labels.meaning}` | `Plain meaning` | `쉬운 뜻` |
| `{s.labels.problem}` | `Which problem it touches` | `이 도구의 어느 문제에 닿는가` |
| `{s.labels.proposal}` | `Integration candidate` | `접목 후보` |
| `{s.labels.scene}` | `Example scene` | `예시 장면` |
| `{s.labels.limits}` | `Counterexamples and limits` | `반례·한계` |
| `{s.labels.status}` | `Status` | `지위` |
| `{s.status_value}` | `Proposal. Not adopted; effectiveness not proven.` | `제안. 채택·효과 입증 아님.` |
| `{s.already_met}` | `already met` | `이미 충족` |
| `{s.no_candidates}` | `No integration candidates` | `접목 후보 없음` |
| `{s.no_example_rule}` | `No example rule` | `예시 규칙 없음` |
| `{s.sections.not_proposed}` | `Reviewed but not proposed` | `검토했으나 올리지 않은 것` |
| `{s.sections.unverified}` | `Unverified` | `미확인` |
| `{s.sections.recheck}` | `Source recheck` | `출처 재확인` |
| `{s.unverified_title_marker}` | ` · Unverified: source unverified` (leading space) | ` · 미확인: 출처 미확인` (leading space) |
| `{s.unverified_item_prefix}` | `Unverified:` | `미확인:` |
| `{s.unverified_item_format}` | `- Unverified: <what> — reason: <why>` | `- 미확인: <내용> — 이유: <이유>` |
| `{s.nothing_unverified}` | `Nothing unverified` | `확인하지 못한 것 없음` |
| `{s.recheck_marker}` | `⟨recheck {date}: {verdict}⟩` | `⟨재확인 {date}: {verdict}⟩` |
| `{s.chat_end.investigator}` | `Review done` | `검토 끝` |
| `{s.chat_end.judge}` | `Judging done` | `판정 끝` |
| `{s.chat_end.rechecker}` | `Recheck done` | `재확인 끝` |
| `{s.synthesis_title}` | `Theory sweep synthesis — {date}` | `학문 분야별 이론 접목 검토 통합 (theory sweep 00-synthesis) — {date}` |
| `{s.synthesis_metrics.fields}` | `Fields` | `분야 수` |
| `{s.synthesis_metrics.reports}` | `Reports` | `보고 수` |
| `{s.synthesis_metrics.candidates}` | `Candidates` | `후보 수` |
| `{s.synthesis_metrics.already_met_any}` | `Already met (any)` | `이미 충족 수` |
| `{s.synthesis_metrics.already_met_full}` | `Already met (fully)` | `전부 충족 수` |
| `{s.synthesis_metrics.unverified}` | `Unverified (title line)` | `미확인 수` |

`ko.json` also lists a legacy alias for the scene label under `label_aliases`. The scorer accepts it so older Korean reports still score; new reports use the main label.
