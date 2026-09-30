import uuid
from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator
from .validators import validate_audio_upload
from django.utils import timezone
class Exam(models.Model):
    title=models.CharField(max_length=180)
    section=models.CharField(max_length=16,choices=[(s,s) for s in ['Reading','Listening','Writing','Speaking']])
    version=models.PositiveIntegerField(default=1)
    published=models.BooleanField(default=False)
    duration_seconds=models.PositiveIntegerField(default=600)
    passage=models.TextField(blank=True)
    listening_transcript=models.TextField(blank=True)
    audio_url=models.URLField(blank=True)
    audio_file=models.FileField(upload_to='exam_audio/',blank=True,validators=[FileExtensionValidator(['mp3','wav','ogg','m4a','webm']),validate_audio_upload])
    # Only drafts can be edited; attempts additionally retain a complete snapshot.
    def __str__(self): return f'{self.title} · v{self.version}'
class Question(models.Model):
    exam=models.ForeignKey(Exam,on_delete=models.CASCADE,related_name='questions')
    position=models.PositiveIntegerField()
    prompt=models.TextField()
    choices=models.JSONField(default=list,blank=True)
    accepted_answers=models.JSONField(default=list,blank=True)
    evidence=models.TextField(blank=True)
    explanation=models.TextField(blank=True)
    skill_tag=models.CharField(max_length=100,blank=True)
    class Meta:
        ordering=['position']
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
class Attempt(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    exam=models.ForeignKey(Exam,on_delete=models.PROTECT)
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

class SpeakingSet(models.Model):
    title=models.CharField(max_length=180)
    version=models.PositiveIntegerField(default=1)
    published=models.BooleanField(default=False)
    part1_questions=models.JSONField(default=list)
    cue_title=models.CharField(max_length=500)
    cue_points=models.JSONField(default=list)
    part3_questions=models.JSONField(default=list)

    class Meta:
        verbose_name='Speaking savol to‘plami'
        verbose_name_plural='Speaking savol to‘plamlari'

    def __str__(self):return f'{self.title} · v{self.version}'

    def clean(self):
        from django.core.exceptions import ValidationError
        errors={}
        for name,limit in [('part1_questions',15),('cue_points',5),('part3_questions',12)]:
            values=getattr(self,name)
            minimum=3 if name=='cue_points' else 1
            if not isinstance(values,list) or not minimum<=len(values)<=limit or any(not isinstance(value,str) or not value.strip() or len(value)>500 for value in values):
                errors[name]=f'{minimum}–{limit} ta matn kiriting; har biri 500 belgidan oshmasin.'
        if not self.cue_title.strip():errors['cue_title']='Cue card mavzusi kerak.'
        if errors:raise ValidationError(errors)
