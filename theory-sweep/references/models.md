# Models by role

In step 0, use this file when asking the user for the investigator, synthesis and judge models.

**Read this first.** The model names here come from one evaluation on 2026-10-17. Model versions, aliases and prices change. Treat the names as examples of what passed or failed, not as a current recommendation. Re-evaluate with the models you actually have (§3). All numbers behind this file are in [evidence.md](evidence.md).

## 1. Roles

| Role | Step | Default guidance | Basis |
|---|---|---|---|
| Investigator | 1 | A model that passed your own trial on format, bibliography, restraint and connection (§2). Reasoning effort high | evidence.md §2 |
| Synthesizer | 4 | The skill does not choose. The user picks in step 0. Prefer a top-tier model, ideally from a different family than the investigators | evidence.md §3. Untested in this procedure |
| Checker | 2 | Scripts first (`score_format.py`, `count.py`). Hand only sentence matching to a model; a small model may do | evidence.md §3 |
| Judge | 2 | A model family different from the investigator's. Never change it within a run. Do not use a small model | evidence.md §3 |
| Rechecker | 3 | A model with web search. Prefer a family different from the investigator's | evidence.md §2 |

## 2. Investigator: what the 2026-10-17 evaluation showed

Setup: several models, the same prompt and reading, a small set of fields, one run each. Setup details and all numbers: evidence.md §2.

| Model (as named in the evaluation) | Rating | Short reason |
|---|---|---|
| Claude Opus 5.5 | Suitable | Format, bibliography, restraint and connection all at or above the baseline |
| gpt-6.1-sol | Suitable | No bibliography errors; separated "already met" parts most often. Long reports and slow. Use `adapter-codex.md` |
| Claude Sonnet 5.5 | Conditional | Format and restraint good. Connection scores split between judges. Use two judge families and run a second time first to see variance |
| Claude Haiku 5.5 | Not suitable as investigator | Format deviations; titles missing from citations broke the automatic check; one content mismatch. Still a candidate for the checker role |
| gpt-6-luna | Not suitable as investigator | Almost no unverified markers or sections, lowest connection, fewest candidates. Use only for search or summary |

These ratings are model judgment from one small trial. They are not verified.

Pattern worth keeping even as model names change:
- Top-tier models did best on connection and restraint. Mid-tier was usable but less stable across judges. Small models broke format or skipped restraint.
- Bibliography accuracy differed little between models once reprint-year mismatches were rechecked. Restraint (marking what was not verified) differed a lot.
- Format compliance did not predict citation accuracy. Score them separately (evidence.md §3).

## 3. Re-evaluate with your own models

Do this before a large run, or whenever your model set changes.

1. Pick 5–7 fields from `field-list.md`. Mix fields rich in literature (e.g. cognitive psychology) with sparse ones (e.g. music).
2. Run each candidate model once per field with the same rendered prompt, the same reading and the same effort. Put each model's reports in its own folder.
3. Score format with `scripts/score_format.py`.
4. Check citations with `scripts/bib_check.py`, then recheck non-matches with `recheck-prompt.md`.
5. Judge connection with `judge-rubric.md`. Use judges from two families. Let both judges see the same one field to measure agreement.
6. Combine with `scripts/aggregate.py`.
7. Rate each model on format pass, bibliography errors, errors written without an unverified marker, connection mean, and judge agreement. Record the exact model version and effort.
8. If a model's results split between judges, run it a second time before deciding.

## 4. Role guidance from agent-tool practice

These come from a survey of open-source agent tools' role-to-model assignments (evidence.md §3). They describe practice, not measured effect in this procedure.

- Judge (review): the surveyed tools do not move review to small models. One tool's documentation says small models "drift and rubber-stamp". Another says the reviewer should be a different family from the writer.
- Checker: several tools give pure matching work to cheap models. Count with scripts first and give only sentence matching to a small model.
- Investigator: no surveyed tool used a small model for work that draws knowledge from the model's own memory.

## 5. Unverified

- Unverified: run-to-run variance for the same model and field. Reason: the evaluation ran each pair only once.
- Unverified: judge bias. Reason: only two judge families were used, and each saw the other family's reports in one field only.
- Unverified: a small model in the checker role. Reason: not tested in that role.
- Unverified: quality differences between synthesis models. Reason: synthesis was not compared across models.
- Unverified: a small model after the prompt made work titles mandatory. Reason: not re-tested.
- Unverified: token counts for Claude models. Reason: token counts were available only in Codex logs.
