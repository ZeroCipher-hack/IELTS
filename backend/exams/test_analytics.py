from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Exam,Attempt

class AnalyticsTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('analytics@example.com',password='Strong-Test-123!')
        self.other=get_user_model().objects.create_user('private@example.com',password='Strong-Test-123!')
        self.exam=Exam.objects.create(title='Reading A',section='Reading')
        self.client.force_login(self.user)
    def add(self,user=None,result=None,**snapshot):
        snap={'section':'Reading','title':'Reading A','version':1,'questions':[],'passage':'Text','audio_url':''};snap.update(snapshot)
        return Attempt.objects.create(user=user or self.user,exam=self.exam,snapshot=snap,state='graded',deadline=timezone.now(),result=result or {'correct':3,'total':5},submitted_at=timezone.now())
    def modules(self):return self.client.get('/api/analytics/').json()['modules']
    def test_private_and_only_graded(self):
        self.add();self.add(user=self.other)
        a=self.add();a.state='awaiting_assessment';a.save()
        data=self.modules();self.assertEqual([m['section'] for m in data],['Listening','Reading','Writing','Speaking'])
        self.assertEqual(len(data[1]['series'][0]['points']),1)
        self.client.logout();self.assertEqual(self.client.get('/api/analytics/').status_code,401)
    def test_changed_raw_test_is_not_connected(self):
        self.add();self.add(result={'correct':4,'total':5});self.add(version=2)
        series=self.modules()[1]['series'];self.assertEqual(sorted(len(s['points']) for s in series),[1,2])
        self.assertTrue(all(s['metric']=='raw' for s in series))
    def test_ai_model_and_scope_are_separate(self):
        for model,scope in [('model-a','writing_section'),('model-a','writing_section'),('model-b','writing_section'),('model-a','submitted_tasks_only')]:
            self.add(section='Writing',result={'assessment':{'band':6.5,'model':model,'scope':scope,'rubric_version':'v1','tasks':[{'position':1},{'position':2}]}})
        series=self.modules()[2]['series'];self.assertEqual(sorted(len(s['points']) for s in series),[1,1,2]);self.assertTrue(all(s['maximum']==9 for s in series))
    def test_zero_score_is_included_and_invalid_score_excluded(self):
        self.add(result={'correct':0,'total':5});self.add(result={'correct':8,'total':5});self.add(result={'correct':True,'total':5})
        points=self.modules()[1]['series'][0]['points'];self.assertEqual(len(points),1);self.assertEqual(points[0]['value'],0)
