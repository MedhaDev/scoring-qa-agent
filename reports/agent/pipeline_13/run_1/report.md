# QA Scoring Pipeline Report

We performed a comprehensive audit of `pipeline_output.csv` against `raw_responses.csv` using the scoring guides and data notes for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES).

## Summary
- **GAD-7**: Passed with 0 mismatches across all columns (`gad7_total`, `gad7_band`, `gad7_prorated`).
- **RSES**: Passed with 0 mismatches across all columns (`rses_total`, `rses_prorated`).
- **PHQ-9**: Found discrepancies in 131 rows for `phq9_total`, 39 rows for `phq9_band`, and 20 rows for `phq9_prorated`. Specifically, the pipeline fails to properly prorate scores when exactly one item (such as `phq9_8`) is skipped, incorrectly returning `NaN` instead of prorating. The `phq9_self_harm_flag` passed with 0 mismatches.

## Recommendations
- Fix the PHQ-9 missing data handling routine in the scoring pipeline so that single missing items are correctly prorated according to study protocol.
