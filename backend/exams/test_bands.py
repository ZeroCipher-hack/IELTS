"""A band is reported only where a band can honestly be reported."""
from django.test import TestCase

from .bands import STANDARD_LENGTH, overall, raw_band, round_band


class RawBandTests(TestCase):
    def test_a_standard_paper_converts(self):
        self.assertEqual(raw_band('Listening', 30, 40), 7.0)
        self.assertEqual(raw_band('Listening', 23, 40), 6.0)
        self.assertEqual(raw_band('Reading', 30, 40), 7.0)
        self.assertEqual(raw_band('Reading', 23, 40), 6.0)

    def test_the_two_sections_do_not_share_a_table(self):
        """27/40 is 6.5 in Academic Reading and 6.5 in Listening only by luck;
        at 33 the tables genuinely differ, which is the point of keeping two."""
        self.assertEqual(raw_band('Reading', 33, 40), 7.5)
        self.assertEqual(raw_band('Listening', 33, 40), 7.5)
        self.assertEqual(raw_band('Reading', 19, 40), 5.5)
        self.assertEqual(raw_band('Listening', 19, 40), 5.5)
        self.assertNotEqual(raw_band('Reading', 15, 40), raw_band('Listening', 15, 40))

    def test_a_short_practice_set_has_no_band(self):
        """The whole reason this returns None: 5/6 is not 'band 8'."""
        for total in (1, 5, 6, 10, 39, 41):
            with self.subTest(total=total):
                self.assertIsNone(raw_band('Reading', total, total))

    def test_sections_without_a_table_have_no_band(self):
        self.assertIsNone(raw_band('Writing', 40, 40))
        self.assertIsNone(raw_band('Speaking', 40, 40))

    def test_nonsense_input_is_refused_rather_than_clamped(self):
        self.assertIsNone(raw_band('Reading', -1, STANDARD_LENGTH))
        self.assertIsNone(raw_band('Reading', 41, STANDARD_LENGTH))
        self.assertIsNone(raw_band('Reading', 20.5, STANDARD_LENGTH))

    def test_the_floor_is_covered(self):
        self.assertEqual(raw_band('Reading', 2, 40), 2.0)
        self.assertEqual(raw_band('Reading', 0, 40), 1.0)


class RoundingTests(TestCase):
    def test_quarter_bands_round_up_as_ielts_does(self):
        self.assertEqual(round_band(6.25), 6.5)
        self.assertEqual(round_band(6.75), 7.0)

    def test_an_eighth_below_a_quarter_rounds_down(self):
        self.assertEqual(round_band(6.125), 6.0)
        self.assertEqual(round_band(6.625), 6.5)

    def test_exact_halves_stay_put(self):
        for value in (5.0, 5.5, 6.0, 9.0):
            self.assertEqual(round_band(value), value)


class OverallTests(TestCase):
    def test_four_bands_make_an_overall(self):
        self.assertEqual(overall({'Listening': 6.5, 'Reading': 6.0, 'Writing': 6.0, 'Speaking': 7.0}), 6.5)
        self.assertEqual(overall({'Listening': 7.0, 'Reading': 6.5, 'Writing': 6.0, 'Speaking': 6.5}), 6.5)

    def test_one_missing_section_means_no_overall(self):
        for missing in ('Listening', 'Reading', 'Writing', 'Speaking'):
            with self.subTest(missing=missing):
                bands = {'Listening': 6.0, 'Reading': 6.0, 'Writing': 6.0, 'Speaking': 6.0}
                bands[missing] = None
                self.assertIsNone(overall(bands))
        self.assertIsNone(overall({}))
