# QA Report: Survey Scoring Pipeline

We audited the scoring pipeline output (`pipeline_output.csv`) against `raw_responses.csv` using the provided scoring guides and data notes for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES).

## Summary of Findings

1. **PHQ-9 and GAD-7 Item Scoring (Off-by-One)**:
   - The pipeline incorrectly treats PHQ-9 and GAD-7 item responses as scored 1 to 4 instead of 0 to 3 (+1 added per item). This inflates PHQ-9 totals by exactly 9 and GAD-7 totals by exactly 7 across all valid respondents.
2. **PHQ-9 and GAD-7 Severity Bands (Cutoff Bands)**:
   - Because totals are inflated by +9 / +7, applying standard severity cutoffs directly to these shifted totals leads to widespread misclassification of severity bands (e.g., true score 0 resulting in total 9 being labeled as 'mild' instead of 'none-minimal').
3. **PHQ-9 Self-Harm Flag (Logic Error / Other)**:
   - The pipeline flags participants as `True` for self-harm whenever question 9 is answered, even when answered 0 ("not at all"). Only answers of 1, 2, or 3 should trigger the flag.
4. **RSES Total Scores (Reverse Coding / Prorating)**:
   - 71 rows show minor score discrepancies (+/- 1 or 2 points) on the Rosenberg Self-Esteem Scale totals.
