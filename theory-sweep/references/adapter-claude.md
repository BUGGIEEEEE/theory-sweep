# Claude Code adapter

How to launch investigators, judges and recheckers in Claude Code. Read it in steps 1, 2 and 3. Adapters for other tools use the same four headings in the same order: launch, model selection, collecting files, failure handling.

## 1. Launch

1. Render the prompt to a file. Put it in the session's scratch directory, or in a temporary folder outside the output folder.
   ```
   python3 -I <skill>/scripts/render_prompt.py <skill>/references/field-prompt.md --lang <lang> \
     --vars <scratch>/vars.json --fields <slug1,slug2,…> \
     --list <skill>/references/field-list.md --out <scratch>/prompts/{slug}.txt
   ```
   Render `judge-rubric.md` and `recheck-prompt.md` the same way, without `--fields`, using `--set` or `--vars`.
2. Launch one subagent per field with the Agent tool. Use only these two lines as the prompt.
   ```
   First read this file and follow its instructions exactly: <scratch>/prompts/<slug>.txt
   Create only the output file named in those instructions and modify no other file.
   ```
   - Why: every investigator gets the identical prompt, character for character. The parent session cannot alter it while copying. The rendered file stays, so you can later check which prompt a report ran on.
   - Use a general-purpose subagent type (or omit the type). Investigators need file read and write, and web search.
   - One subagent handles one field. Never reuse a subagent for another field; it would know the earlier field's result.
3. Launch one batch (default 5–8) in a single response so the subagents run in parallel. Do not launch the next batch until the step 2 check is done.
   - Observed time per report: see `evidence.md` §2.
   - Unverified: the maximum number of subagents that can run at once. Reason: batches of up to 8 were used; the limit was not tested.
4. Wait for completion notices. Never write results before a notice arrives. A subagent's chat reply should end with the role's `chat_end` string from `strings/<lang>.json` (investigator, judge or rechecker). Do not use the chat reply as evidence; use only the files.

## 2. Model selection

- Set the Agent tool's `model` to an alias such as `opus`, `sonnet` or `haiku`. These are examples; the aliases your installation offers, and the versions they point to, change over time. Write the exact model name you confirmed at run time into `{model}`.
- Set reasoning effort with the Agent tool's `effort` parameter if your installation offers it (for example low, medium, high). Use the value chosen in step 0 (default high) and write the same value into `{effort}`.
- If `model` is omitted, the subagent inherits the parent session's model. Do not omit it: the run line and the real model could then disagree.
- To run a judge from a different family (for example a Codex model), launch it the way `adapter-codex.md` describes.

## 3. Collecting files

When a batch finishes, check each field.

1. Before launching, save `git status --porcelain` (if the target folder is a git repository).
2. Check that the output file exists and is not empty.
3. Check the first three lines (`head -3 <report>`). Line 2 must equal `status_line` character for character.
4. Score the format with `python3 -I <skill>/scripts/score_format.py <reports> --format table`.
5. Run `git status --porcelain` again and compare. If any file other than the outputs changed, report the file and the change to the user. Revert only after the user confirms.
6. Record the result (success, failure, rerun) in `<output>/00-run-log.md`.

## 4. Failure handling

- Count as failure: no output file, an empty file, wrong first three lines, other files modified, or a chat reply that does not end with the investigator's `chat_end` string.
- If the output file is missing or empty, launch one new subagent with the same rendered file. Do not continue the old subagent.
- If only the format is off, do not relaunch. Record it in the step 2 check. If the same deviation repeats within a batch, list it as a prompt change candidate.
- If the rerun also fails, record the field as "failed" in the run log and tell the user. Try a third time only after the user decides.
- Never change the prompt for one field. Change it per batch, and record the change, the reason and the batches it applies to in the run log.
- A subagent that reports running out of web-search allowance has not failed. Its sources stay marked unverified in the title line and go to the step 3 recheck (`evidence.md` §5).
