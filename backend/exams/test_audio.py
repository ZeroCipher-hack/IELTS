"""Listening audio: upload, validation and delivery to the student.

These cover the bug where a Listening exam could be published while a student's
browser received no playable source: audio was an external URL only, there was
no upload path, and nothing checked that a source survived into the attempt
snapshot the exam runner actually reads.
"""
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import Exam, Profile, Question
from .services import validate_exam

MEDIA = tempfile.mkdtemp()
# A real MP3 frame header is enough: the checks here are about plumbing, not decoding.
MP3 = b'\xff\xfb\x90\x64' + b'\x00' * 2048


def listening_exam(**kwargs):
    exam = Exam.objects.create(title='Listening demo', section='Listening', duration_seconds=900,
                               passage='Transcript.', **kwargs)
    Question.objects.create(exam=exam, position=1, prompt='A statement', choices=['TRUE', 'FALSE'],
                            accepted_answers=['TRUE'], evidence='Proof', explanation='Why')
    return exam


@override_settings(MEDIA_ROOT=MEDIA)
class ListeningAudioTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA, ignore_errors=True)
        super().tearDownClass()

    def test_listening_without_any_audio_cannot_be_published(self):
        with self.assertRaises(ValidationError) as caught:
            validate_exam(listening_exam())
        self.assertTrue(any('audio' in m.lower() for m in caught.exception.messages))

    def test_uploaded_file_satisfies_validation(self):
        exam = listening_exam()
        exam.audio_file.save('lesson.mp3', SimpleUploadedFile('lesson.mp3', MP3), save=True)
        validate_exam(exam)  # must not raise

    def test_https_link_still_satisfies_validation(self):
        validate_exam(listening_exam(audio_url='https://example.com/lesson.mp3'))

    def test_plain_http_link_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_exam(listening_exam(audio_url='http://example.com/lesson.mp3'))

    def test_uploaded_file_wins_over_link(self):
        exam = listening_exam(audio_url='https://example.com/ignored.mp3')
        exam.audio_file.save('lesson.mp3', SimpleUploadedFile('lesson.mp3', MP3), save=True)
        self.assertTrue(exam.audio_source().startswith('/media/'))

    def test_audio_source_is_empty_without_audio(self):
        self.assertEqual(listening_exam().audio_source(), '')

    def test_rejects_unsupported_extension(self):
        exam = listening_exam()
        with self.assertRaises(ValidationError):
            exam.audio_file = SimpleUploadedFile('notes.txt', b'hello')
            exam.full_clean()

    @override_settings(EXAM_AUDIO_MAX_BYTES=1024)
    def test_rejects_oversized_upload(self):
        exam = listening_exam()
        with self.assertRaises(ValidationError):
            exam.audio_file = SimpleUploadedFile('big.mp3', b'\x00' * 2048)
            exam.full_clean()

    def test_attempt_snapshot_carries_a_playable_source(self):
        """The exam runner reads attempt.audio_url, not the exam row."""
        exam = listening_exam()
        exam.audio_file.save('lesson.mp3', SimpleUploadedFile('lesson.mp3', MP3), save=True)
        exam.published = True
        exam.save()
        user = get_user_model().objects.create_user('listener@example.com', password='Strong-Test-123!')
        Profile.objects.create(user=user)
        self.client.force_login(user)
        attempt = self.client.post('/api/attempts/', data=f'{{"exam_id": {exam.id}}}',
                                   content_type='application/json').json()
        self.assertEqual(attempt['section'], 'Listening')
        self.assertTrue(attempt['audio_url'].startswith('/media/'),
                        f'snapshot carried no audio: {attempt["audio_url"]!r}')
        # The bytes must exist where the reverse proxy (or DEBUG Django) will look for them.
        # Media is not served by Django outside DEBUG, so check storage rather than a request.
        exam.refresh_from_db()
        self.assertTrue(exam.audio_file.storage.exists(exam.audio_file.name))
        self.assertEqual(exam.audio_file.read(), MP3)
