# Evidence

This file backs `models.md` and the format rules in `report-format.md`. It summarizes one evaluation carried out on 2026-10-17, plus an earlier 52-field run on 2026-10-14 that served as the baseline. Everything here is a reference value from small samples. Nothing here proves that adopting a candidate has any effect.

Model names are given as they were named in the evaluation. Re-evaluate with your own models (`models.md` §3).

## 1. Scope

| Source | What it is |
|---|---|
| Model trial (§2) | 5 models × 7 fields × 1 run on the same design document, scored by scripts, two judge families and a web recheck |
| Precedent surveys (§3) | Two AI-run web surveys: published comparisons of LLM citation accuracy, and open-source agent tools' role-to-model assignments |
| End-to-end trial (§4) | All steps 0–6 run on a second, unrelated design document with 5 fields |
| Baseline run (§5) | An earlier 52-field run on the first design document, used as baseline and as the source of several format rules |

## 2. Model trial (2026-10-17)

### Setup

- Target: a design document for an AI development tool. Same prompt (the baseline run's template), same files, same line ranges, short web searches allowed for source checks.
- Fields (7): philosophy (epistemology), cognitive psychology, medicine, mathematics, reliability and safety engineering, accounting and auditing, music.
- Models (5), effort high: Claude Opus 5.5, Claude Sonnet 5.5, Claude Haiku 5.5 (launched with the Claude Code Agent tool); gpt-6.1-sol, gpt-6-luna (launched with `codex exec`, web search on). 35 reports.
- Baseline: 7 reports by Claude Fable 5.1 (effort high) from the 2026-10-14 run, not rerun. 42 reports scored in total.
- Scoring:
  - Format, scene presence, unverified-marker rate: `score_format.py`.
  - Connection score (1 forced / 2 loose / 3 direct), quotation existence, scene score: two judge families. Claude-family reports, baseline included, were judged by gpt-6-astra. Codex-family reports were judged by Claude Opus 5.5. Both judges saw all 6 philosophy reports, to measure agreement.
  - Bibliography: `bib_check.py` matched title-line sources against Crossref and OpenAlex (190+ citations). The 123 non-matches went to 6 Claude Opus 5.5 recheckers with web search, which sorted them into exists / bibliographic error / content mismatch / undetermined / not found.
  - "Errors without a marker" = citations without an unverified marker that the recheck found erroneous, mismatched or not found.

### Results (7 fields combined)

| Model | Candidates | Format pass | "Already met" marked | Unverified title markers (rate) | Unverified section items | Final: exists / bib error / content mismatch / undetermined | Errors without a marker | Connection mean (assigned judge) | Connection = 1 | Judge agreement (philosophy, exact) |
|---|---|---|---|---|---|---|---|---|---|---|
| Claude Fable 5.1 (baseline) | 41 | 6/7 | 19 | 8 (0.20) | 43 | 41/0/0/0 | 0 | 2.86 | 2 | 0.67 |
| Claude Opus 5.5 | 35 | 7/7 | 23 | 7 (0.20) | 51 | 35/0/0/0 | 0 | 2.91 | 1 | 1.00 |
| gpt-6.1-sol | 32 | 7/7 | 32 | 1 (0.03) | 33 | 32/0/0/0 | 0 | 2.71 | 0 | 0.75 |
| Claude Sonnet 5.5 | 33 | 7/7 | 20 | 7 (0.21) | 39 | 31/1/0/1 | 1 | 2.80 | 3 | 0.20 |
| Claude Haiku 5.5 | 32 | 5/7 | 7 | 5 (0.16) | 35 | 28/0/1/3 | 1 | 2.72 | 1 | 0.25 |
| gpt-6-luna | 26 | 7/7 | 14 | 0 (0.00) | 9 | 21/1/0/4 | 1 | 2.50 | 0 | 0.75 |

How to read: connection is out of 3. Judge agreement is the share of philosophy candidates where both judges gave the same connection score. Part of "undetermined" comes from parser limits (see Observations).

Connection mean by field:

| Model | Philosophy | Cognitive psych. | Medicine | Mathematics | Reliability | Accounting | Music |
|---|---|---|---|---|---|---|---|
| Claude Fable 5.1 | 2.83 | 3 | 3 | 3 | 3 | 3 | 2.2 |
| Claude Opus 5.5 | 3 | 3 | 2.8 | 3 | 3 | 2.6 | 3 |
| gpt-6.1-sol | 2.75 | 2.6 | 2.6 | 3 | 2.5 | 2.8 | 2.75 |
| Claude Sonnet 5.5 | 2.6 | 3 | 2.4 | 3 | 2.6 | 3 | 3 |
| Claude Haiku 5.5 | 2.75 | 2.8 | 2.75 | 2.75 | 3 | 2.6 | 2.4 |
| gpt-6-luna | 2.25 | 2.5 | 2.5 | 2.5 | 2.33 | 2.25 | 2.33 |

### Observations (confirmed in the trial data)

- **Bibliography accuracy differed little.** Most machine non-matches were reprint or reissue year differences. After the recheck, the real errors were: Sonnet 1 (one author missing from an arXiv paper), luna 1 (wrong title of a standards handbook), Haiku 1 content mismatch (the four types of unsafe control action in STPA misstated). Fable, Opus and sol had 0.
- **Restraint differed clearly.** luna left the unverified section empty in 6 of 7 fields and had 0 title markers. sol had 1 title marker but 33 unverified section items. The three Claude models and Fable marked 0.16–0.21 of titles. Haiku marked all 4 candidates unverified in mathematics, a case of backing off in a narrow field.
- **Only Haiku broke format.** It renamed or dropped items in 2 reports. In all 7 fields it wrote "(author, year)" without a work title, so 22 automatic citation checks failed. This is the evidence for the title-line rule. The Fable baseline exceeded the 3–6 candidate range once (7 in accounting).
- **sol separated "already met" most often** (all 32 candidates). The common reason both judges gave a connection score of 2 was "the design already holds this, but the report did not say already met", most often for luna and Haiku. This is the evidence for the already-met rule.
- **Connection was highest for Opus and Fable and lowest for luna.** luna also had the fewest candidates and stayed at or below 2.5 in every field. Every connection score of 1 given by gpt-6-astra (Sonnet 3, Fable 2, Opus 1, Haiku 1) had the same reason: a blanket rule that conflicts with an existing design rule. No report had analogy-only candidates, music included.
- **Judges are sensitive on connection.** Exact agreement in philosophy: Opus report 1.0, luna and sol 0.75, Fable 0.67, Haiku 0.25, Sonnet 0.2. Agreement within ±1 was at least 0.8 for all. One Sonnet candidate got 1 from one judge and 3 from the other.
- **Time:** sol about 3 minutes per report (10–14 web searches by the run summary; 8–16 `web search:` log lines per report, which count a different thing), luna about 1.5–2 minutes, the three Claude models 3–6 minutes in parallel. Token counts existed only in Codex logs, so no cross-model token table was made.
- **Parser limits** (`bib_check.py` at the time): 4 subtitle lines in one luna report and 1 "no candidates" line in one Haiku report were read as sources and ended as "undetermined". Standards documents (ISA, COSO, IEC) were not in Crossref and relied on the recheck.

### Limits of the trial

- One run per model and field. Model differences and run-to-run variance cannot be separated.
- Two judge families only. Each saw the other family's reports in philosophy only.
- "Group number not in the design" counts from one judge came from it not reading outside the given ranges; the other judge read whole files and counted 0. Truly missing groups were not confirmed.
- The baseline reports were made by another session and lack the run line. Prompt, files and ranges were confirmed to be the same.
- Machine "match" citations (68+) were not checked for content. "Exists" means the citation exists.

## 3. Precedent surveys (2026-10-17)

Both surveys were AI-run web searches. Each finding was marked by how it was confirmed (original read, search summary only, or secondary report). They inform design choices; they are not evidence of effect.

### 3.1 Published comparisons of LLM citation accuracy

Conclusions:

1. Precedents exist. Since 2023 several studies gave the same citation task to several LLMs and compared fake-reference rates.
2. No precedent matched this task: reading a design document and choosing discipline theories as integration candidates, with per-field subagents and current models.
3. The survey supported four bibliography classes: does not exist / exists with citation errors / exists but content does not match the claim / undetermined. The recheck verdicts follow this (`not_found`, `bib_error`, `content_mismatch`, `undetermined`, plus `exists`).
4. An "unverified" rate alone means nothing. Precedents pair "did not answer" with "answered wrongly". Record both.
5. Format compliance does not predict source accuracy. In one study, adding constraints kept the format but raised fake sources. So format and citation accuracy are scored separately.

Confirmed facts behind these conclusions:

- The same model's rate of genuine citations changed sharply with conditions (.381 by default, .119 under a publication-year restriction, in one 2026 study).
- Model families back off differently. On a short-fact benchmark (SimpleQA), a small Claude model declined 75.3% of questions, while a small GPT model declined 0.9% and was wrong on 90.5%.
- Reasoning settings and system prompts change abstention rates (AbstentionBench).
- LLM judges agreed with human samples about 88% in two cases. One figure is from a preprint; the published figure was not confirmed.
- In one study, an audit of 35 "undetermined" citations found 16 fabricated.
- Swapping the judge mid-study broke score comparability in one benchmark (MultiChallenge). This backs "never change the judge within a run".

Survey proposals reflected in the skill (model judgment, not verified): machine check first, then recheck; judge from a different family, fixed per run; record exact model version and effort; stratify trial fields by how rich their literature is. The survey suggested 8–12 trial fields; the trial used 7.

### 3.2 Role-to-model assignment in open-source agent tools

Survey of 11 tools, 23 searches or page reads.

Confirmed in tool documentation:

1. Most tools have one main model plus slots for helper roles (summaries, compression, titles, commit messages, search).
2. Three tools state role defaults in their docs. All put the coordinator or main loop on a top-tier model. One says a weak main model "caps quality regardless of delegated models".
3. Review and judging roles are not moved down. One tool says small models "drift and rubber-stamp". Another gives critic and architect roles the highest effort and says the reviewer should be a different family from the writer.
4. Counterexample: one official tool runs its exploration subagent on a top-tier model for subscribers, so "exploration = small model" is not a universal rule.

Inference (not verified): tools give small models search that fetches facts with tools. Field investigation draws knowledge from the model's own memory, which is closer to the "planning consultant" or "architect" roles that tools put on top-tier models.

## 4. End-to-end trial on a second document (2026-10-17)

Purpose: test the skill's own procedure, adapters and scripts on a document unrelated to the first. It was not a design review of that document.

### Setup

- Target: a 290-line design spec for a research-results explorer. The group map had 24 groups.
- Fields (5), one per discipline group: cognitive psychology, industrial engineering and human factors (HCI), design (design thinking, service design), information theory (with the no-analogy clause), rhetoric and narratology.
- No common example rule, so every scene item read the fixed "no example rule" string.
- Investigators: Claude Opus 5.5 (high) ×3 via the Claude adapter, in parallel; gpt-6.1-sol (high) ×2 via the Codex adapter (`codex exec`), in sequence.
- Synthesis: Claude Opus 5.5. Judges: gpt-6-astra (high) for the 3 Claude reports, Claude Opus 5.5 for the 2 sol reports.
- A coordinating session set the inputs and decisions. The completeness check, adapted first questions, user approval and per-candidate user questions were skipped and recorded as deviations.

### Results

| Item | Value |
|---|---|
| Reports created | 5/5, no change outside the output files (`git status` before and after) |
| Time | Claude parallel about 5 min; sol about 3 and 3.5 min |
| Format pass | 5/5, no stray sections |
| Candidates | 19 |
| Already met (any / fully) | 19 / 0 |
| Unverified title markers | 0 |
| Unverified section items | 31 |
| Machine bibliography check (19) | match 11 · partial 4 · nohit 3 · standard_doc 1 |
| Recheck (8 non-matches) | exists 7 · content_mismatch 1 · others 0 |
| Judge connection scores | 3 points: 15 · 2 points: 3 · 1 point: 1 |
| Quotation existence | present 19/19 |
| Scene score | not scored (no example rule) |
| `count.py --expect` | matched on the first write |
| Top candidates in pre-review | 5; all deferred by the coordinating session |

Script defects found and fixed during the trial:
- The scorer counted a "no example rule" scene as a missing scene. It now reports it separately.
- The scorer read a long number inside a citation as a group number. Group patterns are now limited to 1–2 digits per side, and groups not in the map are a warning column.

Gaps in the skill text found and fixed (7): definitions of † and ‡; the position of the unverified section once a recheck section is added; a "fully already met" metric, because "already met (any)" was 19/19 and carried little information; the header table format for runs using two adapters; missing rows in the §5 registration table (handoff, run log, judge JSON); a fallback scene rule for pre-review without an example rule; a definition for counting independent groups.

Remaining limits of this trial: one judge per report, so no judge agreement; machine "match" citations were not checked for content; one field per discipline group, so missing fields are likely; token cost and effect not measured.

OpenAlex: without a key it returned HTTP 429 with a Retry-After of about 16 hours (observed on 2026-10-17). With a key set in `OPENALEX_API_KEY`, the run used about 190 of 10,000 credits. Pass the key only as an environment variable.

## 5. Baseline run (2026-10-14, 52 fields)

- One investigator per field on the first design document, Claude Fable 5.1 (effort high), batches of up to 8.
- In the 52 reports, the section for excluded ideas had more than 20 different titles and could not be collected by machine. This is the evidence for the fixed section titles.
- 5 fields reported running out of web-search allowance. Their sources stayed marked unverified and went to the recheck. Running out is not a failure.
- Cost estimate used for planning: about 300 lines read and about 100 lines written per investigator. Unverified: this was never measured.
- 2 fields (LLM agent engineering and evaluation research; resilience engineering) were added after the first 50.

## 6. Unverified

- Unverified: run-to-run variance. Reason: every model–field pair ran once.
- Unverified: judge bias beyond two families. Reason: no third judge family was used.
- Unverified: synthesis quality by model. Reason: synthesis was run with one model only.
- Unverified: `axis=problem`. Reason: never run.
- Unverified: the maximum number of parallel subagents or Codex sessions. Reason: batches of up to 8 were used; limits were not tested.
- Unverified: real token cost per run. Reason: no measurement for Claude-launched investigators.
- Unverified: effect of any candidate. Reason: proving effect is outside this procedure.
