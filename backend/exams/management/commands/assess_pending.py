import time,uuid
from datetime import timedelta
from django.core.management.base import BaseCommand,CommandError
from django.db import transaction
from django.utils import timezone
from exams.models import AssessmentJob,Attempt
from exams.gemini import configured,assess_writing,AIError

def process_one():
    now=timezone.now()
    with transaction.atomic():
        job=AssessmentJob.objects.select_for_update().filter(state__in=['pending','running'],available_at__lte=now).order_by('available_at').first()
        if not job:return False
        if job.tries>=3:
            job.state='failed';job.error_code='AI_RETRY_EXHAUSTED';job.save();return True
        job.state='running';job.tries+=1;job.lease=uuid.uuid4();job.available_at=now+timedelta(minutes=3);job.save()
        lease=job.lease;pk=job.pk;attempt=job.attempt
    try:report=assess_writing(attempt);error=None
    except AIError as exc:report=None;error=str(exc)
    with transaction.atomic():
        job=AssessmentJob.objects.select_for_update().get(pk=pk)
        if job.lease!=lease:return True
        a=Attempt.objects.select_for_update().get(pk=job.attempt_id)
        if report is not None:
            if a.state=='awaiting_assessment':
                a.result={'correct':0,'total':0,'rows':[],'skills':{},'weekly_plan':[],'band':report['band'],'assessment':report}
                a.state='graded';a.save(update_fields=['result','state'])
            job.state='done';job.error_code=''
        else:
            job.state='failed' if job.tries>=3 else 'pending';job.error_code=error
            job.available_at=timezone.now()+timedelta(seconds=60*job.tries)
        job.save()
    return True

class Command(BaseCommand):
    help='Process Gemini Writing jobs. --watch runs a polling worker; bounded retries.'
    def add_arguments(self,parser):parser.add_argument('--watch',action='store_true')
    def handle(self,*args,**options):
        if not configured():raise CommandError('Set AI_ENABLED=1 and GEMINI_API_KEY in server environment.')
        while True:
            worked=process_one()
            if not worked:
                if not options['watch']:break
                time.sleep(3)
