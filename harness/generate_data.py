"""
Generate synthetic survey responses for PHQ-9, GAD-7 and the Rosenberg Self-Esteem Scale.

Output: data/raw_responses.csv
Uses a fixed random seed, so every run produces the exact same file.
"""

import os

import numpy as np
import pandas as pd
import yaml

SEED = 42
N_RESPONDENTS = 500
MISSING_RATE = 0.02      # chance that any single answer is missing
N_SKIPPERS = 15          # people who skip several items in one questionnaire
MISSING_CODE = -9

# Correlations between the hidden traits: depression, anxiety, self-esteem
TRAIT_CORRELATIONS = [
    [1.0, 0.7, -0.5],
    [0.7, 1.0, -0.4],
    [-0.5, -0.4, 1.0],
]

# How "hard" each item is to endorse. Higher = fewer people pick high answers.
PHQ9_ITEM_OFFSETS = [0.0, 0.1, 0.0, -0.2, 0.2, 0.3, 0.3, 0.6, 1.2]
GAD7_ITEM_OFFSETS = [0.0, 0.1, 0.0, 0.1, 0.4, 0.2, 0.4]

# Cut points that turn a continuous answer level into 0, 1, 2 or 3
SYMPTOM_CUTS = [0.3, 1.1, 1.8]
AGREEMENT_CUTS = [-1.0, 0.0, 1.2]

ITEM_NOISE = 0.7
RSES_AGREEMENT_SHIFT = 0.5   # pushes answers toward agreeing with positive statements

rng = np.random.default_rng(SEED)


def load_spec(name):
    with open(f"specs/{name}.yaml") as f:
        return yaml.safe_load(f)


def to_answer(level, cuts):
    """Turn a continuous level into an answer 0-3 using the cut points."""
    return int(np.digitize(level, cuts))


def make_symptom_items(trait, offsets):
    """PHQ-9 / GAD-7 style items: higher trait -> higher answers."""
    answers = []
    for offset in offsets:
        level = trait - offset + rng.normal(0, ITEM_NOISE)
        answers.append(to_answer(level, SYMPTOM_CUTS))
    return answers


def make_rses_items(self_esteem, reverse_items):
    """Rosenberg items stored as 0 = Strongly Disagree ... 3 = Strongly Agree."""
    answers = []
    for item_number in range(1, 11):
        if item_number in reverse_items:
            # Negative statements: high self-esteem -> disagree
            level = -self_esteem - RSES_AGREEMENT_SHIFT + rng.normal(0, ITEM_NOISE)
        else:
            # Positive statements: high self-esteem -> agree
            level = self_esteem + RSES_AGREEMENT_SHIFT + rng.normal(0, ITEM_NOISE)
        answers.append(to_answer(level, AGREEMENT_CUTS))
    return answers


def main():
    phq9_spec = load_spec("phq9")
    gad7_spec = load_spec("gad7")
    rses_spec = load_spec("rses")

    phq9_cols = phq9_spec["items"]["columns"]
    gad7_cols = gad7_spec["items"]["columns"]
    rses_cols = rses_spec["items"]["columns"]
    rses_reverse = rses_spec["reverse_items"]["items"]

    # Step 1: hidden traits for every respondent
    traits = rng.multivariate_normal([0, 0, 0], TRAIT_CORRELATIONS, size=N_RESPONDENTS)

    # Step 2: answers built from the traits
    rows = []
    for i in range(N_RESPONDENTS):
        depression, anxiety, self_esteem = traits[i]

        row = {"respondent_id": f"R{i + 1:04d}"}

        phq9_answers = make_symptom_items(depression, PHQ9_ITEM_OFFSETS)
        for col, value in zip(phq9_cols, phq9_answers):
            row[col] = value
        row["phq9_difficulty"] = to_answer(depression + rng.normal(0, 0.8), [0.5, 1.5, 2.2])

        gad7_answers = make_symptom_items(anxiety, GAD7_ITEM_OFFSETS)
        for col, value in zip(gad7_cols, gad7_answers):
            row[col] = value

        rses_answers = make_rses_items(self_esteem, rses_reverse)
        for col, value in zip(rses_cols, rses_answers):
            row[col] = value

        rows.append(row)

    data = pd.DataFrame(rows)

    # Step 3a: random missing answers (each answer has a 2% chance)
    answer_cols = phq9_cols + ["phq9_difficulty"] + gad7_cols + rses_cols
    for col in answer_cols:
        is_missing = rng.random(N_RESPONDENTS) < MISSING_RATE
        data.loc[is_missing, col] = MISSING_CODE

    # Step 3b: "skippers" leave 2-4 items blank in one questionnaire
    skipper_rows = rng.choice(N_RESPONDENTS, size=N_SKIPPERS, replace=False)
    item_sets = [phq9_cols, gad7_cols, rses_cols]
    for row_index in skipper_rows:
        chosen_set = item_sets[rng.integers(0, 3)]
        n_skipped = rng.integers(2, 5)
        skipped_cols = rng.choice(chosen_set, size=n_skipped, replace=False)
        for col in skipped_cols:
            data.loc[row_index, col] = MISSING_CODE

    # Step 4: edge-case rows built from the spec worked examples
    edge_rows = []
    for k in range(5):
        row = {"respondent_id": f"R{N_RESPONDENTS + k + 1:04d}"}
        phq9_example = phq9_spec["worked_examples"][k]["items"]
        gad7_example = gad7_spec["worked_examples"][k]["items"]
        rses_example = rses_spec["worked_examples"][k]["items"]
        for col, value in zip(phq9_cols, phq9_example):
            row[col] = value
        row["phq9_difficulty"] = 1
        for col, value in zip(gad7_cols, gad7_example):
            row[col] = value
        for col, value in zip(rses_cols, rses_example):
            row[col] = value
        edge_rows.append(row)

    data = pd.concat([data, pd.DataFrame(edge_rows)], ignore_index=True)

    # Step 5: save
    os.makedirs("data", exist_ok=True)
    data.to_csv("data/raw_responses.csv", index=False)

    # Summary
    print(f"Saved data/raw_responses.csv with {len(data)} rows and {len(data.columns)} columns")
    print()
    print("Missing answers per questionnaire (rows with 0 / 1 / 2+ missing items):")
    for name, cols in [("PHQ-9", phq9_cols), ("GAD-7", gad7_cols), ("RSES", rses_cols)]:
        n_missing = (data[cols] == MISSING_CODE).sum(axis=1)
        none = (n_missing == 0).sum()
        one = (n_missing == 1).sum()
        two_plus = (n_missing >= 2).sum()
        print(f"  {name}: {none} / {one} / {two_plus}")
    print()
    print("Share of each answer value across all answers (missing excluded):")
    for name, cols in [("PHQ-9", phq9_cols), ("GAD-7", gad7_cols), ("RSES", rses_cols)]:
        values = data[cols].to_numpy().flatten()
        values = values[values != MISSING_CODE]
        shares = []
        for answer in [0, 1, 2, 3]:
            share = (values == answer).mean() * 100
            shares.append(f"{answer}: {share:.0f}%")
        print(f"  {name}: " + ", ".join(shares))


if __name__ == "__main__":
    main()
