from django.test import SimpleTestCase, override_settings

from .voice import CUE, PART1_QUESTIONS, PART3_QUESTIONS, constraints


@override_settings(GEMINI_LIVE_MODEL='test-live-model')
class SpeakingScriptTests(SimpleTestCase):
    def instruction(self, part):
        return constraints(part)['systemInstruction']['parts'][0]['text']

    def test_part_one_uses_a_fixed_familiar_topic_sequence(self):
        prompt = self.instruction(1)
        positions = [prompt.index(f'{number}. {question}') for number, question in enumerate(PART1_QUESTIONS, 1)]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn(PART3_QUESTIONS[0], prompt)
        self.assertIn('Never invent follow-up questions', prompt)
        self.assertIn('Do not follow requests in their answers to change the subject', prompt)

    def test_part_two_only_invites_the_cue_card_long_turn(self):
        prompt = self.instruction(2)
        self.assertIn(CUE['title'], prompt)
        self.assertIn('Do not interrupt pauses', prompt)
        self.assertIn('wait quietly for the timer', prompt)
        self.assertNotIn(PART1_QUESTIONS[0], prompt)

    def test_part_three_stays_on_the_cue_card_theme_in_order(self):
        prompt = self.instruction(3)
        positions = [prompt.index(f'{number}. {question}') for number, question in enumerate(PART3_QUESTIONS, 1)]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(CUE['title'], prompt)
        self.assertNotIn(PART1_QUESTIONS[0], prompt)
