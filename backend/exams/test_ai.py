import json
from unittest.mock import patch
from django.test import TestCase,override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Exam,Attempt,AssessmentJob
from .gemini import AIError,validate_report,CRITERIA,assess_writing
from .management.commands.assess_pending import process_one

@override_settings(AI_ENABLED=True,GEMINI_API_KEY='test-only-placeholder')
class AIIntegrationTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('pilot@example.com')
        self.exam=Exam.objects.create(title='Writing',section='Writing')
        self.attempt=Attempt.objects.create(user=self.user,exam=self.exam,state='awaiting_assessment',deadline=timezone.now(),
          snapshot={'section':'Writing','title':'Writing','questions':[{'position':2,'prompt':'Discuss transport.'}]},answers={'2':'Reliable buses help students.'})
        self.report={'tasks':[{'position':2,'criteria':dict.fromkeys(CRITERIA,6),'evidence':'Reliable buses','feedback':'Develop the idea.','improvement':'Add an example.'}]}
    def test_rejects_invented_evidence(self):
        self.report['tasks'][0]['evidence']='invented quotation'
        with self.assertRaises(AIError):validate_report(self.report,self.attempt)
    def test_rejects_impossible_band(self):
        self.report['tasks'][0]['criteria']['grammar']=10
        with self.assertRaises(AIError):validate_report(self.report,self.attempt)
    def test_rejects_duplicate_tasks(self):
        self.report['tasks']*=2
        with self.assertRaises(AIError):validate_report(self.report,self.attempt)
    def test_transport_uses_validated_json(self):
        response={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(self.report)}]}}]}
        with patch('exams.gemini.post',return_value=response):self.assertEqual(assess_writing(self.attempt)['band'],6)
    def test_worker_idempotency(self):
        AssessmentJob.objects.create(attempt=self.attempt)
        with patch('exams.management.commands.assess_pending.assess_writing',return_value=validate_report(self.report,self.attempt)) as mocked:
            self.assertTrue(process_one());self.assertFalse(process_one());self.assertEqual(mocked.call_count,1)
        self.attempt.refresh_from_db();self.assertEqual(self.attempt.result['band'],6);self.assertEqual(self.attempt.state,'graded')
    def test_rate_limit_never_fabricates_score(self):
        job=AssessmentJob.objects.create(attempt=self.attempt,tries=2)
        with patch('exams.management.commands.assess_pending.assess_writing',side_effect=AIError('AI_RATE_LIMIT')):process_one()
        job.refresh_from_db();self.attempt.refresh_from_db()
        self.assertEqual(job.state,'failed');self.assertIsNone(self.attempt.result)
    def test_voice_denied_to_student(self):
        self.client.force_login(self.user)
        with patch('exams.gemini.post') as mocked:
            self.assertEqual(self.client.post('/api/voice/token/',data='{}',content_type='application/json').status_code,403)
            mocked.assert_not_called()
    def test_voice_token_is_one_use_and_constrained(self):
        self.user.is_staff=True;self.user.save();self.client.force_login(self.user)
        with patch('exams.gemini.post',return_value={'name':'ephemeral-test-token'}) as mocked:
            response=self.client.post('/api/voice/token/',data='{}',content_type='application/json')
            self.assertEqual(response.status_code,200);self.assertEqual(response['Cache-Control'],'no-store')
            self.assertEqual(mocked.call_args.args[1]['uses'],1)
            self.assertIn('systemInstruction',mocked.call_args.args[1]['liveConnectConstraints']['config'])
            self.assertNotIn('test-only-placeholder',response.content.decode())
    def test_voice_status_does_not_expose_key(self):
        self.client.force_login(self.user)
        response=self.client.get('/api/voice/status/')
        self.assertTrue(response.json()['configured']);self.assertFalse(response.json()['allowed'])
        self.assertNotIn('test-only-placeholder',response.content.decode())
    @override_settings(VOICE_PRACTICE_ENABLED=True)
    def test_student_practice_flag_and_part_constraints(self):
        self.client.force_login(self.user)
        with patch('exams.gemini.post',return_value={'name':'ephemeral-test-token'}) as mocked:
            response=self.client.post('/api/voice/token/',data=json.dumps({'part':2}),content_type='application/json')
            self.assertEqual(response.status_code,200)
            locked=mocked.call_args.args[1]['liveConnectConstraints']
            self.assertIn('Part 2',locked['config']['systemInstruction']['parts'][0]['text'])
            self.assertIn('inputAudioTranscription',locked['config'])
    def test_bad_part_does_not_call_provider(self):
        self.user.is_staff=True;self.user.save();self.client.force_login(self.user)
        with patch('exams.gemini.post') as mocked:
            for part in [0,4,True,'2']:
                self.assertEqual(self.client.post('/api/voice/token/',data=json.dumps({'part':part}),content_type='application/json').status_code,400)
            mocked.assert_not_called()
    @override_settings(AI_ENABLED=False)
    def test_voice_missing_configuration_reported(self):
        self.user.is_staff=True;self.user.save();self.client.force_login(self.user)
        self.assertEqual(self.client.get('/api/voice/status/').json()['reason'],'AI_NOT_CONFIGURED')
        with patch('exams.gemini.post') as mocked:
            self.assertEqual(self.client.post('/api/voice/token/',data='{}',content_type='application/json').status_code,503)
            mocked.assert_not_called()
