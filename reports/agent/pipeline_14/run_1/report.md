# QA Scoring Report

## Overview
We performed a comprehensive quality assurance check of `pipeline_output.csv` against `raw_responses.csv` using the official scoring guides and data notes for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES). 

Our custom Python scorer implemented all rules correctly, including missing data handling (-9 / blank as missing, prorating when exactly one item is missing with half-rounding up, and blanking when two or more items are missing), severity band cutoffs, self-harm flagging, and reverse-coding instructions.

## Findings

### Rosenberg Self-Esteem Scale (RSES) Reverse Coding Error
- **Category:** `reverse_coding`
- **Instrument:** `rses`
- **Affected Column:** `rses_total`
- **Rows Affected:** 505 (all respondents)
- **Description:** The scoring guide specifies that items 3, 5, 8, 9, and 10 are negatively worded and must be reverse-scored (i.e., `3 - stored_answer`). However, the pipeline incorrectly reverse-scores items **2, 5, 6, 8, and 9** instead.
- **Evidence:** When our scorer applies reverse-scoring to items 3, 5, 8, 9, and 10, it disagrees with `rses_total` in 452 out of 505 rows. When we hypothesize that the pipeline reverse-scored items 2, 5, 6, 8, and 9, the scorer matches the pipeline's `rses_total` and `rses_prorated` **100% perfectly across all 505 respondents**.

## Questionnaire Rules Verified (Passing)
- **PHQ-9 (`phq9_total`, `phq9_band`, `phq9_prorated`, `phq9_self_harm_flag`):** 100% exact match. Missing data rules, prorating, severity bands, and question 9 self-harm flagging are implemented correctly by the pipeline.
- **GAD-7 (`gad7_total`, `gad7_band`, `gad7_prorated`):** 100% exact match. Missing data rules, prorating, and severity bands are implemented correctly by the pipeline.
- **RSES Prorating (`rses_prorated`):** 100% exact match once accounting for the reverse-coding item set difference.

## Verdict
`issues_found` (due to the RSES reverse-coding error).
