import uuid
from django.conf import settings
from django.db import models
class Exam(models.Model):
    title=models.CharField(max_length=180)
    section=models.CharField(max_length=16,choices=[(s,s) for s in ['Reading','Listening','Writing','Speaking']])
    version=models.PositiveIntegerField(default=1)
    published=models.BooleanField(default=False)
    duration_seconds=models.PositiveIntegerField(default=600)
    passage=models.TextField(blank=True)
    audio_url=models.URLField(blank=True)
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
