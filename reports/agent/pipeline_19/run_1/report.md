# Quality Assurance Report: Survey Scoring Pipeline

**Verdict:** `issues_found`

We conducted a comprehensive QA review of `pipeline_output.csv` against `raw_responses.csv` and the official scoring guides for PHQ-9, GAD-7, and the Rosenberg Self-Esteem Scale (RSES). 

## Summary
- **PHQ-9:** Fully correct across all 505 respondents (totals, severity bands, proration / missing data handling, and self-harm flags).
- **RSES:** Fully correct across all 505 respondents (correct reverse-scoring of items 3, 5, 8, 9, 10, totals, and proration).
- **GAD-7:** **Issues found.** The pipeline systematically omits the seventh item (`gad7_7`) when scoring the GAD-7 questionnaire.

---

## Detailed Findings

### 1. GAD-7 Item Set Error (`item_set`)
- **Instrument:** GAD-7 (`gad7`)
- **Affected Columns:** `gad7_total`, `gad7_band`, `gad7_prorated`
- **Rows Affected:** 160 respondents differ on `gad7_total` (with corresponding downstream effects on `gad7_band` for 40 respondents and `gad7_prorated` for 21 respondents).
- **Description:** According to the GAD-7 scoring guide and study protocol, the GAD-7 consists of 7 items (`gad7_1` to `gad7_7`). However, the scoring pipeline calculates totals using only items 1 through 6 (`gad7_1` to `gad7_6`), completely ignoring `gad7_7`. 
- **Evidence & Confirmation:** Reproducing the pipeline's output by restricting the GAD-7 sum to items 1–6 yielded an exact 100% match across all 505 rows for every GAD-7 output column. When scored correctly using all 7 items (with proper proration when exactly one item is skipped), respondents like `R0004` score 12 instead of 10.