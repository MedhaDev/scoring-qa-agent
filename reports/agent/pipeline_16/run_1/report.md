# Quality Assurance Report: Survey Scoring Pipeline

We have completed a comprehensive QA audit of `pipeline_output.csv` against `raw_responses.csv`, the scoring guides, and the study data notes. 

## Verdict
**Issues Found**

---

## Summary of Findings

1. **Failure to Apply Missing Data Protocol Across All Questionnaires (`missing_data`)**
   - **Instruments:** PHQ-9, GAD-7, RSES
   - **Description:** The data notes explicitly specify a study protocol for missing answers:
     - 0 skipped questions: sum the items.
     - Exactly 1 skipped question: scale up (prorate) the sum ($\text{sum} \times N / (N-1)$), rounding half up. Set `*_prorated` to `True`.
     - $\ge 2$ skipped questions: assign no total (blank/NaN) and leave severity bands blank.
   - **Pipeline Behavior:** The pipeline completely ignores missing data rules. It simply sums whatever valid items are present (treating skipped items as 0), outputs total scores even for participants with 2, 3, or 4 missing answers, and hardcodes `*_prorated` to `False` for every single participant.

2. **Improper Handling of Missing Values in Rosenberg Self-Esteem Scale (`reverse_coding`)**
   - **Instrument:** RSES
   - **Description:** For RSES, missing values (`-9`) are treated as a valid response of `0` (strongly disagree). For negatively worded items (items 3, 5, 8, 9, 10), this means a missing answer is scored as $3 - 0 = 3$, which incorrectly adds maximum points to participants who skipped negative items.
   - **Evidence:** 71 participants with missing RSES items had their totals inflated by this imputation behavior.

3. **Self-Harm Flag Not Left Blank When Question 9 is Skipped (`missing_data`)**
   - **Instrument:** PHQ-9 (`phq9_self_harm_flag`)
   - **Description:** The PHQ-9 scoring guide states: *"If question 9 itself was skipped, leave the flag blank."*
   - **Pipeline Behavior:** For the 9 participants who skipped question 9, the pipeline assigned `False` instead of leaving the flag blank.
