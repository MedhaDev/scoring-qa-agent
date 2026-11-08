# Quality Assurance Report: Survey Scoring Pipeline

**Verdict:** PASS

## Summary
The scoring pipeline (`pipeline_output.csv`) was independently verified against `raw_responses.csv` using a Python scoring script built strictly from the scoring guides (`phq9_scoring_guide.md`, `gad7_scoring_guide.md`, `rses_scoring_guide.md`) and data notes (`data_notes.md`).

Every output column across all 505 respondents—including total scores, severity bands, self-harm flags, proration status flags, missing data handling (-9 / out-of-range values treated as missing), prorated scaling with half-up rounding, and reverse scoring for items 3, 5, 8, 9, and 10 of the Rosenberg Self-Esteem Scale—matched the pipeline output **100% exactly** with zero discrepancies.

## Rules Verified
1. **PHQ-9:**
   - 9 items (0-3 scale), `phq9_difficulty` correctly excluded from total.
   - Severity bands correctly assigned with cutpoints at 5, 10, 15, 20 (ties/exact cutpoints go to higher severity).
   - Self-harm flag (`phq9_self_harm_flag`) correctly triggers on any answer > 0 for question 9.
   - Proration: 1 skipped item scaled up and rounded half-up (`.5` rounds up); 2+ skipped items leave total/band/prorated blank.
2. **GAD-7:**
   - 7 items (0-3 scale), no difficulty item.
   - Severity bands correctly assigned with cutpoints at 5, 10, 15 (labeling <5 as "minimal").
   - Proration rules matching PHQ-9.
3. **Rosenberg Self-Esteem Scale (RSES):**
   - 10 items (0-3 scale).
   - Reverse-scored items correctly identified as 3, 5, 8, 9, and 10 per the University of Maryland version (`3 - stored_value`).
   - Proration rules matching PHQ-9 and GAD-7.
