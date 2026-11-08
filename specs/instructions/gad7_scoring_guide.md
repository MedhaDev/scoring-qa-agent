# Scoring guide: GAD-7 (anxiety)

The GAD-7 is a seven-question anxiety questionnaire from the same developers as the
PHQ-9 (Spitzer, Kroenke, Williams and Löwe). It is in the public domain.

## Answers

All seven questions (`gad7_1` to `gad7_7`) use the same four options as the PHQ-9:
0 "not at all", 1 "several days", 2 "more than half the days", 3 "nearly every day".
There are no reverse-scored questions. The study's version of the form does not
include the extra "how difficult" question, so there is nothing to leave out.

## Total score

Add all seven answers, giving a total from 0 to 21, using the study's missing-answer
rule from the data notes.

## Severity label

The developers give cutpoints of 5, 10 and 15 for mild, moderate and severe anxiety.
They do not name the range below 5; this study calls it "minimal". So:

- 0 to 4: "minimal"
- 5 to 9: "mild"
- 10 to 14: "moderate"
- 15 to 21: "severe"

There is no "moderately severe" level on the GAD-7. Some score sheets found online
use different ranges; do not use them. A total exactly on a cutpoint belongs to the
higher group.

## Output columns

- `gad7_total`: the total (whole number), or blank
- `gad7_band`: the severity label, or blank when there is no total
- `gad7_prorated`: `True` if the total was scaled up for one skipped question,
  `False` if all seven were answered, blank when there is no total
