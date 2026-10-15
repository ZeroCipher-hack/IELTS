"""Full IELTS Academic sitting: four sections, in order, one result page.

What this does NOT do is as important as what it does. A section is reported
with a band only where a band can honestly be derived -- a standard-length
Listening or Reading paper, or an AI assessment for Writing and Speaking. A
short practice set reports its raw score and nothing more, and the overall
band appears only when all four sections carry one.
"""
from django.utils import timezone

from .bands import overall, raw_band
from .models import Attempt, Exam, ExamSession

ORDER = ExamSession.ORDER
TERMINAL = ('graded', 'awaiting_assessment', 'expired')


def build_plan():
    """The newest published exam for each section, in exam order.

    Returns (plan, missing). A sitting is only offered when all four exist:
    half an exam is not an IELTS exam.
    """
    plan, missing = [], []
    for section in ORDER:
        exam = Exam.objects.filter(published=True, section=section).order_by('-id').first()
        if exam is None:
            missing.append(section)
            continue
        plan.append({'section': section, 'exam_id': exam.id, 'title': exam.title,
                     'duration_seconds': exam.duration_seconds,
                     'question_count': exam.questions.count()})
    return plan, missing


def section_band(attempt):
    """The band for one finished attempt, or None when none can be claimed."""
    result = attempt.result or {}
    assessed = result.get('assessment') or {}
    if isinstance(assessed.get('band'), (int, float)):
        return float(assessed['band']), 'ai_estimate'
    if isinstance(result.get('band'), (int, float)):
        return float(result['band']), 'table'
    band = raw_band(attempt.snapshot.get('section'), result.get('correct'), result.get('total'))
    if band is not None:
        return band, 'table'
    return None, 'none'


def stages(session):
    """Per-section progress, read from the attempts rather than stored twice."""
    by_order = {a.session_order: a for a in session.attempts.all()}
    rows = []
    for index, entry in enumerate(session.plan):
        attempt = by_order.get(index)
        row = {**entry, 'order': index, 'attempt_id': '', 'state': 'not_started',
               'band': None, 'band_source': 'none', 'correct': None, 'total': None}
        if attempt:
            band, source = section_band(attempt)
            result = attempt.result or {}
            row.update({'attempt_id': str(attempt.id), 'state': attempt.state,
                        'band': band, 'band_source': source,
                        'correct': result.get('correct'), 'total': result.get('total')})
        rows.append(row)
    return rows


def current_index(rows):
    """The first section not yet finished, or len(rows) when all are done."""
    for row in rows:
        if row['state'] not in TERMINAL:
            return row['order']
    return len(rows)


def report(session):
    rows = stages(session)
    bands = {row['section']: row['band'] for row in rows}
    total = overall(bands)
    awaiting = [r['section'] for r in rows if r['state'] == 'awaiting_assessment']
    no_band = [r['section'] for r in rows if r['state'] == 'graded' and r['band'] is None]
    return {
        'id': str(session.id), 'state': session.state,
        'started_at': session.started_at.isoformat(),
        'completed_at': session.completed_at.isoformat() if session.completed_at else '',
        'stages': rows, 'current': current_index(rows), 'overall_band': total,
        'awaiting_assessment': awaiting, 'sections_without_band': no_band,
        'estimated': True,
        'note': ('AI va jadval asosidagi taxminiy natija. Rasmiy IELTS bandi emas.'
                 if total is not None else ''),
    }


def refresh(session):
    """Close the sitting once every section has reached a terminal state."""
    rows = stages(session)
    done = all(row['state'] in TERMINAL for row in rows) and len(rows) == len(ORDER)
    if done and session.state == 'in_progress':
        session.state = 'completed'
        session.completed_at = timezone.now()
        session.save(update_fields=['state', 'completed_at'])
    return session


def attach(session, attempt, section):
    """Link a new attempt to its slot. Returns False when the slot is wrong."""
    for index, entry in enumerate(session.plan):
        if entry['section'] == section and entry['exam_id'] == attempt.exam_id:
            if Attempt.objects.filter(session=session, session_order=index).exclude(pk=attempt.pk).exists():
                return False
            attempt.session = session
            attempt.session_order = index
            attempt.save(update_fields=['session', 'session_order'])
            return True
    return False
