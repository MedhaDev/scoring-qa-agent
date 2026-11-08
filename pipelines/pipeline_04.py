"""
Reference scoring pipeline for PHQ-9, GAD-7 and the Rosenberg Self-Esteem Scale.

Production scoring pipeline.

Usage:
    python harness/reference_pipeline.py <input.csv> <output.csv>
"""

import math
import sys

import pandas as pd

MISSING_CODE = -9
VALID_VALUES = [0, 1, 2, 3]
MAX_MISSING_ITEMS = 1

PHQ9_ITEMS = ["phq9_1", "phq9_2", "phq9_3", "phq9_4", "phq9_5", "phq9_6", "phq9_7", "phq9_8", "phq9_9"]
GAD7_ITEMS = ["gad7_1", "gad7_2", "gad7_3", "gad7_4", "gad7_5", "gad7_6", "gad7_7"]
RSES_ITEMS = ["rses_1", "rses_2", "rses_3", "rses_4", "rses_5", "rses_6", "rses_7", "rses_8", "rses_9", "rses_10"]

RSES_REVERSE_ITEMS = ["rses_3", "rses_5", "rses_8", "rses_9", "rses_10"]

PHQ9_SELF_HARM_ITEM = "phq9_9"

PHQ9_BANDS = [
    (0, 4, "none-minimal"),
    (5, 9, "mild"),
    (10, 14, "moderate"),
    (15, 19, "moderately severe"),
    (20, 27, "severe"),
]

GAD7_BANDS = [
    (0, 4, "minimal"),
    (5, 9, "mild"),
    (10, 14, "moderate"),
    (15, 21, "severe"),
]


def clean_answer(value):
    """Return the answer as an int, or None if it is missing or invalid."""
    if pd.isna(value):
        return None
    if value == MISSING_CODE:
        return None
    if value not in VALID_VALUES:
        return None
    return int(value) + 1


def reverse_code(value):
    """Flip a 0-3 answer: 0 -> 3, 1 -> 2, 2 -> 1, 3 -> 0."""
    return 3 - value


def round_half_up(number):
    """Round to the nearest whole number, with .5 always rounded up."""
    return math.floor(number + 0.5)


def total_from_answers(answers):
    """
    Add up item scores using the missing-data rule.
    Returns (total, prorated). Both are None if too many items are missing.
    """
    n_items = len(answers)
    answered = []
    for answer in answers:
        if answer is not None:
            answered.append(answer)

    n_missing = n_items - len(answered)

    if n_missing > MAX_MISSING_ITEMS:
        return None, None

    if n_missing == 0:
        return sum(answered), False

    prorated_total = sum(answered) * n_items / len(answered)
    return round_half_up(prorated_total), True


def band_for(total, bands):
    """Return the band label for a total, or None if there is no total."""
    if total is None:
        return None
    for low, high, label in bands:
        if low <= total <= high:
            return label
    return None


def score_phq9(row):
    answers = []
    for col in PHQ9_ITEMS:
        answers.append(clean_answer(row[col]))

    total, prorated = total_from_answers(answers)

    self_harm_answer = clean_answer(row[PHQ9_SELF_HARM_ITEM])
    if self_harm_answer is None:
        self_harm_flag = None
    else:
        self_harm_flag = self_harm_answer >= 1

    return {
        "phq9_total": total,
        "phq9_band": band_for(total, PHQ9_BANDS),
        "phq9_prorated": prorated,
        "phq9_self_harm_flag": self_harm_flag,
    }


def score_gad7(row):
    answers = []
    for col in GAD7_ITEMS:
        answers.append(clean_answer(row[col]))

    total, prorated = total_from_answers(answers)

    return {
        "gad7_total": total,
        "gad7_band": band_for(total, GAD7_BANDS),
        "gad7_prorated": prorated,
    }


def score_rses(row):
    answers = []
    for col in RSES_ITEMS:
        answer = clean_answer(row[col])
        if answer is not None and col in RSES_REVERSE_ITEMS:
            answer = reverse_code(answer)
        answers.append(answer)

    total, prorated = total_from_answers(answers)

    return {
        "rses_total": total,
        "rses_prorated": prorated,
    }


def score_all(data):
    """Score every respondent and return a table of results."""
    results = []
    for _, row in data.iterrows():
        result = {"respondent_id": row["respondent_id"]}
        result.update(score_phq9(row))
        result.update(score_gad7(row))
        result.update(score_rses(row))
        results.append(result)

    scores = pd.DataFrame(results)

    # Whole-number columns that can be blank
    for col in ["phq9_total", "gad7_total", "rses_total"]:
        scores[col] = scores[col].astype("Int64")

    return scores


def main():
    if len(sys.argv) != 3:
        print("Usage: python reference_pipeline.py <input.csv> <output.csv>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    data = pd.read_csv(input_path)
    scores = score_all(data)
    scores.to_csv(output_path, index=False)
    print(f"Scored {len(scores)} respondents -> {output_path}")


if __name__ == "__main__":
    main()
