# Codex adapter

How to launch investigators, judges and recheckers with the Codex CLI. Read it in steps 1, 2 and 3. For an interactive pane instead of `codex exec`, see `adapter-interactive-pane.md`.

## 1. Launch

Run one new `codex exec` session per field. Investigators, judges and recheckers all use the same form. Render the role's template first; the rendered prompt names the material to read and the one output file.

```sh
codex exec -m <model> -c model_reasoning_effort=<effort> -s workspace-write -C <root> --skip-git-repo-check -o <last-reply file> < <prompt file>
```

`-o` saves the last chat reply. `{output_path}` inside the prompt is where the report or judge JSON goes. Keep the two files separate. Never let an investigator read other fields' or other models' reports. Give a judge the report to judge and the reference material; give a rechecker the list of sources and the recheck questions.

Sequential example. Replace the values with real paths and models, and prepare the folders and prompts first. `RUN` must be a new folder for every call. For judges and rechecks, change `prompts` and `reports` to that role's input and output paths.

```bash
#!/bin/bash
ROOT='/absolute/project/path'
RUN='/absolute/new/run/folder'
MODEL='<model id>'
EFFORT='high'
mkdir -p "$RUN/logs"
for slug in philosophy-epistemology cognitive-psychology; do
  prompt="$RUN/prompts/$slug.txt"
  report="$RUN/reports/$slug.md"
  last="$RUN/logs/$slug.last.md"
  log="$RUN/logs/$slug.log"
  test -s "$prompt" || { echo "missing prompt: $prompt"; exit 1; }
  test ! -e "$report" && test ! -e "$last" && test ! -e "$log" || {
    echo "earlier results exist: use a new run folder"; exit 1;
  }
  codex exec -m "$MODEL" -c "model_reasoning_effort=$EFFORT" \
    -s workspace-write -C "$ROOT" --skip-git-repo-check \
    -o "$last" < "$prompt" > "$log" 2>&1
  rc=$?
  echo "$slug exit=$rc"
  test "$rc" -eq 0 && test -s "$report" || exit 1
  head -n 3 "$report"
  wc -c < "$report"
done
```

Web search follows the `web_search` setting of the active config: `live` searches in real time, `cached` uses cached search, `disabled` turns it off. Shell network access and the web search tool are separate things. Writing "web search allowed" in a prompt does not change the run settings. Check run options in the Codex CLI documentation for your version.

For parallel runs, give every field, role and attempt its own prompt, report, last-reply and log path. Never let several sessions write the same result file or a shared ledger. Choose the number of parallel runs while watching provider limits, search limits, cost and real processing time.

## 2. Model selection

Check your Codex installation's model catalog or config for the model IDs available to you. As an example only, one installation kept a catalog JSON at `~/.codex/opencodex-catalog.json` and stored IDs under a `slug` key; your path and keys may differ. A model listed in a catalog is not proof that your account can call it.

```sh
python3 -I -c 'import json,pathlib,sys; d=json.loads(pathlib.Path(sys.argv[1]).expanduser().read_text()); print("\n".join(m.get("id") or m["slug"] for m in d["models"]))' '<path to your catalog JSON>'
```

Set reasoning effort like `-c model_reasoning_effort=high`. Allowed values differ by model; if the catalog lists supported reasoning levels, pick one from there. Render `{model}` and `{effort}` with the same values as the real options. Do not confuse a file-safe folder name (for example `gpt-6-1-sol`) with the model ID (`gpt-6.1-sol`).

Observed time per report and search counts: see `evidence.md` §2. They describe one day's material and settings, not a guarantee.

Unverified: the parallel run limit. Reason: the provider's and account's maximum number of concurrent runs was not measured.

Unverified: other sandbox modes. Reason: the trials used `workspace-write` only.

## 3. Collecting files

Check the exit code and the result file together. A last reply ending with the `chat_end` string does not mean the report file was created.

```sh
test -s "$report" && head -n 3 "$report" && wc -c < "$report"
```

The first three lines of a new report follow `report-format.md` §1: title with `title_marker`, `status_line`, `run_line`. Older baseline reports may lack the run line. `score_format.py` shows that as `run_line: null` and does not fail a report for that alone.

If a judge or recheck result is JSON, check that it parses: `python3 -I -m json.tool "$report" > /dev/null`. A format check does not prove the content is correct.

One line to read the token count and the number of web-search markers from a text log. Put the log path in `$log`.

```sh
python3 -I -c 'import pathlib,re,sys; t=pathlib.Path(sys.argv[1]).read_text(errors="replace"); n=re.findall(r"(?m)^tokens used\s*\n([\d,]+)",t); print("tokens used="+(n[-1] if n else "unverified")+", web search markers="+str(len(re.findall(r"(?m)^web search:",t))))' "$log"
```

`web search:` lines may include empty-response markers and URL opens as well as searches. The value is a count of marker lines, not of independent search requests or network calls. If the log format changes or a value is missing, read the raw log and leave it unverified.

## 4. Failure handling

1. If the exit code is not 0, read the log for the cause. Compare model and effort errors with the catalog. For permission, network or quota errors, do not repeat the same call until the condition is resolved.
2. If the exit code is 0 but the result is missing or empty, treat it as a failure. Find the real save path in the last reply and the log. Collect any valid result that exists and do not run it again.
3. On a timeout, first check whether the original process ended. If it is still running, do not rerun with the same result path. Keep partial files and logs. Retry once with a new attempt folder and a new result path, after rendering the prompt again. If the same cause repeats, stop and report the cause and the condition needed.
4. A retry never changes model, effort or reading scope on its own. Check the new run's exit code, file existence, first three lines, size or JSON syntax again before collecting.

Known pitfall: if the project has a Stop hook from a work-logging tool, a Codex session may run the hook's requested command even though the prompt says not to. This was seen in real logs in the 2026-10-17 trial. Judge report success and hook activity separately. Do not change hooks or logging settings from this procedure.

Unverified: a fresh Codex session running this exact example. Reason: no new paid session was started while checking this adapter, and a local `codex exec --help` failed because the launcher lacked permission to its state folder. The command form was checked against the trial's sequential script and the CLI documentation.
