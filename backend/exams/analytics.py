"""Own-account score series. Keep incompatible tests and AI rubrics separate."""
import hashlib
import json
import math
from .models import Attempt

SECTIONS = ('Listening', 'Reading', 'Writing', 'Speaking')

def number(value):
    return type(value) in (int, float) and math.isfinite(value)

def student_analytics(user):
    modules = {name: {'section': name, 'series': []} for name in SECTIONS}
    grouped = {}
    attempts = list(Attempt.objects.filter(user=user, state='graded').exclude(result=None).order_by('-started_at', '-id')[:100])
    for attempt in reversed(attempts):
        snap, result = attempt.snapshot, attempt.result
        section = snap.get('section')
        if section not in modules or not isinstance(result, dict):
            continue
        assessment = result.get('assessment')
        if isinstance(assessment, dict):
            value = assessment.get('band')
            if not number(value) or not 0 <= value <= 9:
                continue
            metric, maximum = 'ai_band', 9
            # Do not connect task-only and full-section estimates or changed models/rubrics.
            scope = assessment.get('scope', 'unknown')
            model = assessment.get('model', 'unknown')
            rubric = assessment.get('rubric_version', 'unknown')
            positions = sorted(str(t.get('position')) for t in assessment.get('tasks', []) if isinstance(t, dict))
            identity = [section, metric, scope, model, rubric, positions]
            if 'unknown' in (scope, model, rubric):
                identity.append(str(attempt.id))
            label = {'scope': scope, 'model': model, 'rubric': rubric}
        else:
            value, maximum = result.get('correct'), result.get('total')
            if not number(value) or not number(maximum) or maximum <= 0 or not 0 <= value <= maximum:
                continue
            metric = 'raw'
            content = {k: snap.get(k) for k in ('section', 'version', 'passage', 'audio_url', 'questions')}
            identity = [section, metric, attempt.exam_id, content, maximum]
            label = {'title': snap.get('title', ''), 'version': snap.get('version', 1)}
        key = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]
        if key not in grouped:
            series = {'id': key, 'metric': metric, 'maximum': maximum, **label, 'points': []}
            grouped[key] = series
            modules[section]['series'].append(series)
        grouped[key]['points'].append({'id': str(attempt.id), 'date': (attempt.submitted_at or attempt.started_at).isoformat(), 'value': value, 'title': snap.get('title', '')})
    for module in modules.values():
        for series in module['series']:
            series['points'].sort(key=lambda p: (p['date'], p['id']))
        module['series'].sort(key=lambda s: s['points'][-1]['date'])
    return {'limit': 100, 'modules': list(modules.values())}
