"""Create the full-length practice papers: 40 questions each.

These exist so that a full sitting can report a band at all. A short practice
set carries none -- see exams/bands.py -- so without a 40-question Listening
and Reading paper the overall band is permanently withheld.

Reading is published immediately: it needs no audio. Listening is created as a
DRAFT, because a Listening test without a recording is not a test; run
`manage.py generate_audio --section Listening --publish` to finish it.
"""
from django.core.management.base import BaseCommand

from exams.bands import STANDARD_LENGTH
from exams.models import Exam, Question
from exams.papers import listening_campus, reading_transport


class Command(BaseCommand):
    help = 'Create 40-question Reading and Listening papers. Never overwrites existing content.'

    def handle(self, *args, **options):
        self.build(reading_transport.TITLE, 'Reading', reading_transport.DURATION,
                   reading_transport.PASSAGE, reading_transport.ITEMS, publish=True)
        self.build(listening_campus.TITLE, 'Listening', listening_campus.DURATION,
                   listening_campus.TRANSCRIPT, listening_campus.ITEMS, publish=False)

    def build(self, title, section, duration, passage, items, publish):
        if Exam.objects.filter(title=title).exists():
            self.stdout.write(f'{section}: allaqachon mavjud.')
            return
        if len(items) != STANDARD_LENGTH:
            # The whole point of these papers is the standard length; a short
            # one would silently produce an exam that can never carry a band.
            self.stdout.write(self.style.ERROR(
                f'{section}: {len(items)} ta savol — {STANDARD_LENGTH} ta bo‘lishi kerak. To‘xtatildi.'))
            return
        exam = Exam.objects.create(title=title, section=section,
                                   duration_seconds=duration, passage=passage)
        for position, (prompt, choices, answers, evidence, explanation, tag) in enumerate(items, 1):
            Question.objects.create(exam=exam, position=position, prompt=prompt, choices=choices,
                                    accepted_answers=answers, evidence=evidence,
                                    explanation=explanation, skill_tag=tag)
        if publish:
            exam.published = True
            exam.save()
            self.stdout.write(self.style.SUCCESS(
                f'{section}: yaratildi va nashr qilindi — {STANDARD_LENGTH} savol, band chiqadi.'))
        else:
            self.stdout.write(self.style.WARNING(
                f'{section}: QORALAMA yaratildi — {STANDARD_LENGTH} savol va transkript tayyor.\n'
                '  Audio yo‘q. Yarating va nashr qiling:\n'
                '    .venv/bin/python manage.py generate_audio --section Listening --publish'))
