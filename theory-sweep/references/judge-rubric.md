# Judge prompt template

Step 2 (quality check) uses this prompt to hand items that need human-like judgment (forced candidates, quotation existence, example-scene connection) to a model of a different family. Judge scores are reference values. The user makes the final call.

## Assignment rules

- Pick a judge from a model family different from the investigator's. Evidence: `evidence.md` §3.
- Do not change the judge within a run. Scores from different judges are not comparable.
- With judges from two families, let both judges see the same field's report so agreement can be measured.

## Variables

| Variable | Meaning |
|---|---|
| `{report_path}` | Field report to judge |
| `{output_path}` | Judge JSON path |
| `{project_root}` | Absolute path of the folder holding the target documents |
| `{read_list}` | The same files and line ranges the investigator got |
| `{group_map}` | The same group map the investigator got |
| `{example_rule}` | The same example rule the investigator got. If none, `{s.no_example_rule}` |
| `{forbidden_dirs}` | Sentence listing folders not to open. Include folders holding reports other than the one judged |
| `{lang}` | Language for the `note` and `overall_note` text. Set by `--lang` |

Output JSON keys are fixed for `scripts/aggregate.py`: `connection`, `quote`, `ledger` (the example-scene score; the key name is historical), `analogy_only`, `unknown_groups`. `quote` takes one of four language-neutral codes: `present`, `partial`, `absent`, `no_quote`.

---

You judge a report that proposes theory-integration candidates from one discipline for a design document. You do not know which model wrote the report. Do not judge whether you agree with its conclusions. Judge only the three items below.

Write the free text in `note` and `overall_note` in the language with code `{lang}` (en = English, ko = Korean).

Project root: {project_root}

Files to read (read the originals directly):
- Report to judge: {report_path}
- Design documents:
{read_list}

Group map:
```
{group_map}
```

Example rule: {example_rule}

Do not read: {forbidden_dirs} Do not open any report other than the one judged. Do not search the web; whether sources are genuine is not part of this judgment.

For every candidate section of the report (a title line of the form `## <candidate> — <source>`), judge the following.

1. Connection score (forced-candidate check), 1–3
   - 3 direct: the group and sentence the candidate points to really exist in the design, and the proposal concretely changes a gap or open issue in that sentence.
   - 2 loose: the problem is right, but the proposal is generic, or the design already holds the same content and the report did not mark it "{s.already_met}".
   - 1 forced: the candidate ties to no sentence of the design, carries the theory over only as an analogy, or proposes something that conflicts with the design.
2. Quotation existence: does the design sentence quoted in the "{s.labels.problem}" item really exist within the given files and line ranges? Use one code: `present`, `partial` (same meaning, different wording), `absent`, or `no_quote` (nothing quoted).
3. Example-scene score, 1–3
   - 3: what the candidate changes shows up concretely as a difference in the behavior of the user, the AI or the tool in the scene the example rule sets.
   - 2: a scene exists, but its link to the candidate is weak or generic.
   - 1: there is no scene, or it only describes the example subject's features.
   - If the example rule is "{s.no_example_rule}", skip item 3 and set `ledger` to null.

For the report as a whole, also count: candidates that are analogy only, and candidates that cite a group number not in the group map. Do not count numbers you could not check because they fall outside the given line ranges as missing; mention them separately in `overall_note`.

Output file: create only {output_path}. Do not modify any other file. Do not run commands of any work-logging tool.
Output format (one JSON object):
```
{"report": "<report path>", "candidates": [
  {"name": "<candidate name>", "connection": 3, "quote": "present", "ledger": 3, "note": "<one-sentence reason>"}
], "analogy_only": 0, "unknown_groups": 0, "overall_note": "<two sentences at most>"}
```
In `note`, say in one sentence which design sentence the candidate connects to, or fails to connect to. Do not record your preferences or comments on style.
End your chat reply with "{s.chat_end.judge}".
