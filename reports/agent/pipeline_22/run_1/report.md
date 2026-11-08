# Quality Assurance Report: Survey Scoring Pipeline

**Verdict:** `pass`

## Summary
The scoring pipeline output (`pipeline_output.csv`) was rigorously evaluated against `raw_responses.csv` using a custom Python scorer built strictly according to the scoring guides and data notes for PHQ-9, GAD-7, and the Rosenberg Self-Esteem Scale (RSES). 

Every column and row in `pipeline_output.csv` matched our independent scorer's output with 100% precision (0 differences across all 505 respondents and 9 output columns).

## Rules Applied and Verified
1. **Item Sets & Questionnaires:**
   - **PHQ-9:** Items 1 through 9 (`phq9_1` to `phq9_9`) scored correctly on 0–3 scales. `phq9_difficulty` correctly excluded from total.
   - **GAD-7:** Items 1 through 7 (`gad7_1` to `gad7_7`) scored correctly on 0–3 scales.
   - **RSES:** Items 1 through 10 (`rses_1` to `rses_10`) scored correctly. University of Maryland item numbering applied (`3, 5, 8, 9, 10` reverse-scored as `3 - value`).

2. **Missing Data & Prorating:**
   - `-9` values correctly treated as missing/unanswered.
   - 0 missing items: summed normally, `prorated = False`.
   - Exactly 1 missing item: prorated correctly (scaled up by $N/(N-1)$ and rounded half-up where `.5` rounds up), `prorated = True`.
   - $\ge 2$ missing items: totals and derived columns correctly left blank (`NaN`).

3. **Severity Bands & Flags:**
   - **PHQ-9 Bands:** Correct thresholds (0–4 none-minimal, 5–9 mild, 10–14 moderate, 15–19 moderately severe, 20+ severe).
   - **GAD-7 Bands:** Correct thresholds (0–4 minimal, 5–9 mild, 10–14 moderate, 15–21 severe).
   - **PHQ-9 Self-Harm Flag:** Correctly set to `True` if `phq9_9` $\ge 1$, `False` if `0`, and blank if `phq9_9` was missing.
