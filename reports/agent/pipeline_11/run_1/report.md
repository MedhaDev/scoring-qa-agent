# QA Report: Survey Scoring Pipeline

**Verdict:** `pass`

## Summary of Findings

We independently implemented scoring functions for the PHQ-9, GAD-7, and Rosenberg Self-Esteem Scale (RSES) in strict accordance with the study's data notes and individual scoring guides. We compared the pipeline output (`pipeline_output.csv`) against our re-scored responses across all 505 respondents and all 10 output columns.

Every single calculated value—including totals, severity bands (`phq9_band`, `gad7_band`), proration indicators (`phq9_prorated`, `gad7_prorated`, `rses_prorated`), missing data handling (treating `-9`, nulls, or out-of-range values as missing and correctly prorating for exactly one missing item while dropping totals for two or more missing items), half-rounding rules (half-up rounding), and the PHQ-9 self-harm flag (`phq9_self_harm_flag`)—matched the pipeline output **100%** with zero discrepancies.

The scoring pipeline is functioning correctly and adheres fully to all study protocols and scoring guides.
