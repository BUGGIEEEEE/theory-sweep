# Synthesis skeleton

Contents: writing rules · skeleton (header and run-result table · §1 conclusions with 1.1 three-axis re-rating and 1.2 issue table · §2 per-group axis · §3 per-problem axis · §4 unverified and recheck · §5 registration · Appendix A versions)

In step 4 (synthesize), render this file and give the body to the synthesis model, which fills it into `<output>/00-synthesis.md`. The section layout comes from the synthesis of an earlier 52-field run.

```
python3 -I <skill>/scripts/render_prompt.py <skill>/references/synthesis-template.md --lang en \
  --set date=YYYY-MM-DD --out <scratch>/synthesis-skeleton.md
```

`scripts/render_prompt.py` reads only the text between the first separator line and the next one. Variables: `{lang}` and `{date}` (default today). All other `{s.*}` placeholders come from `references/strings/<lang>.json`. `count.py` finds the six metric rows by their names, not by the table header wording.

---

## Writing rules

- Write all free text, headings and non-metric row names in the language with code `{lang}` (en = English, ko = Korean). Keep these fixed strings exactly as given: the title line, the status line, the six metric row names, and anything copied from field reports.
- Do not change the status line on line 2 or the status line in the first paragraph of §1.
- Keep the "run results" table in the header as a vertical two-column table (item and value). Put only numbers in number cells. `scripts/count.py <output> --expect <output>/00-synthesis.md` looks for the six metric rows in the first 100 lines and compares them with the real counts of the report folder.
- "{s.synthesis_metrics.already_met_any}" is the number of candidates carrying the "{s.already_met}" mark, partial ones included. "{s.synthesis_metrics.already_met_full}" is the number whose integration item ends with "{s.already_met}" alone. Both rows are compared by `count.py --expect`.
- The investigator-model row joins `model(effort) ×count [adapter]` with ` · `. Example: `Claude Opus 5.5(high) ×3 [Claude adapter] · gpt-6.1-sol(high) ×2 [Codex adapter]`. The batches row joins `<batch number>: <field slugs>, <adapter>` with `; `.
- Never call repeated proposals "independent convergence". Count independent groups this way: with the same reading and the same prompt, each model family (Claude, GPT, etc.) is one group. More models or runs from one family do not add groups. Candidates citing the same work count as one repetition even across fields. Use repetition counts only to order items.
- Group numbers and "{s.already_met}" marks are the investigators' self-reports. If the synthesis did not re-judge them, say so.
- Markers follow `report-format.md` §7. † is an unverified source flagged by the investigator in the title line. ‡ is a step 3 recheck verdict of `bib_error`, `content_mismatch` or `not_found`. `undetermined` keeps † only.
  - §2: add †/‡ after candidate names.
  - §3: add †/‡ after the participating candidate names and give the recheck verdict of ‡ candidates in the "Sources" line.
  - §4: list † candidates and ‡ candidates separately, each with a count.
- Fill every `<…>` slot. Do not delete a section that has nothing to say; write "not applicable" and the reason.

## Skeleton

