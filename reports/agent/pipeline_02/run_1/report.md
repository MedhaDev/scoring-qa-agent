# Quality Assurance Report: Survey Scoring Pipeline

We conducted a comprehensive QA review of `pipeline_output.csv` against `raw_responses.csv`, guided by the data notes and official scoring guides for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES).

## Summary
- **Verdict:** `issues_found`
- **Instruments affected:** PHQ-9, GAD-7, RSES
- **Root cause category:** `missing_data` across all three instruments.

## Detailed Findings

### 1. PHQ-9: Incorrect handling of 2 missing items
- **Columns affected:** `phq9_total`, `phq9_band`, `phq9_prorated`
- **Rows affected:** 10 respondents (e.g., `R0032`, `R0123`, `R0143`, `R0251`, `R0324`, `R0336`, `R0393`, `R0454`, `R0482`, `R0503`).
- **Description:** Per study protocol in `data_notes.md`, if **two or more** questions are unanswered, the participant should receive no total (leaving the total, band, and prorated flag blank). However, the pipeline incorrectly applies prorating when participants have 2 missing items (scaling up by $\frac{9}{7}$ and rounding). Note that when participants had 3 or 4 missing items, the pipeline correctly returned blank.

### 2. GAD-7: Incorrect handling of 2 missing items
- **Columns affected:** `gad7_total`, `gad7_band`, `gad7_prorated`
- **Rows affected:** 11 respondents (e.g., `R0037`, `R0048`, `R0120`, `R0138`, `R0193`, `R0211`, `R0259`, `R0282`, `R0308`, `R0500`, `R0503`).
- **Description:** Similar to the PHQ-9 error, the pipeline incorrectly prorates GAD-7 scores when exactly two items are skipped (scaling up by $\frac{7}{5}$ and rounding) instead of treating 2 or more missing items as invalid. (3 or 4 missing items correctly resulted in blank).

### 3. RSES: Incorrect handling of 2 missing items
- **Columns affected:** `rses_total`, `rses_prorated`
- **Rows affected:** 13 respondents (e.g., `R0024`, `R0095`, `R0122`, `R0157`, `R0177`, `R0198`, `R0223`, `R0312`, `R0429`, `R0431`, `R0440`, `R0478`, `R0505`).
- **Description:** The pipeline incorrectly prorates RSES scores when exactly two items are skipped (scaling up by $\frac{10}{8}$ and rounding) instead of assigning blank totals for 2 or more missing items. (3 or 4 missing items correctly resulted in blank).

## Conclusion
The scoring pipeline correctly handles complete data, 1 missing item (prorating), and $\ge 3$ missing items (blank), but contains a systematic logic flaw where **2 missing items** are mistakenly prorated instead of being set to missing. We recommend updating the pipeline's missing-data threshold check from `n_missing >= 2` to properly invalidate any participant with $\ge 2$ missing items across all questionnaires.
