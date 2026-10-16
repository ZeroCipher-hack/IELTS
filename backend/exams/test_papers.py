"""The full-length papers must be exactly that, or they carry no band."""
import io

from django.core.management import call_command
from django.test import TestCase

from .bands import STANDARD_LENGTH, raw_band
from .models import Exam
from .papers import listening_campus, reading_transport
from .services import validate_exam


def run():
    out = io.StringIO()
    call_command('seed_papers', stdout=out, stderr=out)
    return out.getvalue()


class PaperContentTests(TestCase):
    """Checked without touching the database: these are facts about the source."""

    def papers(self):
        return (('Reading', reading_transport.ITEMS, reading_transport.PASSAGE),
                ('Listening', listening_campus.ITEMS, listening_campus.TRANSCRIPT))

    def test_each_paper_is_the_standard_length(self):
        for name, items, _ in self.papers():
            with self.subTest(paper=name):
                self.assertEqual(len(items), STANDARD_LENGTH)

    def test_every_answer_key_matches_its_choices(self):
        for name, items, _ in self.papers():
            for number, (_, choices, answers, _, _, _) in enumerate(items, 1):
                if not choices:
                    continue
                with self.subTest(paper=name, question=number):
                    self.assertTrue(set(answers) <= set(choices))

    def test_every_evidence_quote_is_verbatim(self):
        """The results page searches the passage for this string; a quote that
        is not there shows the student no evidence at all."""
        for name, items, text in self.papers():
            for number, (_, _, _, evidence, _, _) in enumerate(items, 1):
                if not evidence:
                    continue
                with self.subTest(paper=name, question=number):
                    self.assertIn(evidence, text)

    def test_only_not_given_questions_may_omit_evidence(self):
        for name, items, _ in self.papers():
            for number, (_, _, answers, evidence, _, _) in enumerate(items, 1):
                if evidence:
                    continue
                with self.subTest(paper=name, question=number):
                    self.assertEqual(answers, ['NOT GIVEN'])

    def test_every_question_carries_an_answer_and_an_explanation(self):
        for name, items, _ in self.papers():
            for number, (prompt, _, answers, _, explanation, tag) in enumerate(items, 1):
                with self.subTest(paper=name, question=number):
                    self.assertTrue(prompt.strip())
                    self.assertTrue(answers)
                    self.assertTrue(explanation.strip())
                    self.assertTrue(tag.strip())

    def test_the_listening_transcript_covers_all_four_parts(self):
        for part in ('PART 1', 'PART 2', 'PART 3', 'PART 4'):
            self.assertIn(part, listening_campus.TRANSCRIPT)

    def test_the_reading_passage_has_three_passages(self):
        for part in ('PASSAGE 1', 'PASSAGE 2', 'PASSAGE 3'):
            self.assertIn(part, reading_transport.PASSAGE)

    def test_no_paragraph_is_hard_wrapped(self):
        """Hard wrapping is why evidence matching silently failed before."""
        for name, _, text in self.papers():
            for block in text.split('\n\n'):
                with self.subTest(paper=name):
                    self.assertNotIn('\n', block)


class SeedPapersTests(TestCase):
    def test_reading_is_published_and_can_report_a_band(self):
        run()
        exam = Exam.objects.get(section='Reading', title=reading_transport.TITLE)
        self.assertTrue(exam.published)
        self.assertEqual(exam.questions.count(), STANDARD_LENGTH)
        validate_exam(exam)
        self.assertEqual(raw_band('Reading', 30, exam.questions.count()), 7.0)

    def test_listening_is_a_draft_until_it_has_audio(self):
        run()
        exam = Exam.objects.get(section='Listening', title=listening_campus.TITLE)
        self.assertFalse(exam.published, 'a Listening test without a recording is not a test')
        self.assertEqual(exam.questions.count(), STANDARD_LENGTH)
        with self.assertRaises(Exception):
            validate_exam(exam)

    def test_running_twice_creates_nothing_new(self):
        run()
        before = Exam.objects.count(), Exam.objects.get(section='Reading').questions.count()
        output = run()
        self.assertIn('allaqachon mavjud', output)
        self.assertEqual((Exam.objects.count(), Exam.objects.get(section='Reading').questions.count()), before)

    def test_question_order_and_positions_are_contiguous(self):
        run()
        for section in ('Reading', 'Listening'):
            positions = list(Exam.objects.get(section=section).questions.order_by('position')
                             .values_list('position', flat=True))
            with self.subTest(section=section):
                self.assertEqual(positions, list(range(1, STANDARD_LENGTH + 1)))
