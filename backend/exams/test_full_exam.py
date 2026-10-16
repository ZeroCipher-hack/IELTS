"""A full IELTS Academic sitting: four sections in order, one honest report."""
import json

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from .models import Attempt, Exam, ExamSession, Profile, Question
from .sessions import build_plan, report


def exam(section, questions=2, published=True, title=None, **kwargs):
    e = Exam.objects.create(title=title or f'{section} paper', section=section,
                            duration_seconds=900,
                            passage='Transcript text.' if section in ('Reading', 'Listening') else 'Guidance.',
                            **kwargs)
    for i in range(1, questions + 1):
        Question.objects.create(
            exam=e, position=i, part=(1 if section == 'Speaking' and i == 1 else
                                      2 if section == 'Speaking' and i == 2 else
                                      3 if section == 'Speaking' else 0),
            prompt=f'Question {i}',
            choices=['A point'] if section == 'Speaking' and i == 2 else [],
            accepted_answers=[] if section in ('Writing', 'Speaking') else ['yes'])
    e.published = published
    e.save()
    return e


def full_catalogue():
    exam('Listening', audio_url='https://example.com/a.mp3')
    exam('Reading')
    exam('Writing')
    exam('Speaking', questions=3)


@override_settings(EXAMS_OPEN_ACCESS=True)
class PlanTests(TestCase):
    def test_a_sitting_needs_all_four_sections(self):
        exam('Reading')
        plan, missing = build_plan()
        self.assertEqual(missing, ['Listening', 'Writing', 'Speaking'])

    def test_the_plan_is_in_exam_order_not_creation_order(self):
        exam('Speaking', questions=3)
        exam('Writing')
        exam('Reading')
        exam('Listening', audio_url='https://example.com/a.mp3')
        plan, missing = build_plan()
        self.assertEqual(missing, [])
        self.assertEqual([p['section'] for p in plan], ['Listening', 'Reading', 'Writing', 'Speaking'])

    def test_the_newest_published_paper_wins(self):
        exam('Reading', title='old')
        newer = exam('Reading', title='new')
        exam('Listening', audio_url='https://example.com/a.mp3')
        exam('Writing')
        exam('Speaking', questions=3)
        plan, _ = build_plan()
        self.assertEqual(next(p for p in plan if p['section'] == 'Reading')['exam_id'], newer.id)

    def test_a_draft_is_not_eligible(self):
        exam('Reading', published=False)
        _, missing = build_plan()
        self.assertIn('Reading', missing)


@override_settings(EXAMS_OPEN_ACCESS=True)
class SittingFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('c@example.com', password='Strong-Test-123!')
        Profile.objects.create(user=self.user)
        self.client.force_login(self.user)
        full_catalogue()

    def create(self):
        return self.client.post('/api/sessions/', data='{}', content_type='application/json')

    def start(self, exam_id, session_id):
        return self.client.post('/api/attempts/', content_type='application/json',
                                data=json.dumps({'exam_id': exam_id, 'session_id': session_id,
                                                 'accept_pending_assessment': True}))

    def test_a_sitting_opens_with_four_sections_and_nothing_started(self):
        response = self.create()
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertEqual([s['section'] for s in data['stages']], ExamSession.ORDER)
        self.assertEqual(data['current'], 0)
        self.assertIsNone(data['overall_band'])
        self.assertTrue(all(s['state'] == 'not_started' for s in data['stages']))

    def test_a_missing_section_blocks_the_sitting_with_a_named_reason(self):
        Exam.objects.filter(section='Speaking').update(published=False)
        response = self.create()
        self.assertEqual(response.status_code, 409)
        self.assertIn('Speaking', response.json()['error'])

    def test_a_second_request_returns_the_running_sitting(self):
        first = self.create().json()
        again = self.create()
        self.assertEqual(again.status_code, 200)
        self.assertEqual(again.json()['id'], first['id'])
        self.assertEqual(ExamSession.objects.count(), 1)

    def test_sections_must_be_taken_in_order(self):
        data = self.create().json()
        reading = data['stages'][1]['exam_id']
        skipped = self.start(reading, data['id'])
        self.assertEqual(skipped.status_code, 409)
        self.assertIn('ketma-ket', skipped.json()['error'])

    def test_finishing_a_section_advances_the_sitting(self):
        data = self.create().json()
        attempt_id = self.start(data['stages'][0]['exam_id'], data['id']).json()['id']
        self.client.post(f'/api/attempts/{attempt_id}/submit/', data='{"answers": {}}',
                         content_type='application/json')
        after = self.client.get(f'/api/sessions/{data["id"]}/').json()
        self.assertEqual(after['stages'][0]['state'], 'graded')
        self.assertEqual(after['current'], 1)

    def test_an_attempt_knows_which_sitting_it_belongs_to(self):
        data = self.create().json()
        started = self.start(data['stages'][0]['exam_id'], data['id']).json()
        self.assertEqual(started['session_id'], data['id'])

    def test_an_ordinary_attempt_belongs_to_no_sitting(self):
        listening = Exam.objects.get(section='Listening')
        started = self.client.post('/api/attempts/', content_type='application/json',
                                   data=json.dumps({'exam_id': listening.id})).json()
        self.assertEqual(started['session_id'], '')

    def test_another_users_sitting_cannot_be_joined_or_read(self):
        data = self.create().json()
        intruder = get_user_model().objects.create_user('i@example.com', password='Strong-Test-123!')
        Profile.objects.create(user=intruder)
        self.client.force_login(intruder)
        self.assertEqual(self.client.get(f'/api/sessions/{data["id"]}/').status_code, 404)
        self.assertEqual(self.start(data['stages'][0]['exam_id'], data['id']).status_code, 404)
        self.assertFalse(Attempt.objects.filter(session_id=data['id']).exists())

    def test_abandoning_a_sitting_frees_the_candidate_to_start_another(self):
        first = self.create().json()
        self.client.delete(f'/api/sessions/{first["id"]}/')
        second = self.create()
        self.assertEqual(second.status_code, 201)
        self.assertNotEqual(second.json()['id'], first['id'])

    def test_a_completed_sitting_reports_when_assessment_is_still_pending(self):
        data = self.create().json()
        for stage in data['stages']:
            attempt_id = self.start(stage['exam_id'], data['id']).json()['id']
            if stage['section'] == 'Speaking':
                Attempt.objects.filter(pk=attempt_id).update(state='awaiting_assessment')
            else:
                self.client.post(f'/api/attempts/{attempt_id}/submit/', data='{"answers": {}}',
                                 content_type='application/json')
        final = self.client.get(f'/api/sessions/{data["id"]}/').json()
        self.assertEqual(final['state'], 'completed')
        self.assertIn('Writing', final['awaiting_assessment'])
        self.assertIn('Speaking', final['awaiting_assessment'])
        self.assertIsNone(final['overall_band'])


