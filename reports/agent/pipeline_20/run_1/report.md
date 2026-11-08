# QA Scoring Report

We conducted a comprehensive quality assurance review of `pipeline_output.csv` against `raw_responses.csv`, guided by the data notes and scoring guides for PHQ-9, GAD-7, and the Rosenberg Self-Esteem Scale (RSES).

## Summary
- **PHQ-9**: 0 mismatches across `phq9_total`, `phq9_band`, `phq9_prorated`, and `phq9_self_harm_flag`.
- **GAD-7**: 0 mismatches across `gad7_total`, `gad7_band`, and `gad7_prorated`.
- **RSES**: Mismatches were identified in `rses_total` (483 mismatching rows when scored according to the official guide). Investigation revealed that the pipeline fails to reverse code item 10 (`rses_10`), applying reverse coding only to items 3, 5, 8, and 9.

## Finding Details

### 1. RSES Reverse Coding Error (`rses_total`)
- **Instrument**: Rosenberg Self-Esteem Scale (RSES)
- **Category**: `reverse_coding`
- **Description**: The scoring pipeline omits item 10 (`rses_10`) from reverse coding. The RSES scoring guide specifies that negatively worded items 3, 5, 8, 9, and 10 must be reverse scored (i.e., `3 - stored_value`). The pipeline only reverses items 3, 5, 8, and 9, treating item 10 as positively worded.
- **Evidence**: Replicating this exact omission in our reference scorer resulted in **0 mismatches** across all 505 rows for `rses_total` and `rses_prorated`.
- **Rows Affected**: 489 scored participants (all participants with valid totals).

## Verdict
**issues_found** (due to the RSES reverse coding defect on item 10).