```markdown
# {s.synthesis_title}
{s.status_line}

<one or two sentences on the target documents, the parent task and the run plan file>

**Run results:**

| Item | Value |
|---|---|
| {s.synthesis_metrics.fields} | <number> |
| {s.synthesis_metrics.reports} | <number> |
| {s.synthesis_metrics.candidates} | <number> |
| {s.synthesis_metrics.already_met_any} | <number> |
| {s.synthesis_metrics.already_met_full} | <number> |
| {s.synthesis_metrics.unverified} | <number> |
| Investigator models | <model(effort) ×count [adapter] · …> |
| Synthesis model | <model name, effort> |
| Batches | <batch number: field slugs, adapter; …  e.g. 1: ethics·law·economics, Claude adapter; 2: music·medicine, Codex adapter> |
| Failures and reruns | <count and fields> |

**Prompt versions:** <one common template version, or which version and which extra clauses each batch ran with. Details in 00-run-log.md>

**Source check:** <distribution of machine-check results, recheck count and distribution, scope checked (citation only, or content too)>

## 1. What repeated across fields — conclusions first

{s.status_line} Adoption, rejection or deferral is decided in the parent task's review.

<3–6 directions that different field reports proposed in different vocabulary. For each, give the §3 cluster name, the participating fields and the number of independent groups>

### 1.1 Three-axis re-rating of the top candidates

| Candidate | Machine-checkable part | Open issue it feeds | Added burden | Check against the design |
|---|---|---|---|---|
| <candidate> | <how much a program can decide without AI judgment, and why> | <open item this candidate is input to> | <direction of record, token and user-reading burden> | <result of checking against the whole design> |

<which candidates to look at first and which need a cost comparison first. State that this is model judgment, not grounds for adoption>

### 1.2 Issues found in the critical review and how they were handled

| Issue found | Handling |
|---|---|
| <missing fields, overstatement, skewed group distribution, unchecked "already met", effect and cost not measured, etc.> | <section fixed, or unverified item left> |

Common counterexample: <assumption that breaks across all clusters, e.g. human-organization and biological theories assume intent and incentives that an AI session lacks; a new field filled by AI is fluent, not true>

## 2. Axis (a) — per group: integration candidates / already met / counterexamples

Notation: in `field: candidate†`, † is an unverified source in the title line; in `field: candidate‡`, ‡ is a bibliography error, content mismatch or not-found verdict in the recheck. A candidate touching several groups repeats in each. Read a group with few candidates as "less investigated", not "no candidates".

### <group number> <group title>

- Integration candidates (<count>): <field: candidate; …>
- Seen as already met (<count>): <field: candidate; …>
- Counterexamples and limits: <common to this group>

<repeat in the same form for every group in the group map>

## 3. Axis (b) — cross-field clusters per problem

Per problem, cluster what different fields proposed in the same direction. Cluster names (A, B, …) are for reference inside this document only.

### 3.<n> <problem name> (<related group numbers>)

**Cluster <name> — <one-line gist>.** <participating fields and candidate names>
- Common proposal: <what to change or add; which design sentence it is a method for>
- Differences: <differences by field>
- Counterexamples: <assumptions that break, cost, unproven effect>
- Sources: <source status. For ‡ candidates give the recheck verdict (bib_error, content_mismatch, not_found)>

### 3.<n> Clusters and groups

| Cluster | Main group | Related groups |
|---|---|---|
| <name> | <number> | <numbers> |

## 4. Unverified and recheck

- Recheck results: <counts per verdict and list per field, linked to each report's recheck section>
- † candidates (<count>): <field: candidate; …>
- ‡ candidates (<count>): <field: candidate — recheck verdict; …>
- <unverified item> — reason: <reason>
- Group numbers each candidate touches — reason: <whether investigators' self-reports were tallied as is>
- "Already met" marks — reason: <whether investigators read less than the whole design>
- Effect experiment — reason: proving effect is outside this procedure
- Real token cost — reason: <whether a way to measure existed>

## 5. Registration proposal

**Location:** <source list file and where to insert>
**Anchor:** `<theory-sweep-source-YYYYMMDD>`

| Material and relative path | Range the parent session actually checked | Status and limits |
|---|---|---|
| Synthesis `00-synthesis.md` · SHA-256 recorded in the registration row (cannot reference itself) | <which of §1, §2, §3 were read> | AI survey and comparison proposal; not adopted, effect not proven |
| <number> field reports · versions in Appendix A | <range of existence and version checks> | <primary material: one investigator wrote one field without reading other reports> |
| Pre-review notes `01-review-notes.md` · SHA-256 `<value>` | <candidates reviewed> | Adoption candidate / defer / exclude decided with the user; not a design adoption |
| Run log `00-run-log.md` · SHA-256 `<value>` | <up to which step the version covers> | Parent session's record, deviations and failures included |
| Handoff `02-handoff.md` · SHA-256 `<value>` | <range read> | Summary for the parent session; not primary material |
| Judge JSON folder `<path>/` · <number> files · sample `<file>` SHA-256 `<value>` | <files read> | Judge output; reference values |
| Recheck JSON folder `<path>/` · <number> files · sample `<file>` SHA-256 `<value>` | <files read> | Rechecker output; citation and content scope differs per file |

Compute SHA-256 per file. For a folder, give the file count and one sample file's hash, and put per-file hashes in Appendix A.

Counts: fields <number>, candidates <number>, already met <number> (fully <number>), unverified sources <number> (after recheck: <number per verdict>).

## Appendix A. Versions (SHA-256)

<time of the versions and the command used (`shasum -a 256 <file>`)>

| File | SHA-256 |
|---|---|
| <slug>.md | `<value>` |

The SHA-256 of this synthesis itself is computed at registration (it cannot reference itself).
```
