"""The whole chain on the real papers: four sections in, one overall band out.

The unit tests build attempts by hand. This one drives the real API with the
real 40-question papers, because the claim that matters to a candidate -- "you
will get an overall band" -- depends on the papers, the conversion table, the
sitting and the API agreeing with each other, not on any one of them.
"""
import json

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Attempt, Exam, ExamSession, Profile
from .papers import listening_campus, reading_transport


@override_settings(EXAMS_OPEN_ACCESS=True)
class FullSittingOnRealPapersTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_papers', stdout=open('/dev/null', 'w'))
        # The Listening paper seeds as a draft because it needs a recording;
        # the sitting cannot start without it, so give it one.
        listening = Exam.objects.get(section='Listening', title=listening_campus.TITLE)
        listening.audio_url = 'https://example.com/riverside.mp3'
        listening.published = True
        listening.save()
        Exam.objects.create(title='W', section='Writing', duration_seconds=3600,
                            passage='Both tasks.', published=True).questions.create(
            position=1, prompt='Task 1', accepted_answers=[])
        speaking = Exam.objects.create(title='S', section='Speaking', duration_seconds=900,
                                       passage='Three parts.')
        for position, part in ((1, 1), (2, 2), (3, 3)):
            speaking.questions.create(position=position, part=part, prompt=f'P{position}',
                                      choices=['A point'] if part == 2 else [],
                                      accepted_answers=[])
        speaking.published = True
        speaking.save()

    def setUp(self):
        self.user = get_user_model().objects.create_user('sit@example.com', password='Strong-Test-123!')
        Profile.objects.create(user=self.user)
        self.client.force_login(self.user)

    def take(self, stage, correct):
        """Start a section and submit `correct` right answers."""
        started = self.client.post('/api/attempts/', content_type='application/json',
                                   data=json.dumps({'exam_id': stage['exam_id'],
                                                    'session_id': self.sitting['id'],
                                                    'accept_pending_assessment': True}))
        self.assertEqual(started.status_code, 201, started.content)
        attempt = Attempt.objects.get(pk=started.json()['id'])
        answers = {}
        for question in sorted(attempt.snapshot['questions'], key=lambda q: q['position'])[:correct]:
            answers[str(question['position'])] = question['accepted_answers'][0]
        response = self.client.post(f'/api/attempts/{attempt.id}/submit/',
                                    data=json.dumps({'answers': answers}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200, response.content)
        return attempt

    def assessed(self, attempt, band):
        """Stand in for the worker, which needs a provider key."""
        attempt.result = {'correct': 0, 'total': 0, 'rows': [], 'skills': {},
                          'weekly_plan': [], 'band': band,
                          'assessment': {'kind': 'ai_writing', 'estimated': True, 'band': band}}
        attempt.state = 'graded'
        attempt.save(update_fields=['result', 'state'])

    def test_a_complete_sitting_reports_an_overall_band(self):
        self.sitting = self.client.post('/api/sessions/', data='{}',
                                        content_type='application/json').json()
        self.assertEqual([s['section'] for s in self.sitting['stages']], ExamSession.ORDER)

        listening = self.take(self.sitting['stages'][0], correct=30)
        reading = self.take(self.sitting['stages'][1], correct=30)

        half = self.client.get(f'/api/sessions/{self.sitting["id"]}/').json()
        self.assertEqual(half['stages'][0]['band'], 7.0, 'Listening 30/40 is band 7.0')
        self.assertEqual(half['stages'][1]['band'], 7.0, 'Reading 30/40 is band 7.0')
        self.assertEqual([s['band_source'] for s in half['stages'][:2]], ['table', 'table'])
        self.assertIsNone(half['overall_band'], 'two sections are not an exam')

        writing = self.take(self.sitting['stages'][2], correct=0)
        speaking = self.take(self.sitting['stages'][3], correct=0)
        self.assessed(writing, 6.5)
        self.assessed(speaking, 6.0)

        final = self.client.get(f'/api/sessions/{self.sitting["id"]}/').json()
        self.assertEqual(final['state'], 'completed')
        self.assertEqual([s['band'] for s in final['stages']], [7.0, 7.0, 6.5, 6.0])
        # (7.0 + 7.0 + 6.5 + 6.0) / 4 = 6.625 -> 6.5
        self.assertEqual(final['overall_band'], 6.5)
        self.assertTrue(final['estimated'])
        self.assertIn('Rasmiy IELTS bandi emas', final['note'])
        self.assertEqual(final['sections_without_band'], [])
        self.assertEqual(final['awaiting_assessment'], [])
        self.assertEqual(listening.snapshot['section'], 'Listening')
        self.assertEqual(reading.snapshot['section'], 'Reading')

    def test_the_papers_really_are_full_length(self):
        sitting = self.client.post('/api/sessions/', data='{}',
                                   content_type='application/json').json()
        counts = {s['section']: s['question_count'] for s in sitting['stages']}
        self.assertEqual(counts['Listening'], 40)
        self.assertEqual(counts['Reading'], 40)

    def test_a_short_paper_withholds_the_overall_band(self):
        """Publish a six-question Listening set and the overall must vanish."""
        short = Exam.objects.create(title='Short listening', section='Listening',
                                    duration_seconds=900, passage='Transcript.',
                                    audio_url='https://example.com/short.mp3')
        for position in range(1, 7):
            short.questions.create(position=position, prompt=f'Q{position}',
                                   accepted_answers=['yes'])
        short.published = True
        short.save()

        self.sitting = self.client.post('/api/sessions/', data='{}',
                                        content_type='application/json').json()
        self.assertEqual(self.sitting['stages'][0]['question_count'], 6,
                         'the newest published paper is the short one')
        self.take(self.sitting['stages'][0], correct=5)
        self.take(self.sitting['stages'][1], correct=30)
        writing = self.take(self.sitting['stages'][2], correct=0)
        speaking = self.take(self.sitting['stages'][3], correct=0)
        self.assessed(writing, 6.5)
        self.assessed(speaking, 6.0)

        final = self.client.get(f'/api/sessions/{self.sitting["id"]}/').json()
        self.assertIsNone(final['overall_band'])
        self.assertEqual(final['sections_without_band'], ['Listening'])
        self.assertEqual((final['stages'][0]['correct'], final['stages'][0]['total']), (5, 6))

    def test_reading_evidence_is_findable_in_the_passage(self):
        """The results page searches for it; a quote it cannot find shows nothing."""
        attempt = Attempt.objects.create(
            user=self.user,
            exam=Exam.objects.get(section='Reading', title=reading_transport.TITLE),
            snapshot={'title': 'x', 'section': 'Reading', 'version': 1,
                      'passage': reading_transport.PASSAGE, 'questions': []},
            deadline=ExamSession.objects.create(user=self.user, plan=[]).started_at)
        for _, _, _, evidence, _, _ in reading_transport.ITEMS:
            if evidence:
                self.assertIn(evidence, attempt.snapshot['passage'])
