# QA Scoring Report

We audited `pipeline_output.csv` against `raw_responses.csv` using the official scoring guides and data notes for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES).

## Summary
- **PHQ-9**: Pass (Totals, prorating, severity bands, and self-harm flags match 100%).
- **GAD-7**: Issues found in severity band cutoffs for respondents scoring exactly 15.
- **RSES**: Pass (Totals and prorating match 100%).

## Detailed Findings

### GAD-7 Severity Band Cutoff Error (`gad7_band`)
- **Category**: `cutoff_bands`
- **Instrument**: `gad7`
- **Rows Affected**: 6 respondents (e.g., `R0021`, `R0235`, `R0370`, `R0449`, `R0476`, `R0504`)
- **Description**: The scoring guide specifies that GAD-7 severity bands are defined as:
  - 0 to 4: minimal
  - 5 to 9: mild
  - 10 to 14: moderate
  - 15 to 21: severe
  
  The pipeline incorrectly included a total score of 15 in the **moderate** band (`10-15`) rather than the **severe** band (`15+`), affecting all 6 participants who achieved a total score of 15.
