import json
from datetime import timedelta
from django.test import TestCase,Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Exam,Question,Attempt,Profile
class ExamFlowTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('learner@example.com',password='Strong-Test-123!')
        self.other=get_user_model().objects.create_user('other@example.com',password='Strong-Test-123!')
        Profile.objects.create(user=self.user)
        self.exam=Exam.objects.create(title='Test',section='Reading',published=True,duration_seconds=600,passage='A reading passage.')
        Question.objects.create(exam=self.exam,position=1,prompt='A statement',choices=['TRUE','FALSE'],accepted_answers=['TRUE'],evidence='Proof',explanation='Explanation')
        self.client.force_login(self.user)
    def test_catalog_access_is_personal_and_resumable(self):
        from .models import Entitlement
        Entitlement.objects.create(user=self.other,exam=self.exam,reference='other-access')
        self.assertFalse(self.client.get('/api/catalog/').json()['exams'][0]['has_access'])
        a=self.start().json()
        self.assertTrue(self.client.get('/api/catalog/').json()['exams'][0]['has_access'])
        self.client.post(f"/api/attempts/{a['id']}/submit/",data='{}',content_type='application/json')
        self.assertFalse(self.client.get('/api/catalog/').json()['exams'][0]['has_access'])
        Entitlement.objects.create(user=self.user,exam=self.exam,reference='own-access')
        self.assertTrue(self.client.get('/api/catalog/').json()['exams'][0]['has_access'])
    def test_display_name_uses_saved_name_not_email(self):
        self.assertEqual(self.client.get('/api/session/').json()['user']['name'],'')
        response=self.client.patch('/api/profile/',data=json.dumps({'name':'Tolqin'}),content_type='application/json')
        self.assertEqual(response.json()['user']['name'],'Tolqin')
    def start(self):return self.client.post('/api/attempts/',data=json.dumps({'exam_id':self.exam.pk}),content_type='application/json')
    def test_answer_keys_hidden_and_cross_user_denied(self):
        data=self.start().json();self.assertNotIn('accepted_answers',data['questions'][0]);self.assertNotIn('evidence',data['questions'][0])
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f"/api/attempts/{data['id']}/").status_code,404)
    def test_grading_idempotent_and_one_free_attempt(self):
        data=self.start().json();id=data['id']
        self.assertEqual(self.start().json()['id'],id)
        result=self.client.post(f'/api/attempts/{id}/submit/',data=json.dumps({'answers':{'1':' true '}}),content_type='application/json').json()
        self.assertEqual(result['result']['correct'],1)
        again=self.client.post(f'/api/attempts/{id}/submit/',data=json.dumps({'answers':{'1':'FALSE'}}),content_type='application/json').json()
        self.assertEqual(again['result']['correct'],1)
        self.assertEqual(self.start().status_code,402)
    def test_deadline_rejects_late_answers(self):
        id=self.start().json()['id'];Attempt.objects.filter(pk=id).update(deadline=timezone.now()-timedelta(seconds=1))
        self.assertEqual(self.client.patch(f'/api/attempts/{id}/',data=json.dumps({'answers':{'1':'TRUE'}}),content_type='application/json').status_code,409)
        data=self.client.post(f'/api/attempts/{id}/submit/',data=json.dumps({'answers':{'1':'TRUE'}}),content_type='application/json').json()
        self.assertEqual(data['result']['correct'],0)
    def test_snapshot_survives_content_change(self):
        id=self.start().json()['id'];Question.objects.filter(exam=self.exam).update(accepted_answers=['FALSE'])
        data=self.client.post(f'/api/attempts/{id}/submit/',data=json.dumps({'answers':{'1':'TRUE'}}),content_type='application/json').json()
        self.assertEqual(data['result']['correct'],1)
    def test_csrf_required_for_authentication(self):
        c=Client(enforce_csrf_checks=True)
        self.assertEqual(c.post('/api/login/',data='{}',content_type='application/json').status_code,403)
    def test_unauthenticated_access_denied(self):
        self.client.logout();self.assertEqual(self.client.get('/api/attempts/').status_code,401)
    def test_unknown_question_rejected(self):
        id=self.start().json()['id']
        self.assertEqual(self.client.patch(f'/api/attempts/{id}/',data=json.dumps({'answers':{'999':'TRUE'}}),content_type='application/json').status_code,400)
    def test_saved_answers_used_after_deadline(self):
        id=self.start().json()['id']
        self.client.patch(f'/api/attempts/{id}/',data=json.dumps({'answers':{'1':'TRUE'}}),content_type='application/json')
        Attempt.objects.filter(pk=id).update(deadline=timezone.now()-timedelta(seconds=1))
        data=self.client.post(f'/api/attempts/{id}/submit/',data='{}',content_type='application/json').json()
        self.assertEqual(data['result']['correct'],1)
    def test_writing_requires_acknowledgment_and_never_fabricates_grade(self):
        exam=Exam.objects.create(title='Writing',section='Writing',published=True,duration_seconds=3600)
        Question.objects.create(exam=exam,position=1,prompt='Discuss public transport.',accepted_answers=[])
        url='/api/attempts/'
        self.assertEqual(self.client.post(url,data=json.dumps({'exam_id':exam.id}),content_type='application/json').status_code,409)
        a=self.client.post(url,data=json.dumps({'exam_id':exam.id,'accept_pending_assessment':True}),content_type='application/json').json()
        essay='A considered response. '*200
        data=self.client.post(f"/api/attempts/{a['id']}/submit/",data=json.dumps({'answers':{'1':essay}}),content_type='application/json').json()
        self.assertEqual(data['state'],'awaiting_assessment');self.assertIsNone(data['result']);self.assertEqual(data['answers']['1'],essay)
    def test_expired_get_finalizes_saved_answers(self):
        a=self.start().json();Attempt.objects.filter(pk=a['id']).update(answers={'1':'TRUE'},deadline=timezone.now()-timedelta(seconds=1))
        data=self.client.get(f"/api/attempts/{a['id']}/").json()
        self.assertEqual(data['state'],'graded');self.assertEqual(data['result']['correct'],1)
    def test_review_positions_and_profile_validation(self):
        a=self.start().json();url=f"/api/attempts/{a['id']}/"
        self.assertEqual(self.client.patch(url,data=json.dumps({'review_positions':[999]}),content_type='application/json').status_code,400)
        data=self.client.patch(url,data=json.dumps({'review_positions':[1]}),content_type='application/json').json()
        self.assertEqual(data['review_positions'],[1])
        self.assertEqual(self.client.patch('/api/profile/',data=json.dumps({'target_band':7.3}),content_type='application/json').status_code,400)
        self.assertEqual(self.client.patch('/api/profile/',data=json.dumps({'target_band':7.5,'language':'en'}),content_type='application/json').json()['user']['target_band'],7.5)
    def test_invalid_content_does_not_consume_free_attempt(self):
        self.exam.passage='';self.exam.save()
        self.assertEqual(self.start().status_code,409)
        self.assertFalse(Profile.objects.get(user=self.user).free_attempt_used)
    def test_evidence_plan_uses_only_actual_mistakes(self):
        a=self.start().json()
        result=self.client.post(f"/api/attempts/{a['id']}/submit/",data=json.dumps({'answers':{'1':'FALSE'}}),content_type='application/json').json()['result']
        self.assertEqual(result['weekly_plan'][0]['question_positions'],[1])
        self.assertEqual(result['weekly_plan'][0]['wrong'],1)
