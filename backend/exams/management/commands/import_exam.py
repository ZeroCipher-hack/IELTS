import json
from django.core.management.base import BaseCommand,CommandError
from django.core.exceptions import ValidationError
from django.db import transaction
from exams.models import Exam,Question
from exams.services import validate_exam
class Command(BaseCommand):
    help='Import a UTF-8 JSON exam as a draft. Never publishes automatically.'
    def add_arguments(self,parser):parser.add_argument('file')
    def handle(self,*args,**options):
        try:
            with open(options['file'],encoding='utf-8') as f:data=json.load(f)
            if not isinstance(data,dict) or not isinstance(data.get('questions'),list):raise ValueError('questions ro‘yxati kerak.')
            with transaction.atomic():
                exam=Exam.objects.create(**{k:data[k] for k in ['title','section','duration_seconds','passage','audio_url'] if k in data})
                exam.full_clean()
                for i,row in enumerate(data['questions'],1):
                    q=Question(exam=exam,position=i,**{k:row[k] for k in ['prompt','choices','accepted_answers','skill_tag','evidence','explanation'] if k in row})
                    q.full_clean();q.save()
                validate_exam(exam)
            self.stdout.write(self.style.SUCCESS(f'Qoralama yaratildi: {exam.pk}. Admin paneldan nashr qiling.'))
        except (OSError,ValueError,TypeError,ValidationError) as exc:raise CommandError(str(exc))
