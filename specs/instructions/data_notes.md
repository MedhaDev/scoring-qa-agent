# Data notes for the scoring team

These notes apply to all three questionnaires in this study (PHQ-9, GAD-7 and the
Rosenberg Self-Esteem Scale). Read them together with the scoring guide for each
questionnaire.

## The raw file

`raw_responses.csv` has one row per participant. The first column, `respondent_id`,
identifies the participant. Every other column is one question, named after the
questionnaire and the question number, for example `phq9_4` is question 4 of the
PHQ-9 and `rses_10` is question 10 of the Rosenberg scale. There is also a column
called `phq9_difficulty`, which holds the extra question printed at the bottom of
the PHQ-9 form.

Answers are stored as whole numbers from 0 to 3. What each number means depends on
the questionnaire, so check the individual scoring guide.

## Missing answers

When a participant skipped a question, the data team entered **-9**. Treat -9 as
"no answer". An empty cell, or any number outside 0 to 3, should also be treated as
"no answer". None of these should ever be added into a score as if it were a real
answer.

Our study protocol uses the same rule for all three questionnaires:

- If a participant answered every question, the total is simply the sum.
- If exactly **one** question is unanswered, we still give a total, by scaling up:
  take the sum of the answered questions, multiply by the full number of questions,
  and divide by the number actually answered. Round the result to a whole number.
  Halves always round up, so 4.5 becomes 5 and 10.5 becomes 11.
- If **two or more** questions are unanswered, the participant gets no total for
  that questionnaire. Leave the total blank, and leave anything that depends on the
  total (like the severity label) blank as well.

These missing-data steps are our own study convention. The official materials for
these questionnaires do not say how to handle skipped questions.

## The scored file

The scoring pipeline produces `pipeline_output.csv`, with one row per participant,
in the same order as the raw file. The columns are described in each scoring guide.
Yes/no columns are written as `True` or `False`. A blank cell means the value could
not be calculated.
