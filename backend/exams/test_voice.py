from django.test import TestCase, override_settings

from .voice import CUE, PART1_QUESTIONS, PART3_QUESTIONS, access, constraints


@override_settings(GEMINI_LIVE_MODEL='test-live-model')
class SpeakingScriptTests(TestCase):
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
        self.assertIn('Say exactly: Please begin your talk. '+CUE['title'], prompt)
        self.assertNotIn(PART1_QUESTIONS[0], prompt)

    def test_part_three_stays_on_the_cue_card_theme_in_order(self):
        prompt = self.instruction(3)
        positions = [prompt.index(f'{number}. {question}') for number, question in enumerate(PART3_QUESTIONS, 1)]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(CUE['title'], prompt)
        self.assertNotIn(PART1_QUESTIONS[0], prompt)

    @override_settings(AI_ENABLED=True, GEMINI_API_KEY='test-key', VOICE_PRACTICE_ENABLED=True)
    def test_status_exposes_the_same_questions_as_the_locked_token(self):
        class User:
            is_staff = False

        status = access(User())
        self.assertEqual(tuple(status['questions']['1']), PART1_QUESTIONS)
        self.assertEqual(tuple(status['questions']['3']), PART3_QUESTIONS)
        for part in (1, 3):
            prompt = self.instruction(part)
            for question in status['questions'][str(part)]:
                self.assertIn(question, prompt)
