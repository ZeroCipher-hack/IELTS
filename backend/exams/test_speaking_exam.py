"""Speaking EXAM mode: a scripted interview driven by the question bank.

Distinct from the practice pilot in test_speaking.py, which is a live
conversation. Exam mode needs no live key: questions are delivered from the
bank, recordings are collected, and assessment happens afterwards like Writing.
"""
import shutil
import tempfile
import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .gemini import AIError
from .models import AssessmentJob, Attempt, Exam, Profile, Question, SpeakingRecording
from .services import validate_exam
from .speaking_assessment import CRITERIA, validate

MEDIA = tempfile.mkdtemp()
MP3 = b'\xff\xfb\x90\x64' + b'\x00' * 2048
WEBM = b'\x1aE\xdf\xa3' + b'0' * 400


def speaking_exam(parts=(1, 1, 2, 3), cue=('A point',), published=False):
    exam = Exam.objects.create(title='Speaking demo', section='Speaking', duration_seconds=900)
    for i, part in enumerate(parts, 1):
        Question.objects.create(exam=exam, position=i, part=part, prompt=f'Prompt {i}',
                                choices=list(cue) if part == 2 else [], accepted_answers=[])
    if published:
        exam.published = True
        exam.save()
    return exam


@override_settings(MEDIA_ROOT=MEDIA, EXAMS_OPEN_ACCESS=True)
class SpeakingExamShapeTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA, ignore_errors=True)
        super().tearDownClass()

    def test_a_complete_frame_validates(self):
        validate_exam(speaking_exam())  # must not raise

    def test_every_part_is_required(self):
        for missing, parts in (('Part 1', (2, 3)), ('Part 3', (1, 2))):
            with self.subTest(missing=missing), self.assertRaises(ValidationError) as caught:
                validate_exam(speaking_exam(parts=parts))
            self.assertTrue(any(missing in m for m in caught.exception.messages))

    def test_exactly_one_cue_card(self):
        with self.assertRaises(ValidationError):
            validate_exam(speaking_exam(parts=(1, 2, 2, 3)))
        with self.assertRaises(ValidationError):
            validate_exam(speaking_exam(parts=(1, 3)))

    def test_cue_card_needs_its_points(self):
        with self.assertRaises(ValidationError) as caught:
            validate_exam(speaking_exam(cue=()))
        self.assertTrue(any('cue card' in m for m in caught.exception.messages))

    def test_every_question_needs_a_part(self):
        exam = speaking_exam()
        exam.questions.filter(position=1).update(part=0)
        with self.assertRaises(ValidationError) as caught:
            validate_exam(exam)
        self.assertTrue(any('qism' in m for m in caught.exception.messages))


