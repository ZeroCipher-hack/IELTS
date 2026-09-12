import hashlib,json
from datetime import timedelta
from functools import wraps
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction,IntegrityError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from .models import Exam,Attempt,Profile,Entitlement,LoginThrottle
from .services import finish_attempt,validate_exam

def error(message,status=400): return JsonResponse({'error':message},status=status)
def body(request):
    try: data=json.loads(request.body or b'{}')
    except (ValueError,UnicodeDecodeError): raise ValueError('JSON noto‘g‘ri.')
    if not isinstance(data,dict): raise ValueError('JSON obyekt bo‘lishi kerak.')
    return data

def endpoint(methods,auth=True):
    def decorate(fn):
        @require_http_methods(methods)
        @wraps(fn)
        def wrap(request,*args,**kwargs):
            if auth and not request.user.is_authenticated:return error('Hisobga kiring.',401)
            try:return fn(request,*args,**kwargs)
            except ValueError as exc:return error(str(exc))
        return wrap
    return decorate

def throttle(key):
    key=hashlib.sha256(key.encode()).hexdigest()
    now=timezone.now()
    with transaction.atomic():
        obj,_=LoginThrottle.objects.select_for_update().get_or_create(key=key,defaults={'reset_at':now+timedelta(minutes=5)})
        if obj.reset_at<=now:obj.count=0;obj.reset_at=now+timedelta(minutes=5)
        obj.count+=1;obj.save()
        return obj.count>10

def person(user):
    profile,_=Profile.objects.get_or_create(user=user)
    return {'id':user.id,'name':user.first_name or user.username,'email':user.email,'is_staff':user.is_staff,'target_band':float(profile.target_band),'language':profile.language}
@endpoint(['GET'],False)
def health(request):return JsonResponse({'status':'ok','ai_configured':False,'payments_configured':False,'phone_verification_configured':False})
@ensure_csrf_cookie
@endpoint(['GET'],False)
def session(request):return JsonResponse({'user':person(request.user) if request.user.is_authenticated else None})
@endpoint(['POST'],False)
def register(request):
    d=body(request);email=str(d.get('email','')).strip().lower();password=d.get('password','');name=str(d.get('name','')).strip()[:80]
    if throttle('register:'+request.META.get('REMOTE_ADDR','unknown')):return error('Ko‘p urinish. 5 daqiqadan keyin qaytaring.',429)
    from django.core.validators import validate_email
    try:validate_email(email);validate_password(password)
    except (ValidationError,TypeError):return error('Email va kamida 10 belgili kuchli parol kiriting.')
    if len(email)>150:return error('Email juda uzun.')
    try:
        with transaction.atomic():
            user=get_user_model().objects.create_user(username=email,email=email,password=password,first_name=name)
            Profile.objects.create(user=user)
    except IntegrityError:return error('Bu email bilan hisob mavjud.',409)
    login(request,user);return JsonResponse({'user':person(user)},status=201)
@endpoint(['POST'],False)
def sign_in(request):
    d=body(request);email=str(d.get('email','')).strip().lower()
    if throttle('login:'+email) or throttle('ip:'+request.META.get('REMOTE_ADDR','unknown')):return error('Ko‘p urinish. 5 daqiqadan keyin qaytaring.',429)
    user=authenticate(request,username=email,password=d.get('password',''))
    if user is None:return error('Email yoki parol noto‘g‘ri.',401)
    login(request,user);return JsonResponse({'user':person(user)})
@endpoint(['POST'])
def sign_out(request):logout(request);return JsonResponse({'ok':True})
def public_exam(exam):return {'id':exam.id,'title':exam.title,'section':exam.section,'version':exam.version,'duration_seconds':exam.duration_seconds,'question_count':exam.questions.count()}
@endpoint(['GET'])
def catalog(request):
    profile,_=Profile.objects.get_or_create(user=request.user)
    return JsonResponse({'exams':[public_exam(e) for e in Exam.objects.filter(published=True).prefetch_related('questions')],'free_attempt_available':not profile.free_attempt_used,'payment_enabled':False})
def payload(a,include_questions=True):
    snap=a.snapshot
    data={'id':str(a.id),'title':snap['title'],'section':snap['section'],'state':a.state,'deadline':a.deadline.isoformat(),'started_at':a.started_at.isoformat(),'answers':a.answers,'review_positions':a.review_positions,'result':a.result,'server_time':timezone.now().isoformat()}
    if include_questions:
        data.update({'passage':snap['passage'],'audio_url':snap.get('audio_url',''),'questions':[{k:v for k,v in q.items() if k not in ['accepted_answers','evidence','explanation']} for q in snap['questions']]})
    return data
