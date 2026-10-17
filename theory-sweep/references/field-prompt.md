# Field investigator prompt template

This is the prompt for one field investigator. `scripts/render_prompt.py` reads only the text between the first separator line and the next one as the body. Never put a line containing only the separator inside the body.

The body holds the full report format once, written with `{s.<key>}` placeholders. `render_prompt.py --lang en|ko` fills them from `references/strings/<lang>.json`. Do not type fixed strings into the body.

## Variables

| Variable | Meaning | Example value |
|---|---|---|
| `{field}` | Field name. Read from the field list: the `field (en)` column for `--lang en`, `field (ko)` for `--lang ko` | Accounting and auditing |
| `{slug}` | File-safe English ID from the field list. Usually used inside `{output_path}` | accounting-auditing |
| `{model}` | Exact name of the investigator model | Claude Opus 5.5 |
| `{effort}` | Reasoning effort | high |
| `{output_path}` | Report file path (relative to the project root, or absolute) | reviews/theory-sweep/{slug}.md |
| `{extra_clause}` | Per-field extra clause from the field list. Empty if none | See "Extra clause examples" below |
| `{project_root}` | Absolute path of the folder holding the target documents | /home/me/project |
| `{read_list}` | Files and line ranges to read. One per line, each starting with "- " | - docs/design.md L1–240 |
| `{group_map}` | All group (problem) numbers and titles of the target design. May span lines | 1-1 Basic stance on operating AI · 1-2 … |
| `{example_rule}` | Common example scene rule. If none, use `{s.no_example_rule}` | See below |
| `{forbidden_dirs}` | Sentence listing folders not to open | Do not open any file in reviews/theory-sweep/ or reviews/old-sweep/. |
| `{lang}` | Report language code. Set by `--lang` | en |
| `{date}` | Run date, YYYY-MM-DD. Defaults to today | 2026-10-17 |

Fixed strings that carry their own placeholders are expanded too: `{s.title_suffix}` contains `{date}`, and `{s.run_line}` contains `{model}` and `{effort}`.

Example value for `{example_rule}`: "Describe how the work of this tool, the user and the AI changes while building a small personal budget app (expense entry, monthly totals, CSV export). Do not describe the budget app's own features."

Rendering example:

```
python3 -I <skill>/scripts/render_prompt.py <skill>/references/field-prompt.md --lang en \
  --vars <scratch>/vars.json --fields philosophy-epistemology,accounting-auditing \
  --list <skill>/references/field-list.md --out <scratch>/prompts/{slug}.txt
```

---

You are an expert in {field}. Critically review whether the design described in the documents below could borrow or integrate any theory, method or philosophy from {field}.

Report language: write all free text in the language with code `{lang}` (en = English, ko = Korean). Copy every fixed string given below exactly as written. Do not translate or reword it.

Project root: {project_root}

Files to read (read the originals directly and keep to the line ranges; you may read other sections that belong to the group map below if you need them):
{read_list}

Do not read: {forbidden_dirs} Do not consult reports from other fields or other models.

Output file: create only {output_path}. Do not modify any other file.
Do not run commands of any work-logging tool.

Write the first three lines of the file exactly as follows.
```
# {field} — {s.title_suffix}
{s.status_line}
{s.run_line}
```

Treat the group map below as the full set of problems the design covers. Look across the whole map; do not concentrate on the first few groups.
```
{group_map}
```

Report format (3–6 candidates; more is not better):
{s.candidate_heading}
- {s.labels.meaning}: two or three sentences.
- {s.labels.problem}: the group number from the map above, and a quotation of the matching design sentence (file and line).
- {s.labels.proposal}: what to change or add, and how. Anything the design already contains must be marked "{s.already_met}"; propose only what goes beyond it. If the existing contract is fully sufficient, write only "{s.already_met}".
- {s.labels.scene}: {example_rule}
- {s.labels.limits}: assumptions that break when moving the idea from human organizations, living systems and the like to AI. If the effect is unproven, say so.
- {s.labels.status}: {s.status_value}

If the example rule above is exactly "{s.no_example_rule}", write only "{s.no_example_rule}" in that item for every candidate.

Title-line rules:
- Always give the work title in the source. Italicize books and standards with *asterisks*; put papers and chapters in "double quotes". Never use the form that has only author and year in parentheses.
- Do not use " — " inside the candidate name. Use " — " in the title line exactly once, to separate the candidate name from the source.
- If you could not verify a source directly, append `{s.unverified_title_marker}` to the end of its title line. Never present a citation from memory as verified. You may use short web searches to verify a source; if it stays unverified, keep the marker.

If this field offers nothing usable, write "{s.no_candidates}" and the reason. Do not pad the report.
To list things you reviewed but did not propose, use the section title `## {s.sections.not_proposed}`. Apart from that section and `## {s.sections.unverified}`, which is the last section you write, create no other `## ` sections.
{extra_clause}
As the last section you write, add `## {s.sections.unverified}`. List each thing you could not verify on its own line, in the form `{s.unverified_item_format}`. If nothing is unverified, write "{s.nothing_unverified}" and one line saying why; do not write "{s.unverified_item_prefix}" on that line.
End your chat reply with "{s.chat_end.investigator}".

---

## Extra clause examples

These clauses were used in an earlier 52-field run. The common template stayed fixed; only this slot changed per field. The field list already carries the ready-to-use English text in its `extra clause (en)` column.

| Kind | Fields it was used for | Clause (imperative form) | Why |
|---|---|---|---|
| No analogy | Physics, biology, ecology, neuroscience, earth science, information theory, systems theory, architecture, sports coaching, religious studies, music, film and theater, navigation, geography | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. | Natural-science fields (and arts and practice fields) easily produce analogy-only candidates |
| Precedent overlap | Military strategy | Read the design's existing reference section on doctrine and red teaming (give file and lines). Mark what it already covers as "already met". | Part of the field was already referenced by the design |
| Precedent overlap | Software engineering | Read the decision table of the earlier precedent report (give file and lines). Mark what it covered as "already met" and propose only what it did not cover. | The field is core to the design; only additions are useful |
| Precedent overlap | Systems engineering | The basics of requirements traceability and configuration management were already judged in a precedent. Look for concrete methods beyond them. | The precedent covers the basics |
| Precedent overlap (adjacent field) | Control engineering | Find candidates different from those the physics field covered (list their candidate titles). | Reduces duplication with an earlier batch without letting the investigator read another report |
| Precedent overlap (adjacent field) | Industrial engineering and HCI | Find candidates different from those the cognitive psychology field covered (list their candidate titles). | Same as above |
| Precedent overlap | Project management | The design already holds the basics of rolling-wave planning, change control and baselines. Do not propose the basics again; look for concrete methods beyond them. | The design already contains the basics |
| Scope note | Religious studies | Do not look at religious claims themselves. Look at the procedures, records and review structures that practice traditions built (daily schedules of monastic rules, chapter meetings, novitiate periods, examination of conscience). | Separating belief content from procedural structure is what makes candidates possible in this field |

Listing an earlier batch's candidate titles in an adjacent-field clause is allowed. Never let an investigator read another field's report file.
