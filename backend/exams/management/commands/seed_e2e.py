"""Publish a Listening paper with placeholder audio, for automated tests ONLY.

The demo Listening exam is seeded as a draft on purpose: publishing a Listening
test without a real recording would be content a candidate could meet. The
end-to-end suite still needs a complete four-section catalogue to exercise a
full sitting, so this command supplies the missing piece as an obvious fixture
-- a plain tone, titled as a fixture -- and refuses to run outside DEBUG.
"""
import io
import math
import struct
import wave

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from exams.models import Exam
from exams.services import validate_exam

SECONDS = 3
RATE = 22050


def tone():
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(b''.join(
            struct.pack('<h', int(6000 * math.sin(i / 18.0))) for i in range(RATE * SECONDS)))
    return buffer.getvalue()


class Command(BaseCommand):
    help = 'Test fixture: publish the draft Listening demo with placeholder audio. DEBUG only.'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('seed_e2e is a test fixture and refuses to run with DEBUG off.')
        # Oldest first: the 40-question paper seeded last stays a draft unless
        # it is the only one, so the e2e suite keeps exercising a short paper's
        # "no band" path as well as a full sitting.
        exam = Exam.objects.filter(section='Listening', published=False).order_by('id').first()
        if exam is None:
            self.stdout.write('No draft Listening exam to publish.')
            return
        if not exam.audio_file:
            exam.audio_file.save(f'e2e-fixture-{exam.id}.wav', ContentFile(tone()), save=True)
        validate_exam(exam)
        exam.published = True
        exam.save()
        self.stdout.write(self.style.SUCCESS(
            f'Listening #{exam.id} published with FIXTURE audio (a tone, not speech).'))
