import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from .admin import SpeakingSetForm
from .models import SpeakingSet
from .voice import CUE, access, constraints, published_script


@override_settings(AI_ENABLED=True, GEMINI_API_KEY='test-key', VOICE_PRACTICE_ENABLED=True)
class SpeakingSetTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('speaker')
        self.client.force_login(self.user)

    def create_set(self, title='Community places', published=True):
        return SpeakingSet.objects.create(title=title,published=published,
            part1_questions=['What is your hometown like?', 'What do you enjoy about your studies?'],
            cue_title='Describe a library you have visited.',
            cue_points=['Where it is', 'When you visited', 'Why you remember it'],
            part3_questions=['Why are libraries important for communities?'])

    def test_status_ignores_drafts_and_uses_latest_published_set(self):
        self.assertEqual(access(self.user)['cue'],CUE)
        selected=self.create_set()
        self.create_set('Draft',published=False)
        state=access(self.user)
        self.assertEqual(state['set_id'],selected.pk)
        self.assertEqual(state['questions']['1'],selected.part1_questions)
        self.assertIn(selected.cue_title,constraints(2,state)['systemInstruction']['parts'][0]['text'])

    def test_tokens_keep_the_chosen_set_when_a_new_one_is_published(self):
        old=self.create_set('Old')
        new=self.create_set('New');new.cue_title='Describe a park you enjoy.';new.save()
        with patch('exams.gemini.post',return_value={'name':'test-token'}) as mocked:
            response=self.client.post('/api/voice/token/',data=json.dumps({'part':2,'set_id':old.pk}),content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['set_id'],old.pk)
        prompt=mocked.call_args.args[1]['bidiGenerateContentSetup']['systemInstruction']['parts'][0]['text']
        self.assertIn(old.cue_title,prompt)
        self.assertNotIn(new.cue_title,prompt)
        with patch('exams.gemini.post',return_value={'name':'builtin-token'}) as mocked:
            response=self.client.post('/api/voice/token/',data=json.dumps({'part':2,'set_id':None}),content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.assertIn(CUE['title'],mocked.call_args.args[1]['bidiGenerateContentSetup']['systemInstruction']['parts'][0]['text'])

    def test_draft_and_malformed_identifiers_never_call_provider(self):
        draft=self.create_set(published=False)
        for identifier in (draft.pk,True,'1',-1,9999):
            with patch('exams.gemini.post') as mocked:
                response=self.client.post('/api/voice/token/',data=json.dumps({'part':1,'set_id':identifier}),content_type='application/json')
            self.assertEqual(response.status_code,400)
            mocked.assert_not_called()

    def test_editor_lines_and_model_validation(self):
        form=SpeakingSetForm(data={'title':'Libraries','version':1,
            'part1_questions':'What do you study?\nWhere do you live?',
            'cue_title':'Describe a library.', 'cue_points':'Where\nWhen\nWhy',
            'part3_questions':'Why do people visit libraries?'})
        self.assertTrue(form.is_valid(),form.errors)
        self.assertEqual(form.cleaned_data['part1_questions'],['What do you study?','Where do you live?'])
        item=form.save(commit=False);item.cue_points=['Only one point']
        with self.assertRaises(ValidationError):item.full_clean()

    def test_published_set_is_readonly_in_admin(self):
        staff=get_user_model().objects.create_superuser('editor','editor@example.com','test-password')
        self.client.force_login(staff)
        item=self.create_set()
        response=self.client.get(f'/admin/exams/speakingset/{item.pk}/change/')
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response,'name="cue_title"')
        item.published=False;item.save()
        response=self.client.get(f'/admin/exams/speakingset/{item.pk}/change/')
        self.assertContains(response,'name="cue_title"')
