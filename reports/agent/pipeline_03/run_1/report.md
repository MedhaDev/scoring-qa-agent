# Quality Assurance Report: Survey Scoring Pipeline

## Executive Summary

We conducted a comprehensive quality assurance review of `pipeline_output.csv` against `raw_responses.csv`, using the scoring guides and data notes provided for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES).

- **PHQ-9**: **Pass**. All total scores, severity bands (`phq9_band`), prorating flags (`phq9_prorated`), and self-harm flags (`phq9_self_harm_flag`) match our independent scorer exactly across all 505 respondents.
- **GAD-7**: **Pass**. All total scores, severity bands (`gad7_band`), and prorating flags (`gad7_prorated`) match our independent scorer exactly across all 505 respondents.
- **RSES**: **Issues Found**. The pipeline successfully implements the missing-data rule and prorating logic for RSES, but uses an incorrect reverse-coding formula for the negatively worded items.

---

## Detailed Findings

### 1. Rosenberg Self-Esteem Scale (RSES): Incorrect Reverse-Coding Formula

- **Category**: `reverse_coding`
- **Instrument**: `rses`
- **Affected Columns**: `rses_total` (and consequently any downstream analyses using RSES totals)
- **Rows Affected**: 505 (all respondents)
- **Description**: 
  According to the RSES scoring guide, items 3, 5, 8, 9, and 10 are negatively worded and must be reverse-coded using the formula:
  $$\text{Score} = 3 - v$$
  where $v \in \{0, 1, 2, 3\}$.
  
  The scoring pipeline instead uses the formula:
  $$\text{Score} = 4 - v$$
  This adds an extra 1 point to each of the 5 reversed items (totaling a systematic **+5 point inflation** on every participant's RSES score).
- **Evidence**: 
  For complete respondent `R0001`, raw answers are:
  - Positives (1,2,4,6,7): 2, 1, 1, 1, 1 (sum = 6)
  - Negatives (3,5,8,9,10): 0, 0, 1, 2, 2 (raw sum = 5)
  - Correct reverse-coded negative items ($3 - v$): $3, 3, 2, 1, 1$ (sum = 10)
  - Correct total score: $6 + 10 = 16.0$
  - Pipeline output for `R0001`: `21.0` (difference of exactly $+5.0$).
  
  Across all 505 rows, reproducing the pipeline's output requires applying `4 - v` for the five negative items. When this formula is used, 100% of pipeline outputs match our recreated scorer exactly ($N = 505$).

---

## Verification & Conclusion

PHQ-9 and GAD-7 scoring pipelines adhere strictly to the study protocols, including proper rounding rules for prorated scores (half-rounding up, e.g., using `np.floor(x + 0.5)`), cutpoint boundary handling, missing data thresholds (missing $\ge 2$ items yields blank totals), and self-harm flagging. 

For RSES, fixing the reverse-coding formula from `4 - v` back to `3 - v` will resolve the systematic $+5$ score inflation.
