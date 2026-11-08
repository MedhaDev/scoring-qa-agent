# QA Report: Survey Scoring Pipeline

We audited the scoring pipeline output (`pipeline_output.csv`) against the raw responses (`raw_responses.csv`) and the scoring guides/data notes for PHQ-9, GAD-7, and the Rosenberg Self-Esteem Scale (RSES).

## Verdict
**issues_found**

## Summary of Findings
1. **Missing Data / Prorated Flag Issue (`missing_data`)**: 
   - Across all three questionnaires (`phq9_prorated`, `gad7_prorated`, `rses_prorated`), the pipeline sets the prorated indicator to `True` for every single participant who receives a total score, even when zero items were skipped. According to the data notes, `_prorated` should only be `True` when exactly one question was skipped and the score was scaled up, and `False` when all questions were answered.
