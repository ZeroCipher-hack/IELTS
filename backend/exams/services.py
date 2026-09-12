"""Provider-independent exam validation, submission and evidence-based feedback."""
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_exam(exam):
    errors=[]
    questions=list(exam.questions.all())
    if not exam.title.strip(): errors.append('Test nomi kerak.')
    if not 60 <= exam.duration_seconds <= 14400: errors.append('Davomiylik 60–14400 soniya bo‘lsin.')
    if not questions: errors.append('Kamida bitta topshiriq kiriting.')
    if exam.section=='Reading' and not exam.passage.strip(): errors.append('Reading matni kerak.')
    if exam.section=='Listening' and not exam.audio_url.startswith('https://'): errors.append('Listening uchun HTTPS audio havolasi kerak.')
    if exam.section=='Writing' and len(questions)>2: errors.append('Writing uchun ko‘pi bilan ikkita topshiriq kiriting.')
    for q in questions:
        if not q.prompt.strip(): errors.append(f'{q.position}: savol matni kerak.')
        if not isinstance(q.choices,list) or any(not isinstance(c,str) or not c.strip() for c in q.choices):
            errors.append(f'{q.position}: variantlar matnlar ro‘yxati bo‘lsin.')
        if not isinstance(q.accepted_answers,list) or any(not isinstance(c,str) or not c.strip() for c in q.accepted_answers):
            errors.append(f'{q.position}: javob kaliti matnlar ro‘yxati bo‘lsin.')
        elif exam.section in ('Reading','Listening'):
            if not q.accepted_answers: errors.append(f'{q.position}: javob kaliti kerak.')
            elif q.choices and any(a not in q.choices for a in q.accepted_answers): errors.append(f'{q.position}: kalit variantlarga mos emas.')
    if errors: raise ValidationError(errors)


def normal(value): return ' '.join(value.strip().casefold().split())


def finish_attempt(a):
    """Call under an attempt row lock. Repeated delivery is safe."""
    if a.state!='in_progress': return a
    a.submitted_at=timezone.now()
    if a.snapshot['section'] in ('Writing','Speaking'):
        a.state='awaiting_assessment'
        a.result=None
    else:
        rows=[];tags={}
        for q in a.snapshot['questions']:
            answer=a.answers.get(str(q['position']),'')
            correct=normal(answer) in [normal(str(v)) for v in q['accepted_answers']]
            rows.append({'position':q['position'],'prompt':q['prompt'],'answer':answer,'correct':correct,
                         'accepted_answers':q['accepted_answers'],'evidence':q['evidence'],'explanation':q['explanation'],'skill_tag':q['skill_tag']})
            bucket=tags.setdefault(q['skill_tag'] or 'General',{'correct':0,'total':0})
            bucket['total']+=1;bucket['correct']+=int(correct)
        weak=sorted(({'tag':tag,**v,'wrong':v['total']-v['correct']} for tag,v in tags.items() if v['correct']<v['total']),key=lambda v:-v['wrong'])
        plan=[]
        for index,item in enumerate(weak[:7]):
            plan.append({'day':index+1,'tag':item['tag'],'wrong':item['wrong'],'total':item['total'],
                         'question_positions':[r['position'] for r in rows if not r['correct'] and (r['skill_tag'] or 'General')==item['tag']],
                         'minutes':20,'action':'review_evidence_then_retry'})
        a.result={'correct':sum(r['correct'] for r in rows),'total':len(rows),'band':None,'rows':rows,'skills':tags,
                  'weekly_plan':plan,'note':'Raw score only. This test has no validated IELTS band mapping.'}
        a.state='graded'
    a.save(update_fields=['answers','state','submitted_at','result'])
    return a
