# Scoring guide: Rosenberg Self-Esteem Scale

The Rosenberg Self-Esteem Scale has ten statements about how a person feels about
themselves. It is in the public domain; the University of Maryland Sociology
Department hosts the scale and its scoring notes.

## How answers are stored

Participants say how much they agree with each statement. In our data file the
answers are stored as 0 = strongly disagree, 1 = disagree, 2 = agree,
3 = strongly agree.

## Positive and negative statements

Half of the statements are worded positively (for example, feeling that one has a
number of good qualities) and half are worded negatively (for example, feeling like
a failure). Agreeing with a positive statement shows higher self-esteem; agreeing
with a negative statement shows lower self-esteem. So the negative statements have
to be flipped before adding up.

We use the item numbering of the University of Maryland version of the scale. In that
numbering, the **negatively worded statements are questions 3, 5, 8, 9 and 10**. The
positively worded ones are questions 1, 2, 4, 6 and 7.

Be careful: the same ten statements appear in a different order in some other
publications, and those sources list different question numbers as the reversed ones.
Those lists do not apply to our data.

- For questions 1, 2, 4, 6 and 7, the score is the stored answer (0 to 3).
- For questions 3, 5, 8, 9 and 10, the score is 3 minus the stored answer, so strongly
  agreeing scores 0 and strongly disagreeing scores 3.

## Total score

Add the ten item scores (after flipping) for a total between 0 and 30. Higher means
higher self-esteem. Apply the study's missing-answer rule from the data notes to the
flipped scores.

## No severity label

The scale has no official cutoffs for "high" or "low" self-esteem, so the pipeline
does not produce a label for it.

## Output columns

- `rses_total`: the total (whole number), or blank
- `rses_prorated`: `True` if the total was scaled up for one skipped question,
  `False` if all ten were answered, blank when there is no total
