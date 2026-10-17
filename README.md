# theory-sweep

A Claude Code and Codex skill that asks many LLM "discipline experts" to read one design document and propose theories from their field that the design could borrow.

One investigator per discipline (philosophy, accounting, control engineering, music, … 52 fields by default) reads your design document and writes a short, fixed-format report of theory-integration candidates with sources. One model merges the reports by design group and by cross-cutting problem. Scripts and a judge model check format, citations and whether each candidate really connects to a sentence in the design.

Every result carries the same status line: an AI survey and comparison proposal, not adopted, effectiveness not proven. The skill finds candidates. It does not prove that any of them works.

## What is in the repo

```
theory-sweep/            the skill folder (install this)
  SKILL.md               the procedure, steps 0–6
  references/            prompt templates, report format, field list, adapters, model notes, evidence
    strings/en.json      fixed report strings, English
    strings/ko.json      fixed report strings, Korean
  scripts/               render prompts, score format, check citations, count, compare models
README.md
LICENSE
```

## Install

```sh
git clone https://github.com/BUGGIEEEEE/theory-sweep theory-sweep-skill
# Claude Code
ln -s "$(pwd)/theory-sweep-skill/theory-sweep" ~/.claude/skills/theory-sweep
# Codex
ln -s "$(pwd)/theory-sweep-skill/theory-sweep" ~/.codex/skills/theory-sweep
```

Requirements: Python 3 (standard library only) and network access to Crossref, plus OpenAlex if you set a key. Skill folder locations can differ between tool versions; check your tool's documentation if the skill does not appear.

## Quick start

Ask your agent for a theory sweep, for example: "Run a theory sweep on docs/design.md." The skill then asks for these inputs in step 0.

| Input | Required | Example |
|---|---|---|
| Target documents and line ranges | yes | `docs/design.md L1–240` |
| Problem map: the design's group numbers and titles | yes | `1-1 Goals · 1-2 Users · 2-1 Data model …` |
| Output folder | yes | `reviews/theory-sweep/` |
| Fields | no (52 by default) | a subset of slugs from `references/field-list.md` |
| Common example scene rule | no | "how the work changes while building a small budget app" |
| Folders investigators must not open | no | earlier runs' reports |
| `lang` | no (`en`) | `en` or `ko` |
| Investigator, synthesis and judge models | yes, user choice | see `references/models.md` |

The run then goes:

0. **Prepare.** Check inputs and the field list, estimate size, and get your approval.
1. **Investigate.** Launch one investigator per field, in batches of 5–8.
2. **Quality check.** Score the format and stop after the first batch so you can adjust.
3. **Source check.** Machine-check citations against Crossref and OpenAlex, then recheck mismatches by web search.
4. **Synthesize.** Merge reports along two axes, then check the counts with a script.
5. **Pre-review.** You decide per top candidate: adoption candidate, defer or exclude.
6. **Register and hand off.** Write SHA-256 hashes and a handoff note.

Scripts can also be run by hand. Each one has `--help`.

```sh
python3 -I theory-sweep/scripts/render_prompt.py theory-sweep/references/field-prompt.md --lang en \
  --vars vars.json --fields cognitive-psychology --list theory-sweep/references/field-list.md \
  --out prompts/{slug}.txt
python3 -I theory-sweep/scripts/score_format.py reviews/theory-sweep/*.md --format table
python3 -I theory-sweep/scripts/bib_check.py reviews/theory-sweep/*.md --out bib.jsonl
python3 -I theory-sweep/scripts/count.py reviews/theory-sweep
```

## Language support

- The docs, templates and prompts are in English.
- `lang: en` (default) gives English reports. `lang: ko` gives Korean reports with Korean fixed strings.
- Fixed strings live in `references/strings/en.json` and `ko.json`. `references/report-format.md` shows them side by side.
- The scoring scripts detect each report's language from its status line or title.

## OpenAlex key (optional)

