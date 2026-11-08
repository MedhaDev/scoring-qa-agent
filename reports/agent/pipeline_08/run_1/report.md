# QA Report: Survey Scoring Pipeline

**Verdict:** Pass

## Summary
The scoring pipeline output (`pipeline_output.csv`) was compared row-by-row and column-by-column against an independent scoring script written strictly according to the data notes and scoring guides for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES).

All 505 respondents and all output columns (`phq9_total`, `phq9_band`, `phq9_prorated`, `phq9_self_harm_flag`, `gad7_total`, `gad7_band`, `gad7_prorated`, `rses_total`, `rses_prorated`) match the independent scoring script with 100% precision.

## Rules Verified
- **PHQ-9:** Sum of items 1–9, proper handling of missing data (proration for 1 missing item with half-up rounding; exclusion for $\ge 2$ missing items), severity cutpoints (0–4 none-minimal, 5–9 mild, 10–14 moderate, 15–19 moderately severe, 20+ severe), exclusion of difficulty question, and self-harm flag based on question 9.
- **GAD-7:** Sum of items 1–7, missing data rules, severity cutpoints (0–4 minimal, 5–9 mild, 10–14 moderate, 15–21 severe).
- **RSES:** Correct identification and reverse-scoring of negatively worded items (3, 5, 8, 9, 10), missing data rules, and total score calculation (0–30).