@endpoint(['GET','POST'])
def attempts(request):
    if request.method=='GET':
        with transaction.atomic():
            for expired in Attempt.objects.select_for_update().filter(user=request.user,state='in_progress',deadline__lte=timezone.now()):finish_attempt(expired)
        return JsonResponse({'attempts':[payload(a,False) for a in Attempt.objects.filter(user=request.user)[:100]]})
    d=body(request)
    try: exam_id=int(d.get('exam_id'))
    except (TypeError,ValueError):return error('Test tanlang.')
    with transaction.atomic():
        # User-row lock serializes free claim and entitlement consumption in PostgreSQL.
        get_user_model().objects.select_for_update().get(pk=request.user.pk)
        exam=Exam.objects.filter(pk=exam_id,published=True).first()
        if not exam:return error('Test topilmadi.',404)
        if exam.section=='Speaking':return error('Ovozli suhbat xizmati hali ulanmagan.',503)
        existing=Attempt.objects.filter(user=request.user,exam=exam,state='in_progress').first()
        if existing:
            if existing.deadline<=timezone.now():finish_attempt(existing)
            return JsonResponse(payload(existing))
        try:validate_exam(exam)
        except ValidationError as exc:return error(' '.join(exc.messages),409)
        qs=list(exam.questions.values('position','prompt','choices','accepted_answers','evidence','explanation','skill_tag'))
        if exam.section=='Writing' and d.get('accept_pending_assessment') is not True:return error('Writing bahosi AI ulanmaguncha kutilishini tasdiqlang.',409)
        profile,_=Profile.objects.get_or_create(user=request.user)
        if not profile.free_attempt_used:profile.free_attempt_used=True;profile.save()
        else:
            entitlement=Entitlement.objects.select_for_update().filter(user=request.user,exam=exam,consumed=False).first()
            if not entitlement:return error('Bepul urinish ishlatilgan. To‘lov hali ulanmagan; administrator kirish huquqi bera oladi.',402)
            entitlement.consumed=True;entitlement.save()
        snapshot={'title':exam.title,'section':exam.section,'version':exam.version,'passage':exam.passage,'audio_url':exam.audio_url,'questions':qs}
        a=Attempt.objects.create(user=request.user,exam=exam,snapshot=snapshot,deadline=timezone.now()+timedelta(seconds=exam.duration_seconds))
    return JsonResponse(payload(a),status=201)
def clean_answers(d,snapshot):
    values=d.get('answers')
    if not isinstance(values,dict):raise ValueError('Javoblar obyekt bo‘lishi kerak.')
    allowed={str(q['position']) for q in snapshot['questions']}
    if any(k not in allowed or not isinstance(v,str) or len(v)>(30000 if snapshot['section']=='Writing' else 500) for k,v in values.items()):raise ValueError('Javob formati noto‘g‘ri.')
    return values
@endpoint(['GET','PATCH'])
def attempt(request,pk):
    with transaction.atomic():
        a=Attempt.objects.select_for_update().filter(pk=pk,user=request.user).first()
        if not a:return error('Urinish topilmadi.',404)
        if request.method=='PATCH':
            if a.state!='in_progress':return error('Imtihon yakunlangan.',409)
            if timezone.now()>=a.deadline:return error('Vaqt tugagan. Saqlangan javoblarni topshiring.',409)
            d=body(request)
            if 'answers' in d:a.answers.update(clean_answers(d,a.snapshot))
            if 'review_positions' in d:
                positions=d['review_positions'];allowed={q['position'] for q in a.snapshot['questions']}
                if not isinstance(positions,list) or any(type(p) is not int or p not in allowed for p in positions):return error('Savol raqamlari noto‘g‘ri.')
                a.review_positions=sorted(set(positions))
            a.save(update_fields=['answers','review_positions'])
        elif a.state=='in_progress' and a.deadline<=timezone.now():finish_attempt(a)
        return JsonResponse(payload(a))
def normal(value):return ' '.join(value.strip().casefold().split())
@endpoint(['POST'])
def submit(request,pk):
    with transaction.atomic():
        a=Attempt.objects.select_for_update().filter(pk=pk,user=request.user).first()
        if not a:return error('Urinish topilmadi.',404)
        if a.state!='in_progress':return JsonResponse(payload(a))
        d=body(request)
        if 'answers' in d and timezone.now()<a.deadline:a.answers.update(clean_answers(d,a.snapshot))
        finish_attempt(a)
        return JsonResponse(payload(a))

@endpoint(['PATCH'])
def profile(request):
    from decimal import Decimal, InvalidOperation
    d=body(request)
    with transaction.atomic():
        p,_=Profile.objects.select_for_update().get_or_create(user=request.user)
        if 'target_band' in d:
            try: target=Decimal(str(d['target_band']))
            except InvalidOperation:return error('Maqsad bandi noto‘g‘ri.')
            if not target.is_finite() or not 1<=target<=9 or target*2!=int(target*2):return error('Maqsad 1–9 oralig‘ida, 0.5 qadam bilan bo‘lsin.')
            p.target_band=target
        if 'language' in d:
            if d['language'] not in ('uz','en','ru'):return error('Til noto‘g‘ri.')
            p.language=d['language']
        if 'name' in d:
            if not isinstance(d['name'],str) or not d['name'].strip() or len(d['name'])>80:return error('Ism 1–80 belgi bo‘lsin.')
            request.user.first_name=d['name'].strip();request.user.save(update_fields=['first_name'])
        p.save()
    return JsonResponse({'user':person(request.user)})