@override_settings(MEDIA_ROOT=MEDIA, EXAMS_OPEN_ACCESS=True)
class SpeakingExamFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = get_user_model().objects.create_user('candidate@example.com', password='Strong-Test-123!')
        Profile.objects.create(user=self.user)
        self.client.force_login(self.user)
        self.exam = speaking_exam(published=True)

    def start(self):
        return self.client.post('/api/attempts/', data=f'{{"exam_id": {self.exam.id}}}',
                                content_type='application/json')

    def test_speaking_is_no_longer_blocked(self):
        """It used to answer 503: the voice service was 'not connected yet'."""
        response = self.start()
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['section'], 'Speaking')

    def test_snapshot_carries_parts_and_cue_points(self):
        questions = self.start().json()['questions']
        self.assertEqual([q['part'] for q in questions], [1, 1, 2, 3])
        cue = next(q for q in questions if q['part'] == 2)
        self.assertEqual(cue['choices'], ['A point'])
        self.assertTrue(all('audio_url' in q for q in questions))

    def test_snapshot_carries_uploaded_question_audio(self):
        question = self.exam.questions.get(position=1)
        question.audio_file.save('q1.mp3', SimpleUploadedFile('q1.mp3', MP3), save=True)
        first = self.start().json()['questions'][0]
        self.assertTrue(first['audio_url'].startswith('/media/'), first['audio_url'])

    def test_question_without_audio_is_delivered_as_text(self):
        """An empty audio_url tells the runner to read the prompt aloud instead."""
        self.assertEqual(self.start().json()['questions'][0]['audio_url'], '')

    def submit(self, attempt_id, segments=3, consent='yes', transcript=''):
        return self.client.post('/api/voice/submit/', {
            'id': str(attempt_id), 'consent': consent, 'transcript': transcript,
            'audio': [SimpleUploadedFile(f'a{i}.webm', WEBM, content_type='audio/webm') for i in range(segments)],
        })

    def test_recordings_attach_to_the_running_attempt(self):
        attempt_id = self.start().json()['id']
        response = self.submit(attempt_id)
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['state'], 'awaiting_assessment')
        attempt = Attempt.objects.get(pk=attempt_id)
        self.assertEqual(attempt.speaking_recording.segments.__len__(), 3)
        self.assertEqual(AssessmentJob.objects.filter(attempt=attempt).count(), 1)
        self.assertEqual(Attempt.objects.count(), 1, 'no second attempt may be created')

    def test_exam_accepts_more_segments_than_practice(self):
        attempt_id = self.start().json()['id']
        self.assertEqual(self.submit(attempt_id, segments=8).status_code, 201)

    def test_exam_submission_needs_no_live_key_or_practice_flag(self):
        """Practice is gated on VOICE_PRACTICE_ENABLED and a key; an exam is not.

        A candidate admitted to the exam must never record answers and then be
        refused at submission because an unrelated feature flag is off.
        """
        with self.settings(AI_ENABLED=False, GEMINI_API_KEY='', VOICE_PRACTICE_ENABLED=False):
            attempt_id = self.start().json()['id']
            self.assertEqual(self.submit(attempt_id).status_code, 201)

    def test_consent_is_still_required(self):
        attempt_id = self.start().json()['id']
        self.assertEqual(self.submit(attempt_id, consent='no').status_code, 400)
        self.assertEqual(Attempt.objects.get(pk=attempt_id).state, 'in_progress')

    def test_resubmission_is_idempotent(self):
        attempt_id = self.start().json()['id']
        self.assertEqual(self.submit(attempt_id).status_code, 201)
        again = self.submit(attempt_id)
        self.assertEqual(again.status_code, 200)
        self.assertEqual(AssessmentJob.objects.count(), 1)

    def test_another_user_cannot_submit_into_the_attempt(self):
        attempt_id = self.start().json()['id']
        intruder = get_user_model().objects.create_user('intruder@example.com', password='Strong-Test-123!')
        Profile.objects.create(user=intruder)
        self.client.force_login(intruder)
        with self.settings(VOICE_PRACTICE_ENABLED=True, AI_ENABLED=True, GEMINI_API_KEY='k'):
            # A long transcript would otherwise satisfy the practice path's own
            # rules, so this proves ownership is checked before any of them.
            response = self.submit(attempt_id, transcript='I live with my family in a small apartment.')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Attempt.objects.get(pk=attempt_id).state, 'in_progress')
        self.assertFalse(SpeakingRecording.objects.filter(attempt_id=attempt_id).exists())


class ExamTranscriptTests(TestCase):
    """Exam mode has no live transcription, so the model supplies the transcript."""

    def report(self, quote, transcript=None):
        data = {'sufficient_audio': True, 'criteria': dict.fromkeys(CRITERIA, 6.0),
                'feedback': 'F', 'improvement': 'I', 'strengths': 'S',
                'examples': [{'quote': quote, 'explanation': 'E', 'better_answer': 'B'}]}
        if transcript is not None:
            data['transcript'] = transcript
        return data

    def test_model_transcript_is_used_when_the_client_has_none(self):
        result = validate(self.report('a new skill', 'I would like to learn a new skill.'), '')
        self.assertEqual(result['band'], 6.0)
        self.assertEqual(result['transcript'], 'I would like to learn a new skill.')

    def test_quotes_are_still_checked_against_that_transcript(self):
        with self.assertRaises(AIError):
            validate(self.report('something never said', 'I would like to learn a new skill.'), '')

    def test_a_missing_transcript_is_rejected(self):
        with self.assertRaises(AIError):
            validate(self.report('a new skill'), '')
        with self.assertRaises(AIError):
            validate(self.report('a new skill', '   '), '')

    def test_a_client_transcript_still_wins(self):
        result = validate(self.report('my family', 'IGNORED'), 'I live with my family')
        self.assertEqual(result['transcript'], 'I live with my family')
