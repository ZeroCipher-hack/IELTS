import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

def validate_exam_audio(f):
    """Admin-facing guard. Keeps an unplayable or oversized upload out of the catalog."""
    allowed=settings.EXAM_AUDIO_EXTENSIONS
    name=getattr(f,'name','') or ''
    if '.' not in name or name.rsplit('.',1)[1].lower() not in allowed:
        raise ValidationError('Audio formati qo\u2018llab-quvvatlanmaydi. Ruxsat etilgan: '+', '.join(allowed)+'.')
    size=getattr(f,'size',0) or 0
    if size>settings.EXAM_AUDIO_MAX_BYTES:
        raise ValidationError(f'Audio hajmi {settings.EXAM_AUDIO_MAX_BYTES//(1024*1024)} MB dan oshmasligi kerak.')
class Exam(models.Model):
    title=models.CharField(max_length=180)
    section=models.CharField(max_length=16,choices=[(s,s) for s in ['Reading','Listening','Writing','Speaking']])
    version=models.PositiveIntegerField(default=1)
    published=models.BooleanField(default=False)
    duration_seconds=models.PositiveIntegerField(default=600)
    passage=models.TextField(blank=True)
    # Listening audio comes from EITHER an uploaded file or an external HTTPS link.
    # audio_file wins when both are set; audio_source() is the single resolver.
    audio_file=models.FileField(upload_to='exam-audio/',blank=True,validators=[validate_exam_audio],
        help_text='Audio faylni shu yerga yuklang (mp3, m4a, ogg, wav, webm; 40 MB gacha).')
    audio_url=models.URLField(blank=True,
        help_text='Fayl yuklamasangiz, tashqi HTTPS havolasini qo\u2018ying. Fayl yuklangan bo\u2018lsa, shu havola e\u2019tiborga olinmaydi.')
    # Only drafts can be edited; attempts additionally retain a complete snapshot.
    def audio_source(self):
        """The URL a student's browser should load. Empty when no audio is attached."""
        if self.audio_file: return self.audio_file.url
        return self.audio_url
    def __str__(self): return f'{self.title} · v{self.version}'
class Question(models.Model):
    exam=models.ForeignKey(Exam,on_delete=models.CASCADE,related_name='questions')
    position=models.PositiveIntegerField()
    # Speaking only: which part of the interview this belongs to (1, 2 or 3).
    # 0 means the section is not part-structured (Reading, Listening, Writing).
    part=models.PositiveSmallIntegerField(default=0,choices=[(0,'—'),(1,'Part 1'),(2,'Part 2 (cue card)'),(3,'Part 3')],
        help_text='Faqat Speaking uchun. 1 — tanishuv savollari, 2 — cue card, 3 — mavhum muhokama.')
    prompt=models.TextField()
    # Speaking: the examiner's recorded voice for this question. When empty the
    # browser reads the prompt aloud instead, so a bank is usable before audio exists.
    audio_file=models.FileField(upload_to='question-audio/',blank=True,validators=[validate_exam_audio],
        help_text='Ixtiyoriy. Imtihon oluvchining shu savolni o‘qigan yozuvi. Bo‘sh bo‘lsa, brauzer matnni ovoz bilan o‘qiydi.')
    # Speaking Part 2 reuses `choices` as the cue card's bullet points.
    choices=models.JSONField(default=list,blank=True)
    accepted_answers=models.JSONField(default=list,blank=True)
    evidence=models.TextField(blank=True)
    explanation=models.TextField(blank=True)
    skill_tag=models.CharField(max_length=100,blank=True)
    def audio_source(self):
        """The URL the browser should play, or '' when the prompt must be read aloud."""
        return self.audio_file.url if self.audio_file else ''
    class Meta:
        ordering=['part','position']
        constraints=[models.UniqueConstraint(fields=['exam','position'],name='unique_question_position')]
class Profile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    free_attempt_used=models.BooleanField(default=False)
    target_band=models.DecimalField(max_digits=2,decimal_places=1,default=7)
    language=models.CharField(max_length=2,default='uz',choices=[('uz','O‘zbekcha'),('en','English'),('ru','Русский')])
    phone=models.CharField(max_length=24,blank=True)
    city=models.CharField(max_length=80,blank=True)
    institution=models.CharField(max_length=160,blank=True)
    learner_type=models.CharField(max_length=24,blank=True,choices=[('school','School'),('university','University'),('learning_center','Learning center'),('independent','Independent')])
    avatar=models.TextField(blank=True)
class Entitlement(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    exam=models.ForeignKey(Exam,on_delete=models.PROTECT)
    consumed=models.BooleanField(default=False)
    reference=models.CharField(max_length=120,unique=True)
    # Entitlements are granted only by staff until a verified payment provider exists.
class ExamSession(models.Model):
    """One full IELTS Academic sitting: four sections taken in order.

    The plan is fixed when the session starts, so republishing an exam cannot
    change a sitting that is already under way. Per-section progress is not
    stored here; it is read from the Attempt rows that point back, which keeps
    a single source of truth for what a candidate has actually done.
    """
    ORDER=['Listening','Reading','Writing','Speaking']
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    plan=models.JSONField(default=list)
    state=models.CharField(max_length=24,default='in_progress')
    started_at=models.DateTimeField(auto_now_add=True)
    completed_at=models.DateTimeField(null=True,blank=True)
    class Meta: ordering=['-started_at']

class Attempt(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    exam=models.ForeignKey(Exam,on_delete=models.PROTECT)
    session=models.ForeignKey(ExamSession,on_delete=models.SET_NULL,null=True,blank=True,related_name='attempts')
    session_order=models.PositiveSmallIntegerField(default=0)
    snapshot=models.JSONField()
    answers=models.JSONField(default=dict)
    review_positions=models.JSONField(default=list,blank=True)
    state=models.CharField(max_length=24,default='in_progress')
    started_at=models.DateTimeField(auto_now_add=True)
    deadline=models.DateTimeField()
    submitted_at=models.DateTimeField(null=True,blank=True)
    result=models.JSONField(null=True,blank=True)
    class Meta: ordering=['-started_at']
class LoginThrottle(models.Model):
    key=models.CharField(max_length=64,unique=True)
    count=models.PositiveIntegerField(default=0)
    reset_at=models.DateTimeField()

class AssessmentJob(models.Model):
    attempt=models.OneToOneField(Attempt,on_delete=models.CASCADE,related_name='assessment_job')
    state=models.CharField(max_length=16,default='pending')
    tries=models.PositiveIntegerField(default=0)
    available_at=models.DateTimeField(default=timezone.now)
    lease=models.UUIDField(null=True,blank=True)
    error_code=models.CharField(max_length=64,blank=True)

class SpeakingRecording(models.Model):
    attempt=models.OneToOneField(Attempt,on_delete=models.CASCADE,related_name='speaking_recording')
    # Private, bounded audio segments. Deleted after successful assessment.
    segments=models.JSONField(default=list)
