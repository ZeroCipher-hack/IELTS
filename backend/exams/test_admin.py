from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model
from .models import Exam, Question
from .admin import AnswerLinesField, QuestionForm


class QuestionEditorTests(SimpleTestCase):
    def test_lines_preserve_answer_strings(self):
        field = AnswerLinesField(required=False)
        self.assertEqual(field.clean(" TRUE \nFALSE\n\nNOT GIVEN "), ["TRUE", "FALSE", "NOT GIVEN"])
        self.assertEqual(field.prepare_value(["library", "the library"]), "library\nthe library")
        self.assertEqual(field.clean(""), [])

    def test_existing_json_answers_are_editable_as_lines(self):
        form = QuestionForm(initial={"accepted_answers": ["library", "the library"]})
        self.assertEqual(form["accepted_answers"].value(), "library\nthe library")


class ReadingAdminTests(TestCase):
    def test_reading_editor_renders_and_saves_lines_as_answer_lists(self):
        staff = get_user_model().objects.create_superuser('editor', 'editor@example.com', 'test-password')
        self.client.force_login(staff)
        response = self.client.get('/admin/exams/exam/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'exams/admin.css')
        response = self.client.post('/admin/exams/exam/add/', {
            'title': 'Reading editor test', 'section': 'Reading', 'version': '1',
            'duration_seconds': '3600', 'passage': 'The library opens on Monday.',
            'questions-TOTAL_FORMS': '1', 'questions-INITIAL_FORMS': '0',
            'questions-MIN_NUM_FORMS': '0', 'questions-MAX_NUM_FORMS': '1000',
            'questions-0-position': '1', 'questions-0-prompt': 'When does the library open?',
            'questions-0-choices': 'Monday\nTuesday', 'questions-0-accepted_answers': 'Monday',
            'questions-0-evidence': 'The library opens on Monday.',
            'questions-0-explanation': 'Find the opening day in the passage.',
            'questions-0-skill_tag': 'multiple_choice', '_save': 'Save',
        })
        self.assertEqual(response.status_code, 302)
        exam = Exam.objects.get(title='Reading editor test')
        self.assertFalse(exam.published)
        question = Question.objects.get(exam=exam)
        self.assertEqual(question.choices, ['Monday', 'Tuesday'])
        self.assertEqual(question.accepted_answers, ['Monday'])

class WritingEditorTests(TestCase):
    def test_saved_writing_draft_has_task_editor_without_answer_keys(self):
        user=get_user_model().objects.create_superuser('writer','writer@example.com','test-password')
        self.client.force_login(user)
        exam=Exam.objects.create(title='Writing draft',section='Writing',duration_seconds=3600)
        Question.objects.create(exam=exam,position=1,prompt='Summarise the table.')
        response=self.client.get(f'/admin/exams/exam/{exam.pk}/change/')
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'questions-0-prompt')
        self.assertNotContains(response,'questions-0-accepted_answers')
        self.assertNotContains(response,'id_audio_file')

    def test_writing_positions_are_task_numbers(self):
        from django.core.exceptions import ValidationError
        from .services import validate_exam
        exam=Exam.objects.create(title='Writing draft',section='Writing',duration_seconds=3600)
        question=Question.objects.create(exam=exam,position=3,prompt='Discuss transport.')
        with self.assertRaises(ValidationError):validate_exam(exam)
        question.position=2;question.save()
        validate_exam(exam)

class AssessmentRetryTests(TestCase):
    def test_retry_preserves_objective_score_and_skips_missing_speaking_audio(self):
        from unittest.mock import patch
        from django.contrib import admin
        from django.contrib.auth import get_user_model
        from django.test import RequestFactory
        from django.utils import timezone
        from .admin import AssessmentJobAdmin
        from .models import Attempt,AssessmentJob
        user=get_user_model().objects.create_user('retry@example.com')
        exam=Exam.objects.create(title='Retry',section='Reading')
        result={'correct':1,'total':2,'rows':[{'position':1,'correct':True}]}
        reading=Attempt.objects.create(user=user,exam=exam,state='graded',snapshot={'section':'Reading'},result=result,deadline=timezone.now())
        speaking=Attempt.objects.create(user=user,exam=exam,state='awaiting_assessment',snapshot={'section':'Speaking'},deadline=timezone.now())
        objective=AssessmentJob.objects.create(attempt=reading,state='failed',tries=3,error_code='AI_RATE_LIMIT')
        missing=AssessmentJob.objects.create(attempt=speaking,state='failed',tries=3)
        editor=AssessmentJobAdmin(AssessmentJob,admin.site)
        with patch.object(editor,'message_user'):
            editor.retry_failed(RequestFactory().post('/admin/'),AssessmentJob.objects.all())
        objective.refresh_from_db();missing.refresh_from_db();reading.refresh_from_db()
        self.assertEqual(objective.state,'pending');self.assertEqual(objective.tries,0)
        self.assertEqual(missing.state,'failed');self.assertEqual(missing.tries,3)
        self.assertEqual(reading.state,'graded');self.assertEqual(reading.result,result)
