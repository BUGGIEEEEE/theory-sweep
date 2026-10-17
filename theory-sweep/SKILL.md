---
name: theory-sweep
description: Split a design or planning document across per-discipline LLM investigators, collect theory-integration candidates with sources, merge them along two axes (by design group and by cross-cutting problem), and check format, bibliography and connection with scripts and a judge model (theory sweep). Use when the user asks for a "theory sweep", wants a design reviewed "from many disciplines", or wants theories from other fields that the design could borrow, and a design document plus its group or problem map exists. Works in Claude Code and Codex. 분야별 이론 접목 조사, theory sweep, 여러 학문 관점의 설계 검토 요청에도 쓴다.
---

# Theory Sweep

One investigator per discipline reads the design document and reports theory-integration candidates. One model merges the reports along two axes. Scripts and a judge model check format, bibliography and connection.

Paths to `scripts/` and `references/` are relative to this skill folder. If the working directory differs, use absolute paths.

The status line is fixed. Take it from `status_line` in `references/strings/<lang>.json`. Put it unchanged on line 2 of every field report, on line 2 of the synthesis, and in the first paragraph of synthesis §1. Never reword it.

## Language

- `lang` selects `references/strings/en.json` or `references/strings/ko.json`. It sets every fixed string in the reports (title marker, status line, run line, labels, section titles, markers, chat endings, synthesis metric rows).
- Templates contain `{s.<key>}` placeholders. `scripts/render_prompt.py --lang <lang>` fills them. Never type a fixed string into a template by hand.
- The scoring scripts detect each report's language from its status line or title. One output folder may mix languages, but keep one language per run when possible.
- These docs are in English. `lang: ko` gives Korean reports; the prompts stay English and tell the investigator to write in Korean.
- [references/report-format.md](references/report-format.md) shows every fixed string in English and Korean side by side.

## Inputs

Fix all of these in step 0. Ask the user for anything missing.

