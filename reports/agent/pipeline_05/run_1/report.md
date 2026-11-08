# QA Report: Survey Scoring Pipeline

We conducted a thorough quality assurance review of `pipeline_output.csv` against `raw_responses.csv` using the provided scoring guides (`phq9_scoring_guide.md`, `gad7_scoring_guide.md`, `rses_scoring_guide.md`) and `data_notes.md`.

## Summary
- **GAD-7**: Passed (0 mismatches across all columns).
- **Rosenberg Self-Esteem Scale (RSES)**: Passed (0 mismatches across all columns).
- **PHQ-9**: Issues found. The pipeline incorrectly includes `phq9_difficulty` as part of the PHQ-9 item set.

## Detailed Findings

### PHQ-9: Inclusion of Difficulty Question in Score
- **Category**: `item_set`
- **Affected Columns**: `phq9_total`, `phq9_band`, `phq9_prorated`
- **Rows Affected**: 505 (all respondents)
- **Description**: The PHQ-9 scoring guide explicitly states: *"That answer is stored in `phq9_difficulty`. It is useful clinically, but the developers are clear that it is not part of any score. Never add it to the total."* However, the pipeline includes `phq9_difficulty` as a 10th item when computing `phq9_total`, evaluating missingness/prorating (`phq9_prorated`), and determining severity bands (`phq9_band`). When `phq9_difficulty` is skipped (-9), the pipeline incorrectly treats it as a missing questionnaire item, triggering prorating.
- **Confirmation**: Recreating the pipeline with our scorer including `phq9_difficulty` as a 10th item resulted in a **100% exact match** across all PHQ-9 columns (0 mismatches).
