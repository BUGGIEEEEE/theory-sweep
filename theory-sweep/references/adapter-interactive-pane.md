# Running investigators in an interactive terminal pane (e.g., Herdr)

Optional path. Use it when a session needs extra instructions mid-run, or when your environment requires sub-sessions to be opened interactively. Instead of `codex exec`, run an interactive agent (for example Codex) in a new terminal pane, send it the rendered prompt, and collect its files.

The commands below use Herdr, a terminal multiplexer for coding agents, as one example. Any multiplexer that can split a pane, start an agent, send a prompt and read pane output works the same way. Use the same rendered prompts, models and output checks as `adapter-codex.md` §1–§3.

## 1. Launch

Confirm you are inside the multiplexer before using this path. For Herdr: `test "${HERDR_ENV:-}" = 1`. If it fails, do not use this path.

Split to the right if the current pane is wide, or down if it is narrow or tall. Use `ROOT`, `MODEL` and `EFFORT` from `adapter-codex.md` §1. Replace the pane ID, the unique name and the prompt path with real values.

```sh
herdr pane layout --current
herdr pane split --current --direction right --cwd "$ROOT" --no-focus
# Put .result.pane.pane_id from the reply into PANE.
PANE='<returned pane id>'
NAME='ts-philosophy-01'
END='<chat_end string for this role, from strings/<lang>.json>'
herdr agent start "$NAME" --kind codex --pane "$PANE" --timeout 60000 -- \
  -m "$MODEL" -c "model_reasoning_effort=$EFFORT" -s workspace-write -C "$ROOT"
herdr agent prompt "$NAME" "Read /absolute/path/to/rendered-prompt.txt and carry it out. After saving every result file, print $END on its own line as the last line of your reply."
```

If your environment has a work-logging convention for sub-sessions (for example a required first line naming the parent task), follow it in the first message. Otherwise send only the prompt.

Use a new pane and a unique name for every field, role and attempt. Never reuse a pane.

## 2. Collecting results

Poll for result files or a completion marker. This is the primary method. Name the expected result files and the completion marker in the prompt, then wait, with an upper time limit, until the expected files exist or the marker appears in the pane output.

This example waits up to 15 minutes for the marker on its own line.

```sh
herdr pane wait-output "$PANE" --regex "(?m)^${END}[[:space:]]*\$" \
  --source recent-unwrapped --lines 120 --timeout 900000
herdr pane read "$PANE" --source recent-unwrapped --lines 120
```

`wait-output` also searches existing output immediately before polling, so make sure the marker comes from this run. To wait on file count instead, check `ls <output folder>` every 30 seconds and count only this run's expected files, again with a total time limit. After the marker or the files appear, check each output file's existence, first three lines, size or JSON syntax as in `adapter-codex.md` §3. A timeout is not completion: inspect the current files and pane output, and do not launch a duplicate.

Agent status waits are a secondary aid for seeing that work started or changed state. Confirm `working` first, then wait for `idle`, `done` or `blocked`.

```sh
herdr agent wait "$NAME" --until working --timeout 90000
herdr agent wait "$NAME" --until idle --until done --until blocked --timeout 60000
herdr agent get "$NAME"
```

Repeat `--until` for each state. Both `agent wait` and `pane wait-output` wait forever if `--timeout` is omitted. `blocked` means waiting for approval or an answer; `unknown` is not evidence of completion. Even when a status wait ends, still poll for files or the marker and run the file checks. Send mid-run instructions with `herdr agent prompt "$NAME" '<instruction>'`.

## 3. Confirmed pitfalls

1. **A wait right after prompting returns at once.** Calling a plain `agent wait` right after sending the prompt can see the agent still `idle` and return before work starts.
2. **Status flaps during long, tool-heavy runs.** The agent alternates between `working` and `idle`, so an `idle` wait after `working` can also return before the work is done. In one observed run, zero result files existed at that moment. Poll for output files or a completion marker instead.

## 4. Cautions

An agent can stall at an approval prompt. Before running, check the agent's non-interactive approval settings and allowed scope. If `blocked` or a start failure appears, read the cause with `agent get` or `agent read` and get any decision the user must make. Never answer approval prompts on the user's behalf.

## 5. Verified and unverified

Verified on 2026-10-17 in a real coordinating session with Herdr and Codex:
- Pane creation returned `result.pane.pane_id`.
- Agent start reported `interactive_ready: true` and `agent_status: idle`. Start options were `--timeout 60000 -- -m <model> -c model_reasoning_effort=high -s workspace-write -C <root>`.
- Sending the prompt returned immediately with the status still `idle` (pitfall 1).
- Status waits and result collection worked, with pitfall 2 observed.
- The `pane wait-output` syntax above was checked against the local `herdr pane wait-output --help`.

Unverified:
- Opening the sub-session under a work-logging convention's first-line rule. Reason: the verified run used a first message that forbade logging commands instead.
- Whether approval settings actually took effect. Reason: not tested.
- The number of panes that can run at once. Reason: not tested.
- Other multiplexers. Reason: only Herdr was used.