The citation check uses Crossref and, if a key is set, OpenAlex. Without a key, OpenAlex is skipped. In one observation it also rate-limited unkeyed requests for hours. Pass the key only as an environment variable.

```sh
export OPENALEX_API_KEY=...   # never write the key into a file in this repo, a prompt or a log
```

## Limits

- The model guidance comes from one small evaluation (5 models × 7 fields × 1 run, 2026-10-17). Model names and versions change, so re-evaluate with your own models. See `references/models.md` and `references/evidence.md`.
- Judge scores are sensitive to the judge model. Treat them as reference values; you make the final call.
- Standards and institutional documents are often missing from bibliographic databases and depend on the web recheck.
- Repeated proposals from the same model, reading and prompt are not independent evidence.
- Group numbers and "already met" marks are the investigators' self-reports.
- `axis=problem` (one investigator per problem instead of per field) is untested.

## License

MIT. See [LICENSE](LICENSE).

## 한국어

theory-sweep은 설계 문서 하나를 여러 학문 분야의 LLM 조사자에게 읽히는 Claude Code·Codex 스킬입니다. 각 조사자는 자기 분야에서 그 설계가 빌려 올 만한 이론 후보를 출처와 함께 보고합니다. 통합 모델은 보고들을 그룹별과 문제별 두 축으로 묶습니다. 스크립트와 판정 모델은 형식, 서지, 설계 문장과의 연결을 점검합니다. 결과는 모두 "AI 조사·비교 제안. 채택·효과 입증 아님." 지위입니다.

### 설치

```sh
git clone https://github.com/BUGGIEEEEE/theory-sweep theory-sweep-skill
# Claude Code
ln -s "$(pwd)/theory-sweep-skill/theory-sweep" ~/.claude/skills/theory-sweep
# Codex
ln -s "$(pwd)/theory-sweep-skill/theory-sweep" ~/.codex/skills/theory-sweep
```

필요한 것은 Python 3(표준 라이브러리만)과 Crossref 네트워크 접근입니다. OpenAlex 키를 설정하면 OpenAlex도 씁니다. 스킬 폴더 위치는 도구 판에 따라 다를 수 있습니다.

### 빠른 시작

에이전트에게 "docs/design.md로 theory sweep 해 줘"처럼 요청합니다. 0단계에서 스킬이 아래 값을 묻습니다.

- 대상 문서와 행 범위(필수)
- 문제 지도, 즉 설계의 그룹 번호와 제목(필수)
- 출력 폴더(필수)
- 분야(선택, 기본 52개)
- 공통 예시 장면 규칙(선택)
- 조사자가 열면 안 되는 폴더(선택)
- `lang`(선택, 기본 `en`)
- 조사·통합·판정 모델(사용자가 정함, `references/models.md` 참고)

진행 순서는 준비, 조사(5~8개 묶음), 첫 묶음 뒤 품질 점검, 출처 확인, 통합, 사전검토, 등록·인계입니다. 승인 전에는 조사자를 띄우지 않습니다. 후보의 채택·보류·제외는 사용자가 정합니다.

### 언어

- 문서와 지시문 틀은 영어입니다.
- `lang: ko`로 지정하면 보고가 한국어로 나오고 고정 문구도 한국어가 됩니다.
- 고정 문구는 `references/strings/ko.json`에 있습니다. 영어·한국어 대조표는 `references/report-format.md` §9에 있습니다.
- 채점 스크립트는 보고의 지위 줄이나 제목으로 언어를 자동으로 알아봅니다.

### OpenAlex 키(선택)

서지 대조는 Crossref를 쓰고, 키가 있으면 OpenAlex도 씁니다. 키가 없으면 OpenAlex는 건너뜁니다. 키는 환경 변수로만 넘기고 파일·지시문·로그에 쓰지 않습니다.

```sh
export OPENALEX_API_KEY=...
```

### 라이선스

MIT. [LICENSE](LICENSE)를 보세요.
