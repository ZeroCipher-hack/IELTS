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
