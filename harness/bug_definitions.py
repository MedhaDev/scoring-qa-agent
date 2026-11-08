"""
The planted bugs. Each bug is ONE find-and-replace on harness/reference_pipeline.py.

Fields:
  bug_id               short name used in the ground-truth manifest
  category             the bug's main category
  accepted_categories  categories that count as a correct diagnosis
                       (some bugs honestly fit more than one)
  instruments          which questionnaires' outputs the bug can change
  description          plain-English description of the bug
  find / replace       the exact text change made to the reference pipeline
"""

ALL_INSTRUMENTS = ["phq9", "gad7", "rses"]

BUGS = [
    # ---------------- Reverse coding ----------------
    {
        "bug_id": "rev_missing_item",
        "category": "reverse_coding",
        "accepted_categories": ["reverse_coding"],
        "instruments": ["rses"],
        "description": "RSES item 10 is left out of the reverse-coded item list.",
        "find": 'RSES_REVERSE_ITEMS = ["rses_3", "rses_5", "rses_8", "rses_9", "rses_10"]',
        "replace": 'RSES_REVERSE_ITEMS = ["rses_3", "rses_5", "rses_8", "rses_9"]',
    },
    {
        "bug_id": "rev_wrong_item_order",
        "category": "reverse_coding",
        "accepted_categories": ["reverse_coding"],
        "instruments": ["rses"],
        "description": "RSES reverse list copied from a version with a different item order (2, 5, 6, 8, 9 instead of 3, 5, 8, 9, 10).",
        "find": 'RSES_REVERSE_ITEMS = ["rses_3", "rses_5", "rses_8", "rses_9", "rses_10"]',
        "replace": 'RSES_REVERSE_ITEMS = ["rses_2", "rses_5", "rses_6", "rses_8", "rses_9"]',
    },
    {
        "bug_id": "rev_wrong_formula",
        "category": "reverse_coding",
        "accepted_categories": ["reverse_coding"],
        "instruments": ["rses"],
        "description": "Reverse-coding formula uses 4 - x (right for a 1-4 scale) on 0-3 answers.",
        "find": "    return 3 - value",
        "replace": "    return 4 - value",
    },
    {
        "bug_id": "rev_all_items",
        "category": "reverse_coding",
        "accepted_categories": ["reverse_coding"],
        "instruments": ["rses"],
        "description": "Every RSES item is reverse-coded, not just the 5 negative items.",
        "find": "        if answer is not None and col in RSES_REVERSE_ITEMS:",
        "replace": "        if answer is not None:",
    },
    # ---------------- Missing data / prorating ----------------
    {
        "bug_id": "miss_as_zero",
        "category": "missing_data",
        "accepted_categories": ["missing_data"],
        "instruments": ALL_INSTRUMENTS,
        "description": "The missing code -9 is turned into a 0 answer instead of being treated as missing.",
        "find": "    if value == MISSING_CODE:\n        return None",
        "replace": "    if value == MISSING_CODE:\n        return 0",
    },
    {
        "bug_id": "miss_lenient_threshold",
        "category": "missing_data",
        "accepted_categories": ["missing_data"],
        "instruments": ALL_INSTRUMENTS,
        "description": "Totals are prorated with up to 2 missing items instead of at most 1.",
        "find": "MAX_MISSING_ITEMS = 1",
        "replace": "MAX_MISSING_ITEMS = 2",
    },
    {
        "bug_id": "miss_bankers_rounding",
        "category": "missing_data",
        "accepted_categories": ["missing_data"],
        "instruments": ALL_INSTRUMENTS,
        "description": "Prorated totals use Python's round(), which rounds .5 to the nearest even number instead of up.",
        "find": "    return math.floor(number + 0.5)",
        "replace": "    return round(number)",
    },
    {
        "bug_id": "miss_no_scaling",
        "category": "missing_data",
        "accepted_categories": ["missing_data"],
        "instruments": ALL_INSTRUMENTS,
        "description": "When 1 item is missing, the answered items are summed but not scaled up to the full item count.",
        "find": "    prorated_total = sum(answered) * n_items / len(answered)",
        "replace": "    prorated_total = sum(answered)",
    },
    # ---------------- Wrong item sets ----------------
    {
        "bug_id": "items_gad7_missing_item",
        "category": "item_set",
        "accepted_categories": ["item_set"],
        "instruments": ["gad7"],
        "description": "GAD-7 total uses only items 1-6; item 7 is left out.",
        "find": 'GAD7_ITEMS = ["gad7_1", "gad7_2", "gad7_3", "gad7_4", "gad7_5", "gad7_6", "gad7_7"]',
        "replace": 'GAD7_ITEMS = ["gad7_1", "gad7_2", "gad7_3", "gad7_4", "gad7_5", "gad7_6"]',
    },
    {
        "bug_id": "items_phq9_includes_difficulty",
        "category": "item_set",
        "accepted_categories": ["item_set"],
        "instruments": ["phq9"],
        "description": "The unscored PHQ-9 'difficulty' question is added into the PHQ-9 total.",
        "find": '"phq9_8", "phq9_9"]',
        "replace": '"phq9_8", "phq9_9", "phq9_difficulty"]',
    },
    {
        "bug_id": "items_phq9_duplicate_item",
        "category": "item_set",
        "accepted_categories": ["item_set"],
        "instruments": ["phq9"],
        "description": "Copy-paste error: PHQ-9 item 8 is listed twice and item 9 is never used in the total.",
        "find": '"phq9_8", "phq9_9"]',
        "replace": '"phq9_8", "phq9_8"]',
    },
    # ---------------- Severity cutoff bands ----------------
    {
        "bug_id": "cut_phq9_boundary",
        "category": "cutoff_bands",
        "accepted_categories": ["cutoff_bands"],
        "instruments": ["phq9"],
        "description": "PHQ-9 score of 10 is labelled 'mild' instead of 'moderate' (mild band set to 5-10).",
        "find": '    (5, 9, "mild"),\n    (10, 14, "moderate"),\n    (15, 19, "moderately severe"),',
        "replace": '    (5, 10, "mild"),\n    (11, 14, "moderate"),\n    (15, 19, "moderately severe"),',
    },
    {
        "bug_id": "cut_gad7_severe_start",
        "category": "cutoff_bands",
        "accepted_categories": ["cutoff_bands"],
        "instruments": ["gad7"],
        "description": "GAD-7 'severe' starts at 16 instead of 15.",
        "find": '    (10, 14, "moderate"),\n    (15, 21, "severe"),',
        "replace": '    (10, 15, "moderate"),\n    (16, 21, "severe"),',
    },
    {
        "bug_id": "cut_phq9_missing_band",
        "category": "cutoff_bands",
        "accepted_categories": ["cutoff_bands"],
        "instruments": ["phq9"],
        "description": "PHQ-9 'moderately severe' band is missing; scores 15-27 are all labelled 'severe'.",
        "find": '    (15, 19, "moderately severe"),\n    (20, 27, "severe"),',
        "replace": '    (15, 27, "severe"),',
    },
    {
        "bug_id": "cut_gad7_unofficial_bands",
        "category": "cutoff_bands",
        "accepted_categories": ["cutoff_bands"],
        "instruments": ["gad7"],
        "description": "GAD-7 bands copied from an unofficial score sheet (0-5 mild, 6-10 moderate, 11-15 moderately severe, 16-21 severe).",
        "find": '    (0, 4, "minimal"),\n    (5, 9, "mild"),\n    (10, 14, "moderate"),\n    (15, 21, "severe"),',
        "replace": '    (0, 5, "mild"),\n    (6, 10, "moderate"),\n    (11, 15, "moderately severe"),\n    (16, 21, "severe"),',
    },
    # ---------------- Off-by-one errors ----------------
    {
        "bug_id": "obo_one_based_coding",
        "category": "off_by_one",
        "accepted_categories": ["off_by_one"],
        "instruments": ALL_INSTRUMENTS,
        "description": "Answers are shifted to 1-4 coding (every answer gets +1) before scoring.",
        "find": "    return int(value)",
        "replace": "    return int(value) + 1",
    },
    {
        "bug_id": "obo_drops_last_item",
        "category": "off_by_one",
        "accepted_categories": ["off_by_one", "item_set"],
        "instruments": ALL_INSTRUMENTS,
        "description": "Loop over items stops one short, so the last item is always treated as missing (and totals get prorated).",
        "find": "    for answer in answers:",
        "replace": "    for answer in answers[:-1]:",
    },
    {
        "bug_id": "obo_self_harm_item",
        "category": "off_by_one",
        "accepted_categories": ["off_by_one", "item_set"],
        "instruments": ["phq9"],
        "description": "Self-harm flag reads PHQ-9 item 8 instead of item 9.",
        "find": 'PHQ9_SELF_HARM_ITEM = "phq9_9"',
        "replace": 'PHQ9_SELF_HARM_ITEM = "phq9_8"',
    },
]

N_CLEAN_COPIES = 4
