# QA Report: Scoring Pipeline Audit

We performed a comprehensive audit of `pipeline_output.csv` against `raw_responses.csv` using the provided scoring guides and data notes for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES).

## Summary
- **PHQ-9**: Total scores, prorated flags, and self-harm flags match the guide and raw data perfectly across all 505 respondents. However, `phq9_band` has **28 mismatches** due to an incorrect cutoff band definition.
- **GAD-7**: Total scores, bands, and prorated flags match perfectly across all 505 respondents (0 mismatches).
- **RSES**: Total scores and prorated flags match perfectly across all 505 respondents (0 mismatches).

## Detailed Finding

### 1. PHQ-9 Severity Cutoff Bands (`phq9_band`)
- **Category**: `cutoff_bands`
- **Instrument**: `phq9`
- **Affected Column**: `phq9_band`
- **Rows Affected**: 28 respondents (participants with PHQ-9 totals from 15 to 19, e.g., `R0029`, `R0131`, `R0155`).
- **Description**: According to the PHQ-9 scoring guide, scores from 15 to 19 represent "moderately severe" depression, and "severe" begins at 20. The pipeline incorrectly assigns "severe" to any score of 15 or higher, effectively omitting the "moderately severe" band.
- **Confirmation**: Re-running scoring logic with the pipeline's cutoff thresholds (`15+` as `'severe'`) results in an exact match (0 mismatches).

## Verdict
**issues_found** (Minor severity label mapping error for PHQ-9).