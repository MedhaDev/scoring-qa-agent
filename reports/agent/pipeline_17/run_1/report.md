# Data Quality Assessment Report: Survey Scoring Pipeline

We audited `pipeline_output.csv` generated from `raw_responses.csv` using the scoring guides for PHQ-9, GAD-7, and the Rosenberg Self-Esteem Scale (RSES), along with the study data notes.

## Verdict
**Issues Found**

---

## Summary of Findings

### 1. PHQ-9 Self-Harm Flag Uses Item 8 Instead of Item 9 (`phq9_self_harm_flag`)
- **Instrument:** PHQ-9
- **Category:** Item Set
- **Affected Column:** `phq9_self_harm_flag`
- **Rows Affected:** 124 (out of 505)
- **Description:** According to the PHQ-9 scoring guide, the self-harm flag should be evaluated solely based on question 9 (`phq9_9`), which asks about thoughts of being better off dead or hurting oneself. However, the pipeline evaluates `phq9_self_harm_flag` using question 8 (`phq9_8`).
- **Evidence:** When evaluating against `phq9_9`, 124 rows mismatched. When evaluating against `phq9_8`, there is a 100% exact match across all 505 rows (including correct handling of missing values `-9` as `NaN`).

All other columns across PHQ-9, GAD-7, and RSES (totals, bands, proration, and missing data handling) scored correctly according to the protocol.
