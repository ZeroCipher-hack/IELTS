import time,uuid
from datetime import timedelta
from django.core.management.base import BaseCommand,CommandError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from exams.models import AssessmentJob,Attempt,SpeakingRecording
from exams.speaking_assessment import assess_speaking
from exams.gemini import configured,assess_writing,assess_objective,AIError

def process_one():
    now=timezone.now()
    # A conditional write claims the row even on SQLite, where select_for_update is ignored.
    for candidate in AssessmentJob.objects.filter(state__in=['pending','running'],available_at__lte=now).order_by('available_at')[:20]:
        claim=AssessmentJob.objects.filter(pk=candidate.pk,state=candidate.state,lease=candidate.lease,
            tries=candidate.tries,available_at=candidate.available_at)
        if candidate.tries>=3:
            if not claim.update(state='failed',error_code='AI_RETRY_EXHAUSTED'):continue
            if candidate.attempt.snapshot.get('section')=='Speaking':SpeakingRecording.objects.filter(attempt=candidate.attempt).delete()
            return True
        lease=uuid.uuid4()
        if claim.update(state='running',tries=F('tries')+1,lease=lease,available_at=now+timedelta(minutes=3)):
            pk=candidate.pk;attempt=candidate.attempt
            break
    else:return False
    section=attempt.snapshot.get('section')
    try:
        report=(assess_speaking(attempt) if section=='Speaking' else assess_writing(attempt) if section=='Writing' else assess_objective(attempt));error=None
    except AIError as exc:report=None;error=str(exc)
    with transaction.atomic():
        job=AssessmentJob.objects.get(pk=pk)
        if job.lease!=lease or job.state!='running':return True
        next_state=('done' if report is not None else 'failed' if job.tries>=3 or error in ('AI_INSUFFICIENT_AUDIO','AI_RECORDING_UNAVAILABLE') else 'pending')
        next_error='' if report is not None else error
        next_available=job.available_at if report is not None else timezone.now()+timedelta(seconds=60*job.tries)
        if not AssessmentJob.objects.filter(pk=pk,lease=lease,state='running').update(
                state=next_state,error_code=next_error,available_at=next_available):return True
        a=Attempt.objects.select_for_update().get(pk=job.attempt_id)
        if report is not None:
            if section in ('Reading','Listening') and a.state=='graded' and a.result is not None:
                a.result={**a.result,'tutoring':report};a.save(update_fields=['result'])
            elif a.state=='awaiting_assessment':
                a.result={'correct':0,'total':0,'rows':[],'skills':{},'weekly_plan':[],'band':report['band'],'assessment':report}
                a.state='graded';a.save(update_fields=['result','state'])
            if a.snapshot.get('section')=='Speaking':a.speaking_recording.delete()
        else:
            if next_state=='failed' and section=='Speaking':SpeakingRecording.objects.filter(attempt=a).delete()
    return True

class Command(BaseCommand):
    help='Process Gemini Writing and Speaking jobs. --watch runs a polling worker; bounded retries.'
    def add_arguments(self,parser):parser.add_argument('--watch',action='store_true')
    def handle(self,*args,**options):
        if not configured():raise CommandError('Set AI_ENABLED=1 and GEMINI_API_KEY in server environment.')
        while True:
            worked=process_one()
            if not worked:
                if not options['watch']:break
                time.sleep(3)
