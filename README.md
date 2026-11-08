# Can an AI Agent Catch Silent Scoring Bugs?

An evaluation of an AI QA agent against a rule-based script on survey scoring pipelines with planted bugs.

**Case study:** [read the full report](https://medhadev.github.io/scoring-qa-agent/case_study.html)

## Question

Can an AI agent catch survey scoring errors that standard QA scripts miss, without ever seeing the code it is checking?

## Hypothesis

Before running anything, I expected that an agent that reads the scoring rules, re-scores the raw data independently, and investigates mismatches would catch at least 90% of planted bugs with a false-alarm rate under 5%.

## Approach

- Questionnaires: PHQ-9, GAD-7 and the Rosenberg Self-Esteem Scale, all public domain. Scoring rules checked against official sources.
- Data: 505 synthetic respondents (fixed seed) with skipped answers and edge cases on the severity cutoffs. No real participant data.
- Test set: 22 copies of a correct scoring pipeline, 18 with one planted bug each and 4 with none, under shuffled names with a hidden answer key. Each bug reproduces a real-world failure mode from research data management.
- Compared two checkers: a rule-based QA script (the checks teams typically automate) and an AI agent that sees only the scoring guides, the raw data and the pipeline output, never the code.

## Findings

- The agent detected all 18 bugs and named the right type of bug for 16.
- The rule-based script detected 12. It missed every bug that produces plausible-but-wrong scores, such as a missed reverse-coded item or Python's `round()` rounding 10.5 down.
- Neither raised a false alarm on the 4 correct pipelines.
- The agent took about 42 seconds per audit on a free model tier; the script took under a second.

**Hypothesis verdict: supported for the agent, not for the script.**

| | Rule-based script | AI agent |
|---|---|---|
| Bugs detected | 12 of 18 (67%) | 18 of 18 (100%) |
| Right type of bug named | 6 of 18 (33%) | 16 of 18 (89%) |
| False alarms | 0 of 4 | 0 of 4 |

## Recommendation

Keep scripted checks as the first line of QA, and run the agent as a second reviewer at high-risk moments: a change to the scoring code, a new data wave, a new instrument or translation. A data manager confirms each finding before anything is changed.

## Limitations

- One audit per pipeline and only 4 correct pipelines, so the false-alarm result is encouraging rather than conclusive.
- The bugs and data are synthetic.
- The agent named the wrong bug type twice and added noisy extra findings once.

## What I'd do next

- A blind, rubric-scored gold-standard set of 40 new cases, with agent-human agreement measured by Cohen's kappa.
- Repeat runs to measure consistency.
- Compare a lighter and a stronger model on accuracy, speed and cost.

## How to run

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then add a free Gemini API key
python harness/generate_data.py
python harness/make_copies.py
python harness/run_pipelines.py
python harness/check_harness.py
python -m evaluation.run_all --checker rule_based
python -m evaluation.run_all --checker agent
python -m evaluation.evaluate
python -m evaluation.plot_results
quarto render
```
