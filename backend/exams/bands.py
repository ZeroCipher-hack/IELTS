"""Raw score to band, and the overall band of a full exam.

Honesty rules this module. The published raw-to-band conversions apply to a
STANDARD 40-question Listening or Academic Reading paper and to nothing else.
A six-question practice set has no band, and inventing one would be the single
most damaging thing this product could do: a candidate who is told 6.5 and
walks into a real exam at 5.0 was misled by us.

So: 40 questions, band. Anything else, None, and the result says raw score.
A full exam reports an overall band only when all four sections carry one.
"""
import math

# Public conversions widely used for practice papers. Lower bound of correct
# answers for each band; the real tables are version-specific and are not
# published as one authoritative set, so these are ESTIMATES and are labelled
# as such everywhere they surface.
LISTENING = [(39, 9.0), (37, 8.5), (35, 8.0), (32, 7.5), (30, 7.0), (26, 6.5),
             (23, 6.0), (18, 5.5), (16, 5.0), (13, 4.5), (10, 4.0), (8, 3.5),
             (6, 3.0), (4, 2.5)]
ACADEMIC_READING = [(39, 9.0), (37, 8.5), (35, 8.0), (33, 7.5), (30, 7.0), (27, 6.5),
                    (23, 6.0), (19, 5.5), (15, 5.0), (13, 4.5), (10, 4.0), (8, 3.5),
                    (6, 3.0), (4, 2.5)]
TABLES = {'Listening': LISTENING, 'Reading': ACADEMIC_READING}
STANDARD_LENGTH = 40


def raw_band(section, correct, total):
    """Band for a standard-length paper, else None. Never guesses."""
    table = TABLES.get(section)
    if table is None or total != STANDARD_LENGTH:
        return None
    if not isinstance(correct, int) or not 0 <= correct <= total:
        return None
    for threshold, band in table:
        if correct >= threshold:
            return band
    return 2.0 if correct >= 2 else 1.0


def round_band(value):
    """IELTS rounding: to the nearest half band, with .25 and .75 going up."""
    return math.floor(value * 2 + 0.5) / 2


def overall(section_bands):
    """Overall band from four section bands, or None when one is missing."""
    values = [section_bands.get(s) for s in ('Listening', 'Reading', 'Writing', 'Speaking')]
    if any(v is None for v in values):
        return None
    return round_band(sum(values) / 4)
