# Can an AI Agent Catch Silent Scoring Bugs?

I built an AI agent from scratch that reviews survey scoring code the way a careful data manager would, then tested it against a rule-based QA script on 22 scoring pipelines with planted bugs.

**Case study:** [read the full report](https://medhadev.github.io/scoring-qa-agent/case_study.html)

## What survey scoring is

Health and social research often measures things like depression or anxiety with short questionnaires. Each question is answered on a small scale, for example 0 = "not at all" to 3 = "nearly every day". **Scoring** turns a person's answers into one number and a label that researchers analyse:

- add up the answers (the PHQ-9 depression questionnaire gives a total from 0 to 27)
- flip questions worded the opposite way ("I feel good about myself" vs "I feel like a failure")
- decide what to do when someone skips a question
- assign a label, such as "moderate depression" for a total of 10 to 14

Code does this for thousands of people at once. Think of an exam grading script: if one answer in the key is wrong, every student's grade is slightly off, yet nothing looks broken.

## Why this project exists

When scoring code has a mistake, nothing crashes. The scores look normal and flow into analysis, so people get labelled "mild" when they are "moderate", self-harm flags are missed, and wrong numbers reach papers. Teams check scoring with automated QA scripts and manual spot checks, but neither reliably catches a score that is plausible and wrong.

I wanted to know whether an AI agent could act as an independent second reviewer: one that reads the same scoring manual a person would, re-derives the rules itself, and explains what went wrong in plain language.

## Question

Can an AI agent catch survey scoring errors that standard QA scripts miss, without ever seeing the code it is checking?

## Hypothesis

Before running anything, I expected the agent to catch at least 90% of planted bugs with a false-alarm rate under 5%.

## What I built

- **The agent**, from scratch in plain Python with no agent framework. It gets only the scoring guides, the raw answers and the pipeline's output, never the code. It writes its own scorer, compares results column by column, forms a hypothesis about any mismatch, tests it by reproducing the pipeline's exact output, and writes a plain-English report. It runs on Gemini's free tier through a standard interface, so the model can be swapped in one line.
- **A test set:** 505 synthetic respondents on three public-domain questionnaires (PHQ-9, GAD-7, Rosenberg Self-Esteem Scale), and 22 copies of a correct scoring pipeline: 18 with one planted bug each and 4 with none, under shuffled names with a hidden answer key. Each bug reproduces a real-world failure mode from research data management.
- **A baseline:** a rule-based QA script running the checks teams typically automate.
- **An evaluation** that grades both against the answer key.

## Findings

- The agent detected all 18 bugs and named the right type of bug for 16.
- The rule-based script detected 12. It missed every bug that produces plausible-but-wrong scores, such as a question that was never flipped, or Python's `round()` rounding 10.5 down.
- Neither raised a false alarm on the 4 correct pipelines.
- The agent took about 42 seconds per review on a free model tier; the script took under a second.

**Hypothesis verdict: supported for the agent, not for the script.**

| | Rule-based script | AI agent |
|---|---|---|
| Bugs detected | 12 of 18 (67%) | 18 of 18 (100%) |
| Right type of bug named | 6 of 18 (33%) | 16 of 18 (89%) |
| False alarms | 0 of 4 | 0 of 4 |

## Recommendation

Keep scripted checks as the first line of QA, and run the agent as a second reviewer at high-risk moments: a change to the scoring code, a new round of data, a new questionnaire or translation. A data manager confirms each finding before anything is changed.

## Limitations

- One review per pipeline and only 4 correct pipelines, so the false-alarm result is encouraging rather than conclusive.
- The bugs and data are synthetic.
- The agent named the wrong bug type twice and added noisy extra findings once.

## What I'd do next

- A blind, rubric-scored gold-standard set of 40 new cases that I review by hand, with agent-human agreement measured by Cohen's kappa.
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
