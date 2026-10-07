import shutil,tempfile
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase,override_settings
from .models import Exam,Question
from .services import validate_exam

TMP=tempfile.mkdtemp()
DATA=bytes(range(256))*40

@override_settings(MEDIA_ROOT=TMP,EXAMS_OPEN_ACCESS=True)
class ListeningAudioTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass();shutil.rmtree(TMP,ignore_errors=True)
    def setUp(self):
        self.user=get_user_model().objects.create_user('a@example.com',password='x')
        self.other=get_user_model().objects.create_user('b@example.com',password='x')
        self.exam=Exam.objects.create(title='L',section='Listening',duration_seconds=600)
        self.exam.audio_file.save('talk.mp3',ContentFile(DATA))
        Question.objects.create(exam=self.exam,position=1,prompt='Q',choices=[],accepted_answers=['yes'])
        self.exam.published=True;self.exam.save()
        self.client.force_login(self.user)
        self.attempt=self.client.post('/api/attempts/',data={'exam_id':self.exam.id},content_type='application/json').json()
    def url(self):return f"/api/attempts/{self.attempt['id']}/audio"
    def test_attempt_points_to_protected_audio(self):
        self.assertEqual(self.attempt['audio_url'],self.url())
        self.assertNotIn('exam_audio',str(self.attempt))
    def test_full_and_partial_content(self):
        full=self.client.get(self.url());self.assertEqual(full.status_code,200)
        self.assertEqual(b''.join(full.streaming_content),DATA);self.assertEqual(full['Accept-Ranges'],'bytes')
        part=self.client.get(self.url(),HTTP_RANGE='bytes=100-199');self.assertEqual(part.status_code,206)
        self.assertEqual(b''.join(part.streaming_content),DATA[100:200]);self.assertEqual(part['Content-Range'],f'bytes 100-199/{len(DATA)}')
        tail=self.client.get(self.url(),HTTP_RANGE='bytes=-50');self.assertEqual(b''.join(tail.streaming_content),DATA[-50:])
        self.assertEqual(self.client.get(self.url(),HTTP_RANGE=f'bytes={len(DATA)+5}-').status_code,416)
    def test_other_user_and_anonymous_denied(self):
        self.client.force_login(self.other);self.assertEqual(self.client.get(self.url()).status_code,404)
        self.client.logout();self.assertEqual(self.client.get(self.url()).status_code,401)
    def test_listening_needs_audio_to_publish(self):
        bare=Exam.objects.create(title='No audio',section='Listening')
        Question.objects.create(exam=bare,position=1,prompt='Q',choices=[],accepted_answers=['yes'])
        with self.assertRaises(ValidationError):validate_exam(bare)
