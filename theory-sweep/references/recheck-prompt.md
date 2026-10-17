# Bibliography recheck prompt template

Step 3 (source check) uses this prompt to recheck, by web search, only the citations that the `scripts/bib_check.py` machine check did not match. Verdicts are reference values. The user makes the final call.

## Preparation

- The list file holds the rows of `bib_check.py --out` (JSON Lines) whose verdict is not `match`.
- Split a long list by report across several recheckers. One earlier trial split 123 citations across 6 recheckers (`evidence.md` §2).
- Prefer recheckers from a model family different from the investigator's. If you use the same family, record it in the run log.

## Variables

| Variable | Meaning |
|---|---|
| `{list_file}` | JSON Lines file of citations to recheck |
| `{output_dir}` | Folder for the recheck result JSON files |
| `{forbidden_dirs}` | Sentence listing folders not to open. Include folders holding reports not in the list |
| `{lang}` | Language for the `note` text. Set by `--lang` |

Verdict codes and JSON keys are language-neutral and fixed for the scripts.

---

You verify academic citations. Check, one by one by web search, the source strings in the list file below (the author, year and work written in the title line of a report's candidate). Do not use the identity of the model that wrote a report in your verdict.

Write the free text in `note` in the language with code `{lang}` (en = English, ko = Korean).

List file (JSON Lines, one citation per line): {list_file}
Main fields per line: report (report path), candidate (candidate name), source (source string), flagged_unverified (whether the report already marked it unverified), parsed (author, year and title guessed by the machine), verdict (machine-check result), best (best machine-check hit; may be missing).

Handling by machine verdict:
- `partial`, `nohit`: recheck as is.
- `no_title`: the title line has no work title. Find the work in the candidate section's body and recheck it. If you cannot find it, search by author and year.
- `standard_doc`: a standard or institutional document. Look for the issuing body's official page first.
- `not_a_citation`: the machine may have read a string that is not a source. Find the actual source in the candidate section's body and judge it. If there is none, use `undetermined` and give the reason.

Give each citation one verdict.
- `exists`: the author, year and work exist and the citation is correct. Edition or reprint year differences count as correct (e.g. original 1906, reprint 2016).
- `bib_error`: the work exists, but one or more of author, year or title is wrong. Say what is wrong.
- `content_mismatch`: the work exists, but what the report's candidate section presents as the work's claim does not match the work's actual content (by abstract, summary or secondary sources). Read that candidate section in the report to decide.
- `undetermined`: two or three searches cannot settle whether it exists (standards, classics, out-of-print works, etc.). Give the reason.
- `not_found`: there is evidence that it does not exist in any form (the author–title pair appears in no source). Give the evidence.

Rules:
- Finish each citation within two or three web searches. Keep total searches at or below list length × 3.
- State the authority of the material you checked (journal or conference paper, publisher page, encyclopedia, personal blog, etc.) inside the `note` sentence.
- Never write "exists" from memory alone. If searches find nothing, use `undetermined`.
- Read only the relevant candidate section of a report. {forbidden_dirs}
- Modify no file other than your output files. Do not add markers to report files. Do not run commands of any work-logging tool.

Output: write one JSON file per report to {output_dir}/<report file name without .md>.json. If reports with the same name exist in several folders, use <report's folder name>--<report file name>.json instead.
Format:
```
{"report": "<report path>", "items": [
  {"candidate": "<candidate name>", "source": "<source string>", "flagged_unverified": false,
   "verdict": "exists|bib_error|content_mismatch|undetermined|not_found",
   "found": "<the exact citation found, one line, or null>", "note": "<reason and material authority, one sentence>"}
], "searches": <total number of searches>}
```
End your chat reply with the verdict counts per report (exists/bib_error/content_mismatch/undetermined/not_found) followed by "{s.chat_end.rechecker}".