class ReportHonestyTests(TestCase):
    """The report must never invent a band it cannot derive."""

    def setUp(self):
        self.user = get_user_model().objects.create_user('r@example.com', password='Strong-Test-123!')
        Profile.objects.create(user=self.user)
        full_catalogue()
        plan, _ = build_plan()
        self.session = ExamSession.objects.create(user=self.user, plan=plan)

    def finish(self, order, section, result, state='graded'):
        paper = Exam.objects.get(section=section)
        return Attempt.objects.create(
            user=self.user, exam=paper, session=self.session, session_order=order, state=state,
            snapshot={'title': paper.title, 'section': section, 'version': 1, 'passage': '',
                      'questions': []},
            deadline=self.session.started_at, result=result)

    def test_a_short_paper_reports_a_raw_score_and_no_band(self):
        self.finish(0, 'Listening', {'correct': 5, 'total': 6, 'band': None})
        stage = report(self.session)['stages'][0]
        self.assertIsNone(stage['band'])
        self.assertEqual((stage['correct'], stage['total']), (5, 6))
        self.assertIn('Listening', report(self.session)['sections_without_band'])

    def test_a_standard_paper_converts_to_a_band(self):
        self.finish(1, 'Reading', {'correct': 30, 'total': 40, 'band': None})
        stage = report(self.session)['stages'][1]
        self.assertEqual(stage['band'], 7.0)
        self.assertEqual(stage['band_source'], 'table')

    def test_an_ai_assessment_supplies_the_writing_band(self):
        self.finish(2, 'Writing', {'correct': 0, 'total': 0, 'assessment': {'band': 6.5}})
        stage = report(self.session)['stages'][2]
        self.assertEqual(stage['band'], 6.5)
        self.assertEqual(stage['band_source'], 'ai_estimate')

    def test_an_overall_band_appears_only_with_all_four(self):
        self.finish(0, 'Listening', {'correct': 30, 'total': 40})
        self.finish(1, 'Reading', {'correct': 30, 'total': 40})
        self.finish(2, 'Writing', {'assessment': {'band': 6.5}})
        self.assertIsNone(report(self.session)['overall_band'])
        self.finish(3, 'Speaking', {'assessment': {'band': 6.5}})
        data = report(self.session)
        self.assertEqual(data['overall_band'], 7.0)   # (7+7+6.5+6.5)/4 = 6.75 -> 7.0
        self.assertTrue(data['estimated'])
        self.assertIn('Rasmiy IELTS bandi emas', data['note'])

    def test_one_unbandable_section_withholds_the_overall(self):
        self.finish(0, 'Listening', {'correct': 5, 'total': 6})
        self.finish(1, 'Reading', {'correct': 30, 'total': 40})
        self.finish(2, 'Writing', {'assessment': {'band': 6.5}})
        self.finish(3, 'Speaking', {'assessment': {'band': 6.5}})
        data = report(self.session)
        self.assertIsNone(data['overall_band'], 'three bands and a raw score is not an overall band')
        self.assertEqual(data['sections_without_band'], ['Listening'])
