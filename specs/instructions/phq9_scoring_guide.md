# Scoring guide: PHQ-9 (depression)

The PHQ-9 is a nine-question depression questionnaire developed by Kroenke, Spitzer
and Williams. It is in the public domain. Participants rate how often, over the last
two weeks, they have been bothered by each problem.

## Answers

Each of the nine questions (`phq9_1` to `phq9_9`) is answered on the same scale:
0 means "not at all", 1 means "several days", 2 means "more than half the days" and
3 means "nearly every day". Nothing on this questionnaire is reverse-scored; a higher
answer always means more of the symptom.

Below the nine questions, the form asks how difficult these problems have made it to
work, look after things at home or get along with people. That answer is stored in
`phq9_difficulty`. It is useful clinically, but the developers are clear that it is
**not** part of any score. Never add it to the total.

## Total score

Add the nine answers. The total runs from 0 to 27. Follow the study's missing-answer
rule in the data notes (one skipped question is scaled up; two or more means no total).

## Severity label

The developers describe cutpoints at 5, 10, 15 and 20. In practice:

- a total of 0 to 4 is "none-minimal"
- 5 up to and including 9 is "mild"
- 10 up to and including 14 is "moderate"
- 15 up to and including 19 is "moderately severe"
- 20 and above is "severe"

Note that a score sitting exactly on a cutpoint belongs to the higher group: a total
of exactly 10 is "moderate", not "mild".

## Self-harm flag

Question 9 asks about thoughts of being better off dead or of hurting oneself. Any
answer other than "not at all" should be followed up, so we record a flag: `True` if
question 9 was answered 1, 2 or 3, and `False` if it was answered 0. If question 9
itself was skipped, leave the flag blank. The flag is based on question 9 alone, so it
is still filled in even when the participant has no total.

## Output columns

- `phq9_total`: the total (whole number), or blank
- `phq9_band`: the severity label, or blank when there is no total
- `phq9_prorated`: `True` if the total was scaled up because one question was skipped,
  `False` if all nine were answered, blank when there is no total
- `phq9_self_harm_flag`: see above
