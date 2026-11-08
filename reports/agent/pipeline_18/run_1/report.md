# Quality Assurance Report: Survey Scoring Pipeline

## Summary
We reviewed the scoring pipeline output (`pipeline_output.csv`) against `raw_responses.csv` using scoring guides and data notes for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES). 

When questionnaires were fully answered (missing = 0), the pipeline matched our independent reference scorer 100% across all items, reverse-codings, total scores, severity bands, and self-harm flags. However, we identified a systematic issue in handling **missing data** (specifically when exactly one question is skipped).

## Key Findings

### 1. Missing Data Handling (Proration Failure)
* **Instruments affected:** PHQ-9 (94 rows), GAD-7 (64 rows), RSES (71 rows).
* **Description:** According to the study protocol in `data_notes.md`, if exactly one question is unanswered (-9), the score should be scaled up (prorated) by taking the sum of answered items, multiplying by the total number of items, dividing by the number of items answered, and rounding half-ups up to the nearest whole number.
* **Pipeline behavior:** The pipeline correctly identifies that one item is missing and sets `*_prorated = True`, but **fails to apply the scaling-up formula**. Instead, it computes the total simply as the unadjusted sum of the answered items. Consequently, total scores (and resulting severity bands) are understated for any participant with exactly one missing response.

---
*Verdict:* **issues_found**
