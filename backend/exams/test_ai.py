import json
from unittest.mock import patch
from django.test import TestCase,override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Exam,Question,Attempt,AssessmentJob
from .gemini import AIError,validate_report,validate_objective_report,assess_objective,CRITERIA,assess_writing
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
            self.assertIn('systemInstruction',mocked.call_args.args[1]['bidiGenerateContentSetup'])
            setup=mocked.call_args.args[1]['bidiGenerateContentSetup']
            self.assertEqual(setup['generationConfig']['responseModalities'],['AUDIO'])
            self.assertNotIn('config',setup)
            self.assertNotIn('liveConnectConstraints',mocked.call_args.args[1])
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
            locked=mocked.call_args.args[1]['bidiGenerateContentSetup']
            self.assertIn('Part 2',locked['systemInstruction']['parts'][0]['text'])
            self.assertIn('inputAudioTranscription',locked)
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

@override_settings(AI_ENABLED=True,GEMINI_API_KEY='test-only-placeholder')
class ObjectiveCoachingTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('coaching@example.com')
        self.client.force_login(self.user)
        self.exam=Exam.objects.create(title='Reading coaching',section='Reading',published=True,
            passage='The council planted native reeds in 2021.',duration_seconds=600)
        Question.objects.create(exam=self.exam,position=1,prompt='When were reeds planted?',
            choices=['2021','2022'],accepted_answers=['2021'],
            evidence='The council planted native reeds in 2021.',explanation='The text says 2021.')
    def start_and_submit(self,answer):
        started=self.client.post('/api/attempts/',data=json.dumps({'exam_id':self.exam.pk}),content_type='application/json')
        self.assertEqual(started.status_code,201)
        return self.client.post('/api/attempts/'+started.json()['id']+'/submit/',
            data=json.dumps({'answers':{'1':answer}}),content_type='application/json').json()
    def test_ai_explains_wrong_answer_without_regrading(self):
        response=self.start_and_submit('2022')
        self.assertEqual(response['result']['correct'],0)
        self.assertIsNone(response['result']['band'])
        self.assertTrue(AssessmentJob.objects.filter(attempt_id=response['id']).exists())
        attempt=Attempt.objects.get(pk=response['id'])
        report=validate_objective_report({'items':[{'position':1,'evidence':'The council planted native reeds in 2021.',
            'why':'2022 matnda yo‘q.','next_step':'Matndan sanani belgilang.'}]},attempt)
        with patch('exams.management.commands.assess_pending.assess_objective',return_value=report):
            self.assertTrue(process_one())
        refreshed=self.client.get('/api/attempts/'+response['id']+'/').json()
        self.assertEqual(refreshed['result']['correct'],0)
        self.assertIsNone(refreshed['result']['band'])
        self.assertEqual(refreshed['result']['tutoring']['items'][0]['next_step'],'Matndan sanani belgilang.')
        self.assertEqual(refreshed['tutoring_status'],'done')
    def test_legacy_result_missing_optional_fields_does_not_crash_worker(self):
        response=self.start_and_submit('2022')
        attempt=Attempt.objects.get(pk=response['id'])
        attempt.result['rows'][0]={'position':1,'correct':False}
        attempt.save(update_fields=['result'])
        provider={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'items':[
            {'position':1,'evidence':'','why':'Check the date.','next_step':'Read the passage again.'}]})}]}}]}
        with patch('exams.gemini.post',return_value=provider) as mocked:
            self.assertTrue(process_one())
        payload=json.loads(mocked.call_args.args[1]['contents'][0]['parts'][0]['text'])
        self.assertEqual(payload['mistakes'][0]['correct_answers'],[])
        job=AssessmentJob.objects.get(attempt=attempt)
        self.assertEqual(job.state,'done')
        attempt.refresh_from_db()
        self.assertEqual(attempt.result['correct'],0)
    def test_malformed_legacy_rows_return_ai_error_instead_of_stuck_lease(self):
        response=self.start_and_submit('2022')
        attempt=Attempt.objects.get(pk=response['id'])
        attempt.result['rows']='invalid'
        attempt.save(update_fields=['result'])
        self.assertTrue(process_one())
        job=AssessmentJob.objects.get(attempt=attempt)
        self.assertEqual(job.state,'pending')
        self.assertEqual(job.error_code,'AI_INVALID_REPORT')
    def test_rejects_invented_evidence_and_missing_position(self):
        response=self.start_and_submit('2022')
        attempt=Attempt.objects.get(pk=response['id'])
        with self.assertRaises(AIError):
            validate_objective_report({'items':[{'position':1,'evidence':'invented quotation','why':'Wrong year',
                'next_step':'Check the date'}]},attempt)
        with self.assertRaises(AIError):validate_objective_report({'items':[]},attempt)
    def test_not_given_feedback_cannot_claim_a_supporting_quote(self):
        response=self.start_and_submit('2022')
        attempt=Attempt.objects.get(pk=response['id'])
        attempt.result['rows'][0]['accepted_answers']=['NOT GIVEN']
        with self.assertRaises(AIError):
            validate_objective_report({'items':[{'position':1,'evidence':'The council planted native reeds in 2021.',
                'why':'No evidence for the claim.','next_step':'Compare the exact statement.'}]},attempt)

    def test_provider_returns_validated_explanation(self):
        response=self.start_and_submit('2022')
        attempt=Attempt.objects.get(pk=response['id'])
        raw={'items':[{'position':1,'evidence':'The council planted native reeds in 2021.',
                       'why':'2022 is absent.','next_step':'Check the year in the passage.'}]}
        provider={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(raw)}]}}]}
        with patch('exams.gemini.post',return_value=provider) as mocked:
            report=assess_objective(attempt)
        self.assertEqual(report['items'][0]['position'],1)
        self.assertEqual(report['kind'],'ai_explanation')
        self.assertNotIn('audio_url',mocked.call_args.args[1]['contents'][0]['parts'][0]['text'])
    @override_settings(AI_ENABLED=False)
    def test_ai_disabled_keeps_answer_key_and_editor_feedback(self):
        response=self.start_and_submit('2022')
        self.assertEqual(response['result']['correct'],0)
        self.assertEqual(response['result']['rows'][0]['explanation'],'The text says 2021.')
        self.assertFalse(AssessmentJob.objects.filter(attempt_id=response['id']).exists())

    def test_correct_answer_does_not_queue_ai(self):
        response=self.start_and_submit('2021')
        self.assertEqual(response['result']['correct'],1)
        self.assertFalse(AssessmentJob.objects.filter(attempt_id=response['id']).exists())
