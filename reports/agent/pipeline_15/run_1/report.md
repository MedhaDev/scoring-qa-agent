# QA Report: Survey Scoring Pipeline

## Overview
We performed a comprehensive quality audit of `pipeline_output.csv` against `raw_responses.csv` using independent scoring logic implemented strictly according to the scoring guides and data notes for PHQ-9, GAD-7, and RSES.

## Summary of Findings
Out of 10 output columns across 505 respondents (5,050 total data points), **5,035 data points matched our reference scorer perfectly**. 

We identified exactly **one root-cause error** in the pipeline:
- **PHQ-9 Severity Band Cutoff Boundary Error (`phq9_band`)**: For participants with a PHQ-9 total score of exactly 10, the pipeline assigns the severity band `"mild"` instead of `"moderate"`. 

### Detailed Findings

#### 1. PHQ-9 Severity Band Cutoff Error
- **Instrument**: PHQ-9
- **Category**: `cutoff_bands`
- **Affected Columns**: `phq9_band`
- **Rows Affected**: 15 respondents (e.g., `R0038`, `R0044`, `R0091`, `R0117`, `R0191`, `R0198`, `R0222`, `R0374`, `R0388`, `R0391`, `R0396`, `R0416`, `R0442`, `R0465`, `R0501`)
- **Description**: The PHQ-9 scoring guide explicitly states that cutpoints are at 5, 10, 15, and 20, and that a score sitting **exactly on a cutpoint belongs to the higher group** (i.e., a score of 10 is `"moderate"`, not `"mild"`). The pipeline incorrectly treats a score of 10 as upper-bounded by `"mild"` (`score < 10` vs `score <= 9`), resulting in 15 misclassified respondents.
- **Confirmation**: Confirmed by testing a scoring function incorporating the `< 10` boundary condition, which reproduced the pipeline's output with 100% exactness.

## Other Aspects Verified (Passed)
- **Reverse Coding**: RSES items 3, 5, 8, 9, and 10 were correctly reverse-coded (`3 - stored_value`).
- **Missing Data & Prorating**: Missing values (`-9`) and rules for 0 missing items, 1 missing item (scaling up with half-rounding up), and 2+ missing items (blank output) were applied correctly across all three instruments.
- **Self-Harm Flag**: `phq9_self_harm_flag` was correctly calculated based on item 9.
- **GAD-7 and RSES Totals and Bands**: All GAD-7 totals, severity bands, prorating flags, and RSES totals and prorating flags matched our independent reference scorer perfectly.

## Verdict
**issues_found** (1 finding confirmed)
