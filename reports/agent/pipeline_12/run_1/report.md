# Quality Assurance Report: Survey Scoring Pipeline

We have completed a comprehensive QA review of `pipeline_output.csv` against `raw_responses.csv` using the scoring guides and data notes provided for PHQ-9, GAD-7, and the Rosenberg Self-Esteem Scale (RSES).

## Summary
- **Verdict**: `issues_found`
- **Total Findings**: 1 distinct root cause (affecting the GAD-7 severity band column).
- **Correctly Implemented**: PHQ-9 totals, bands, prorating, and self-harm flags; GAD-7 totals and prorating; RSES totals and prorating.

---

## Findings

### 1. Incorrect Severity Cutoffs and Labels for GAD-7 (`gad7_band`)
- **Instrument**: GAD-7
- **Category**: `cutoff_bands`
- **Affected Column**: `gad7_band`
- **Rows Affected**: 444 (out of 505)
- **Description**: The scoring pipeline applies PHQ-9 severity categories (`mild`, `moderate`, `moderately severe`, `severe`) to the GAD-7 scale, entirely omitting the `"minimal"` category (0–4) and introducing `"moderately severe"`, which does not exist for the GAD-7. Furthermore, the score ranges used by the pipeline are incorrect (0–5 for mild, 6–10 for moderate, 11–15 for moderately severe, and 16–21 for severe) instead of the official GAD-7 cutpoints (0–4 minimal, 5–9 mild, 10–14 moderate, 15–21 severe).
- **Evidence**: For example, participant `R0001` has a GAD-7 total score of 1.0. According to the GAD-7 scoring guide, a score of 1 falls into the 0–4 range and should be labeled `"minimal"`. The pipeline incorrectly labels this participant as `"mild"`. Across the dataset, 444 participants with valid GAD-7 scores receive incorrect severity bands due to this mapping error.
- **Confirmation**: Re-running the pipeline's exact band assignment logic (`<= 5` mild, `<= 10` moderate, `<= 15` moderately severe, `> 15` severe) reproduces the pipeline output with 0 mismatches.

---

## Scoring Rules Understood & Verified
- **PHQ-9**: Sum of 9 items (0–3 scale). 1 missing item is scaled up with half-rounding always rounding up. 2+ missing items result in blank total and band. Self-harm flag (`phq9_self_harm_flag`) correctly flags item 9 > 0 independently of missing item count. Severity bands follow standard PHQ-9 cutpoints with upper bound inclusion.
- **GAD-7**: Sum of 7 items (0–3 scale). Missing item rules and rounding align with protocol. Total score calculation and prorating verified 100%.
- **RSES**: Items 3, 5, 8, 9, and 10 correctly reverse-scored ($3 - v$). Total sum (0–30) and prorating verified 100%.
