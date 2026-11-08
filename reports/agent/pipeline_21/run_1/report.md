# QA Report: Scoring Pipeline Review

## Overview
We performed a comprehensive quality assurance review of `pipeline_output.csv` against `raw_responses.csv` using the official scoring guides and data notes for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES). 

Our custom scorer exactly reproduced the pipeline's output across all columns and participants once the pipeline's error on the RSES was accounted for.

## Summary of Findings
- **PHQ-9**: All totals, severity bands, prorating flags, and self-harm flags matched the specification perfectly.
- **GAD-7**: All totals, severity bands, and prorating flags matched the specification perfectly.
- **RSES (`rses_total`)**: **Issues Found.** The scoring pipeline incorrectly reverse-coded **all 10 items** rather than only the 5 negatively worded items (3, 5, 8, 9, and 10).

## Detailed Finding

### RSES Reverse Coding Error
- **Instrument**: Rosenberg Self-Esteem Scale (`rses`)
- **Affected Column**: `rses_total`
- **Rows Affected**: 505 (all rows)
- **Category**: `reverse_coding`
- **Description**: According to the RSES scoring guide, items 3, 5, 8, 9, and 10 are negatively worded and must be reverse-scored ($3 - v$), while items 1, 2, 4, 6, and 7 are positively worded and used as-is. The pipeline applied the reverse-scoring transformation ($3 - v$) to all 10 items. Consequently, the total score produced is equivalent to $30 - \text{raw sum}$ (for complete data), leading to incorrect total scores for every participant.
- **Confirmation**: When our scorer was modified to reverse-code all 10 items, it matched the pipeline's `rses_total` for all 505 respondents (100% exact match).
