import io,uuid
from unittest.mock import patch
from django.test import TestCase,override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Attempt,SpeakingRecording,AssessmentJob
from .speaking_assessment import validate,CRITERIA
from .gemini import AIError

@override_settings(AI_ENABLED=True,GEMINI_API_KEY='test-placeholder',VOICE_PRACTICE_ENABLED=True)
class SpeakingTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username='speaker',password='test-password')
        self.client.force_login(self.user)
    def upload(self,identifier=None,consent='yes'):
        return self.client.post('/api/voice/submit/',{'id':str(identifier or uuid.uuid4()),'consent':consent,'transcript':'I live in a small apartment with my family.',
          'audio':SimpleUploadedFile('part.webm',b'\x1aE\xdf\xa3'+b'0'*200,content_type='audio/webm')})
    def test_submission_is_private_and_idempotent(self):
        identifier=uuid.uuid4();r=self.upload(identifier)
        self.assertEqual(r.status_code,201);self.assertEqual(r.json()['state'],'awaiting_assessment')
        self.assertEqual(self.upload(identifier).status_code,200)
        self.assertEqual(Attempt.objects.count(),1);self.assertEqual(AssessmentJob.objects.count(),1)
        self.assertNotIn('segments',r.json())
        other=get_user_model().objects.create_user(username='other');self.client.force_login(other)
        self.assertEqual(self.client.get('/api/attempts/'+str(identifier)+'/').status_code,404)
        self.assertEqual(self.upload(identifier).status_code,409)
    def test_consent_and_auth_required(self):
        self.assertEqual(self.upload(consent='no').status_code,400)
        self.client.logout();self.assertEqual(self.upload().status_code,401)
    def test_validation_rejects_invented_quotes_and_silence(self):
        data={'sufficient_audio':True,'criteria':dict.fromkeys(CRITERIA,6.5),'feedback':'Feedback','improvement':'Plan','strengths':'Strength',
          'examples':[{'quote':'my family','explanation':'Explain','better_answer':'I share an apartment with my family.'}]}
        self.assertEqual(validate(data,'I live with my family')['band'],6.5)
        with self.assertRaises(AIError):validate(data,'Unrelated text')
        data['sufficient_audio']=False
        with self.assertRaises(AIError):validate(data,'I live with my family')
    def test_worker_saves_feedback_and_removes_audio(self):
        from .management.commands.assess_pending import process_one
        self.upload();report={'band':6.5,'tasks':[],'kind':'ai_speaking'}
        with patch('exams.management.commands.assess_pending.assess_speaking',return_value=report):self.assertTrue(process_one())
        self.assertEqual(Attempt.objects.get().state,'graded');self.assertFalse(SpeakingRecording.objects.exists())
