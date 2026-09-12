from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from exams.models import Attempt
from exams.services import finish_attempt
class Command(BaseCommand):
    help='Submit saved answers for expired attempts. Run every minute.'
    def handle(self,*args,**options):
        count=0
        ids=Attempt.objects.filter(state='in_progress',deadline__lte=timezone.now()).values_list('pk',flat=True)
        for pk in ids.iterator():
            with transaction.atomic():
                a=Attempt.objects.select_for_update().get(pk=pk)
                if a.state=='in_progress':finish_attempt(a);count+=1
        self.stdout.write(str(count))