| Input | Default | Notes |
|---|---|---|
| Target documents and line ranges | none (required) | Files and line ranges investigators read. Becomes `{read_list}` |
| Problem map | none (required) | All group (problem) numbers and titles of the design. Becomes `{group_map}` |
| Field list | `references/field-list.md` | 52 representative fields. A copy may be edited |
| Common example rule | none | Becomes `{example_rule}`. If none, set `example_rule` to `{s.no_example_rule}` so the scene item reads the fixed "no example rule" string |
| Output folder | none (required) | Field reports, synthesis, run log |
| Forbidden folders | none | Folders investigators must not open (earlier runs' reports, etc.). Becomes `{forbidden_dirs}` as a full sentence |
| `lang` | `en` | `en` or `ko`. Report language and fixed strings |
| Batch size | 5–8 | Investigators launched at once |
| Candidates per field | 3–6 | Range stated in the prompt |
| Investigator model and effort | user choice | Propose from [references/models.md](references/models.md) |
| Synthesis model | user choice | The skill does not pick one |
| Judge model | user choice | Different model family from the investigator |
| axis | `field` | `field` (one investigator per field) or `problem` (one per problem). `problem` is unverified |
| `OPENALEX_API_KEY` | unset (optional) | Environment variable only. `scripts/bib_check.py` skips OpenAlex without it and uses Crossref alone. Never write the key into any file, prompt or log |

Unverified: cost and quality of `axis=problem`. Reason: never compared against field-first. If the user picks `problem`, rewrite the first paragraph of the prompt per problem and tell the user there is no tested template.

## Adapter selection

How investigators, judges and recheckers are launched depends on the tool. Read the adapter for the current tool before steps 1, 2 and 3.

- Claude Code: [references/adapter-claude.md](references/adapter-claude.md)
- Codex: [references/adapter-codex.md](references/adapter-codex.md)
- Optional, for sessions that need mid-run instructions: [references/adapter-interactive-pane.md](references/adapter-interactive-pane.md)
- Other tools: add an adapter to `references/` with the same four headings (launch, model selection, collecting files, failure handling), then use it.

## Steps

```
0 prepare -> 1 investigate (batch) -> 2 quality check (stop after first batch) -> repeat 1-2
          -> 3 source check -> 4 synthesize -> 5 pre-review -> 6 register and hand off
```

Keep the run log in one file, `<output>/00-run-log.md`. Record with dates: batch composition, prompt version, per-field extra clauses, failures and reruns, check results, user decisions.

### 0. Prepare

1. Check the inputs. Open the target documents and confirm the line ranges exist.
2. Check the field list for completeness. Follow "Completeness check" in `references/field-list.md` and confirm missing fields per group once with the user. Tell the user the list is a representative selection, not all disciplines.
3. If the "first question" column does not fit the target, write an adapted copy outside the output folder. For rows of kind "precedent overlap", append the actual precedent.
4. Present the expected size. Reports = number of fields. Batches = fields ÷ batch size, rounded up. Estimate cost per investigator as about 300 lines read plus about 100 lines written (estimate, not measured; see `references/evidence.md`). Count the human reading load as a cost too.
5. Ask the user for the investigator model and effort, the synthesis model and the judge model. Show `references/models.md` as the basis.
6. Get user approval. Launch no investigator before approval.

Done when: every input row is fixed, the field list is final, the three models are user-chosen, and the approval is recorded.

### 1. Investigate

1. Per batch, launch one investigator per field. The prompt is `references/field-prompt.md` rendered by `scripts/render_prompt.py --lang <lang>`. Launch as the adapter says.
2. Each investigator writes one report file only. It does not open other fields' reports or forbidden folders. The prompt states this.
3. Launch the next batch only after the step 2 check.

Done when: every field in the batch has a report file (or a recorded failure) and nothing outside the output files changed.

### 2. Quality check

Always stop and check after the first batch. Check later batches the same way.

1. Run `python3 -I scripts/score_format.py <reports> --format table`. Pass only field reports. Exclude files starting with `00-`, `01-`, `02-` (run log, synthesis, notes, handoff). Add `--groups <map file or IDs>` to validate group numbers.
2. Look at four things.
   - **Format**: format pass, stray section titles (`other_sections`), candidate count range. Rules: `references/report-format.md`.
   - **Example scene**: a scene exists and shows a behavior difference caused by that candidate.
   - **Source assertions**: suspicious citations written without the unverified marker. Pass suspects to step 3.
   - **Forced candidates**: candidates not tied to any design sentence, or mere analogies. For a judge, render `references/judge-rubric.md` and run it on a model family different from the investigator's.
3. Report results to the user briefly and ask whether to continue with the next batch.
4. Change the prompt only per batch. Record whether the common template changed or only per-field extra clauses were added. Apply the new version from the next batch. Never rerun finished batches.

Done when: the check table, the prompt version and the user's reply about the next batch are recorded.

### 3. Source check

1. Run the machine check: `python3 -I scripts/bib_check.py <reports> --out <scratch>/bib.jsonl`. Network errors stay in each row's `error` field.
2. Keep only rows whose verdict is not `match`.
   ```
   python3 -I -c 'import json,sys;[print(l,end="") for l in open(sys.argv[1]) if json.loads(l)["verdict"]!="match"]' bib.jsonl > recheck.jsonl
   ```
3. Render `references/recheck-prompt.md` and give it to recheckers. Verdicts fall in five classes: `exists`, `bib_error`, `content_mismatch`, `undetermined`, `not_found`.
4. Apply the results to the reports. Keep the original wording and the unverified section. Append `recheck_marker` (from the strings file, with date and verdict filled) to the end of the title line. Add a final section titled `sections.recheck` plus ` (YYYY-MM-DD)`.

Done when: the machine check file, the recheck result files, the per-report markers and sections, and per-class counts exist.

### 4. Synthesize

1. Run `python3 -I scripts/count.py <output>` for fields, reports, candidates, already met (any), already met (fully) and unverified. It counts only files whose first line contains `title_marker`, so a folder argument is fine.
2. Render `references/synthesis-template.md` with `--lang <lang>`. The synthesis model fills the skeleton into `<output>/00-synthesis.md`. Axis (a) is per group: candidates / already met / counterexamples. Axis (b) is cross-field clusters per problem.
3. Fix the header table until `python3 -I scripts/count.py <output> --expect <output>/00-synthesis.md` reports a match.
4. Do one critical review. Check for missing fields, re-rate the top candidates on three axes (machine-checkable part, open issue it feeds, added burden), and remove overstatements such as "independent convergence". Record the result in §1.1 and §1.2. If missing fields are investigated, run steps 1–3 for those fields only.

Done when: the count check matches, §1–§5 and Appendix A are filled, and the critical review is recorded.

### 5. Pre-review

1. For each top candidate in synthesis §1, write two lines.
   - Added burden: who does what extra, and when.
   - Check method: how to compare before and after adoption in one common example scene. Without a common example rule, use a concrete situation, example or usage scenario from the target document. If there is none, write "no check scene" and recommend deferral.
2. If either line cannot be written, make "defer" the recommended option.
3. Ask the user per candidate: adoption candidate / defer / exclude. The model does not decide. Write that "adoption candidate" means it goes on the review agenda, not that the design adopts it.
4. Record per candidate in `<output>/01-review-notes.md`: existing contract, proposal, added burden, check method, user decision with a quote, possible place of change, remaining checks.

Done when: every top candidate has both lines and a recorded user decision.

### 6. Register and hand off

1. Write the registration text in synthesis §5: anchor, per-file SHA-256 (`shasum -a 256 <file>`), counts. Record the synthesis file's own SHA-256 only in the registration row.
2. Add it to the user's source list only after user approval.
3. Write a handoff note for the parent session: output folder, counts, top candidates with pre-review decisions, remaining unverified items, next actions.
4. This skill runs no work-logging tool commands. If the session uses such a tool, tell it to record this run under its own rules.

Done when: registration text, SHA-256 table and handoff note exist.

## References

| File | When to read |
|---|---|
| [references/field-list.md](references/field-list.md) | Step 0 field selection and completeness check; step 1 rendering |
| [references/field-prompt.md](references/field-prompt.md) | Before rendering in step 1. Variables and extra-clause examples |
| [references/report-format.md](references/report-format.md) | Step 2 format check; step 3 markers. English and Korean strings side by side |
| [references/judge-rubric.md](references/judge-rubric.md) | Step 2 when a judge is used |
| [references/recheck-prompt.md](references/recheck-prompt.md) | Step 3 recheck |
| [references/synthesis-template.md](references/synthesis-template.md) | Step 4 synthesis; step 6 registration text |
| [references/models.md](references/models.md) | Step 0 model question |
| [references/evidence.md](references/evidence.md) | When a rule or model suggestion needs its evidence |
| [references/adapter-claude.md](references/adapter-claude.md) | Steps 1–3 in Claude Code |
| [references/adapter-codex.md](references/adapter-codex.md) | Steps 1–3 in Codex |
| [references/adapter-interactive-pane.md](references/adapter-interactive-pane.md) | Optional: investigators in an interactive terminal pane |

Run every script with `python3 -I`. Arguments follow each script's `--help`. Use `scripts/aggregate.py` only to compare several models on the same fields.

## Known limits

- Model suggestions rest on one evaluation: 7 fields × 1 run per model. Run-to-run variance was not measured. Re-evaluate with your own models (`references/models.md`).
- Judges are sensitive on forced-candidate scoring. Exact per-candidate agreement between two judges varied widely by report (see `references/evidence.md`). Treat judge scores as reference values; the user makes the final call.
- Standards and institutional documents (ISA, IEC, COSO, etc.) are missing from bibliographic databases, so the machine check cannot match them. They rely on the recheck.
- Repeated proposals across reports made by the same model, from the same reading and the same prompt, are not independent evidence.
- If the synthesis model shares a family with the investigator, family preference may leak into the ranking. Use a different family when possible, or state the overlap in §1.1.
- Group numbers and "already met" marks are the investigators' self-reports. Design content outside the ranges they read is not reflected.
- This procedure finds candidates. It does not prove their effect.
