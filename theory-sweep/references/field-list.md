# Field list (52 by default)

This list is a representative selection of fields, not every discipline. Check it for completeness once in step 0 before use.

## How to use

- The list holds 50 fields from an earlier run plan plus 2 added later (LLM agent engineering and evaluation research; resilience engineering).
- The "first question" column was written for the design of an AI development tool. It is an example. For a different target, use an adapted copy made in step 0.
- `scripts/render_prompt.py --list` reads the `slug`, `field (en)`, `field (ko)` and `extra clause (en)` columns. `--lang en` fills `{field}` from `field (en)`, `--lang ko` from `field (ko)`. Keep slugs unchanged; they are stable IDs that let reports from different runs line up.
- The `extra clause (en)` cell goes into the prompt as is, so write complete sentences. Never use the vertical bar or curly braces in a cell. `none` means no clause.
- `kind` is a human label: none / no analogy / precedent overlap / scope note.
- For rows of kind "precedent overlap", render from a copy that appends the actual precedent (file and line range, or an adjacent field's candidate titles) to the end of the extra clause. If there is no precedent, change that row's clause to `none`.

## Completeness check

1. For each group (humanities, social sciences, natural sciences, formal sciences, engineering, applied and practice, arts), name 2–3 fields missing from this table and show them to the user once.
2. Add rows only for the fields the user picks. Make slugs from lowercase English letters, digits and hyphens.
3. Add finer subfields (e.g. contract theory within economics) only after seeing results. Do not grow the list in the first run.
4. Record the result (fields added, candidates not added and why) in the run log.

## Table

| group | field (en) | field (ko) | slug | first question (en) | kind | extra clause (en) |
|---|---|---|---|---|---|---|
| Humanities | Philosophy (epistemology, philosophy of science) | 철학(인식론·과학철학) | philosophy-epistemology | Falsification, levels of evidence, criteria for "not proven" | none | none |
| Humanities | Ethics and responsibility theory | 윤리학·책임 이론 | ethics-responsibility | Delegation and attribution of responsibility, the user's final judgment | none | none |
| Humanities | Logic and argumentation theory | 논리학·논증 이론 | logic-argumentation | Argument structure of critical review, counterexample generation | none | none |
| Humanities | History and source criticism | 역사학·사료 비판 | history-source-criticism | Judging the authority of originals, corrections and versions | none | none |
| Humanities | Linguistics and pragmatics | 언어학·화용론 | linguistics-pragmatics | Meaning loss and compression in prompts and reports | none | none |
| Humanities | Rhetoric and narratology | 수사학·서사학 | rhetoric-narratology | Structures that carry the "why" in cards and explanations | none | none |
| Humanities | Education and learning science | 교육학·학습과학 | education-learning-science | Conditions and assessment of two learning goals | none | none |
| Humanities | Religious studies and practice traditions | 종교학·수행 전통 | religious-studies-practice | Discipline and review rituals, the structure of repeated practice | no analogy + scope note | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. Do not look at religious claims themselves. Look at the procedures, records and review structures that practice traditions built, such as the daily schedule of a monastic rule, chapter meetings, novitiate periods and the examination of conscience. |
| Humanities | Translation studies | 번역학 | translation-studies | Transformation without meaning loss, review methods | none | none |
| Social sciences | Economics (transaction cost, information economics, mechanism design) | 경제학(거래비용·정보경제·메커니즘 설계) | economics-transaction-cost-mechanism-design | Monitoring cost, reporting incentives, delegation contracts | none | none |
| Social sciences | Management and organization theory | 경영학·조직이론 | management-organization-theory | Chain of management, span of control, coordination cost | none | none |
| Social sciences | Public administration and political science (bureaucracy, delegation) | 행정학·정치학(관료제·위임) | public-administration-delegation | Delegation of authority and responsibility, approval procedures | none | none |
| Social sciences | Law (procedure, evidence, liability) | 법학(절차·증거·책임) | law-procedure-evidence | Standards of evidence, adversarial procedure, legal force of records | none | none |
| Social sciences | Sociology (institutions, trust) | 사회학(제도·신뢰) | sociology-institutions-trust | Trust formation, institutionalized review | none | none |
| Social sciences | Cognitive psychology | 인지심리학 | cognitive-psychology | Comprehension bottlenecks, working memory, attention | none | none |
| Social sciences | Behavioral economics and decision theory | 행동경제학·의사결정론 | behavioral-economics-decision | Automation bias, how options are presented | none | none |
| Social sciences | Anthropology (practice, apprenticeship) | 인류학(실천·도제) | anthropology-apprenticeship | Apprenticeship learning, transfer of tacit knowledge | none | none |
| Social sciences | Communication studies | 커뮤니케이션학 | communication-studies | Reporting systems, noise, propagation of corrections | none | none |
| Social sciences | Military science and strategy | 군사학·전략학 | military-strategy | Mission command, red teaming | precedent overlap | Part of this field is already covered by the existing reference section of the design document. Use the already-met marker for what is already reflected, and look for candidates in concrete methods beyond it. |
| Social sciences | Geography and cartography | 지리학·지도학 | geography-cartography | Choosing the level of abstraction, legends, scale | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Natural sciences | Physics (thermodynamics, control) | 물리학(열역학·제어) | physics-thermodynamics-control | Accumulating entropy, feedback stability | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Natural sciences | Biology (evolution, immunity, homeostasis) | 생물학(진화·면역·항상성) | biology-evolution-immunity-homeostasis | Variation and selection, detecting foreign bodies, recovery | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Natural sciences | Ecology and complex systems | 생태학·복잡계 | ecology-complex-systems | Local optima, cascading failure, resilience | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Natural sciences | Neuroscience | 신경과학 | neuroscience | Attention and memory consolidation, sleep or reset analogies | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Natural sciences | Medicine and clinical practice (diagnosis, checklists, patient safety) | 의학·임상(진단·체크리스트·환자안전) | medicine-diagnosis-checklist-safety | Differential diagnosis, checklists, incident reporting | none | none |
| Natural sciences | Earth science and meteorology (forecasting) | 지구과학·기상(예보) | geoscience-meteorology-forecasting | Expressing uncertainty, ensemble forecasting | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Formal sciences | Mathematics (probability, statistics, Bayes) | 수학(확률·통계·베이즈) | mathematics-probability-bayes | Updating evidence, sample inspection | none | none |
| Formal sciences | Game theory and social choice | 게임이론·사회선택 | game-theory-social-choice | Consensus among several reviewers, incentive compatibility | none | none |
| Formal sciences | Theory of computation and formal verification | 계산이론·형식검증 | computation-formal-verification | Invariants, state-transition verification | none | none |
| Formal sciences | Information theory | 정보이론 | information-theory | Compression loss, channel capacity (of reports) | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Formal sciences | Systems theory and cybernetics | 시스템이론·사이버네틱스 | systems-theory-cybernetics | Requisite variety, feedback loops | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Formal sciences | Operations research and queueing | 운용과학(OR)·대기행렬 | operations-research-queueing | Session assignment, bottlenecks, cost | none | none |
| Engineering | Software engineering | 소프트웨어공학 | software-engineering | Already core to the design (additions only) | precedent overlap | The design document and a precedent report already cover the basics of this field. Use the already-met marker for what the precedent covered, and propose only additions it did not cover. |
| Engineering | Systems and requirements engineering | 시스템공학·요구공학 | systems-requirements-engineering | Requirements tracing, V-model, acceptance criteria | precedent overlap | The basics of requirements traceability and configuration management were already judged in a precedent. Look for candidates in concrete methods beyond them. |
| Engineering | Control engineering | 제어공학 | control-engineering | Observers, stability, delay | precedent overlap | This field easily overlaps with physics (thermodynamics, control). Find candidates different from those that field covered. |
| Engineering | Reliability and safety engineering (FMEA, STAMP) | 신뢰성·안전공학(FMEA·STAMP) | reliability-safety-engineering | Failure modes, safety constraints, accident analysis | none | none |
| Engineering | Industrial engineering and human factors (HCI) | 산업공학·인간공학(HCI) | industrial-human-factors-hci | Workload, visibility, designing against error | precedent overlap | This field easily overlaps with cognitive psychology. Find candidates different from those that field covered. |
| Engineering | Quality management (TQM, Six Sigma) | 품질경영(TQM·식스시그마) | quality-management | Inspection versus prevention, process capability | none | none |
| Engineering | High-reliability organizations (aviation CRM, nuclear) | 고신뢰조직(항공 CRM·원자력) | high-reliability-organizations | Reporting culture, cross-checking, authority gradient | none | none |
| Engineering | Architecture and urban planning (pattern language) | 건축·도시계획(패턴 언어) | architecture-pattern-language | Pattern reuse, incremental growth | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Engineering | LLM agent engineering and evaluation research | LLM 에이전트 공학·평가 연구 | llm-agent-engineering-evaluation | Measurement basis for task size, external judgment of context loss, conditions under which review loops help, metrics for comparative experiments | none | none |
| Engineering | Resilience engineering | 레질리언스 공학 | resilience-engineering | Common causes of everyday adjustment and failure, the efficiency–thoroughness trade-off, signs of exhausted margins | precedent overlap | This field easily overlaps with high-reliability organizations, reliability and safety engineering, and ecology. Mark overlapping content only as overlapping with another field, without details. |
| Applied and practice | Accounting and auditing | 회계·감사학 | accounting-auditing | Ledgers, reconciliation, independent audit, sampling | none | none |
| Applied and practice | Project management | 프로젝트관리 | project-management | Rolling-wave planning, change control, baselines | precedent overlap | The design already holds the basics of rolling-wave planning, change control and baselines. Do not propose the basics again; look for concrete methods beyond them. |
| Applied and practice | Journalism and fact-checking | 저널리즘·팩트체킹 | journalism-fact-checking | Source grading, correction notices | none | none |
| Applied and practice | Library and archival science | 문헌정보·기록학 | library-archival-science | Records life cycle, principle of provenance, retention and disposal | none | none |
| Applied and practice | Sports coaching and training science | 스포츠 코칭·훈련학 | sports-coaching-training | Feedback cycles, overload and recovery | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Applied and practice | Design (design thinking, service design) | 디자인학(디자인 사고·서비스 디자인) | design-thinking-service-design | Exploring several directions, drafts, synthesis | none | none |
| Applied and practice | Criminal and accident investigation (forensics) | 범죄 수사·사고 조사(포렌식) | forensics-investigation | Tracing back to where an error began, chain of custody | none | none |
| Applied and practice | Navigation and exploration | 항해·탐험학 | navigation-exploration | Detecting drift from the goal, dead reckoning and correction | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Arts | Music (ensemble, improvisation) | 음악(앙상블·즉흥) | music-ensemble-improvisation | Role division and real-time coordination, signaling systems | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |
| Arts | Film and theater production management | 영화·연극 제작 관리 | film-theater-production | Coordinating roles, schedules and revisions, script version control | no analogy | Do not list candidates that stay at the level of analogy. List only what can be turned into an actual measurement or decision rule. |

## Notes on the values in this table

- The slugs match the file names of the earlier 52-field baseline reports. Keep them unchanged.
- The two added fields had no "first question" in the original plan. Their questions were shortened from the opening paragraphs of their baseline reports.
- Unverified: the original wording of the extra clauses used for the two added fields. Reason: the plan record says only that they used "the same template plus per-field clauses". The resilience engineering clause is inferred from the scope that report stated for itself.
- The military science row dropped a note specific to the original project from its first question. That situation moved into the extra clause (precedent overlap).
- The extra clauses are in English only. In a `--lang ko` run they stay English inside the prompt; the investigator still writes the report in Korean.
