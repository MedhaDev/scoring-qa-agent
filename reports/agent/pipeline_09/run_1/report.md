# QA Scoring Report

We conducted a comprehensive audit of `pipeline_output.csv` against `raw_responses.csv` using scoring implementations derived strictly from the study's guides and data notes (`phq9_scoring_guide.md`, `gad7_scoring_guide.md`, `rses_scoring_guide.md`, and `data_notes.md`).

## Executive Summary
- **Verdict**: Issues found
- **RSES**: 100% match across all 505 participants for both `rses_total` and `rses_prorated`.
- **PHQ-9**: 6 discrepancies found in `phq9_total` and `phq9_band`. All other columns (`phq9_prorated`, `phq9_self_harm_flag`) match 100%.
- **GAD-7**: 2 discrepancies found in `gad7_total`. All other columns (`gad7_band`, `gad7_prorated`) match 100%.

## Detailed Findings

### 1. PHQ-9 Prorated Half-Integer Rounding Mismatch (`missing_data`)
- **Instrument**: PHQ-9
- **Columns**: `phq9_total`, `phq9_band`
- **Rows affected**: 6 (Respondent IDs: `R0028`, `R0122`, `R0243`, `R0259`, `R0425`, `R0502`)
- **Description**: According to the data notes, when exactly one question is skipped, scores are scaled up (`sum * 9 / 8`) and rounded to a whole number with halves always rounding up (e.g. 4.5 becomes 5). The pipeline implemented standard round-half-to-even (Python `round()`), which rounds 4.5 down to 4. Consequently, these participants received a total of 4 instead of 5, and their severity band was incorrectly evaluated as `none-minimal` instead of `mild`.

### 2. GAD-7 Prorated Half-Integer Rounding Mismatch (`missing_data`)
- **Instrument**: GAD-7
- **Columns**: `gad7_total`
- **Rows affected**: 2 (Respondent IDs: `R0328`, `R0502`)
- **Description**: Similarly, for GAD-7 prorated scores (`sum * 7 / 6`), a sum of 9 yields 10.5. The study rules state that halves round up (10.5 becomes 11), but the pipeline used round-half-to-even, scoring these participants as 10 instead of 11.
