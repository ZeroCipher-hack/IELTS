"""Generate examiner audio for draft exams, so no exam depends on browser speech.

Two jobs, both reading content that is already in the database:

  Speaking  one recording per question, in a single examiner voice;
  Listening one recording of the transcript stored in the exam's passage.

Only DRAFT exams are touched: a published exam is immutable by design, and an
attempt already in progress holds its own snapshot of the audio URL. Existing
audio is never overwritten unless --replace is given.
"""
import re

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from exams.gemini import AIError, configured
from exams.models import Exam
from exams.tts import EXAMINER_VOICE, speak

# The transcript is stored for human reference and opens with a header line
# plus Uzbek framing; neither belongs in the recording.
TRANSCRIPT_NOISE = re.compile(r'^\s*(TRANSKRIPT|TRANSCRIPT)\s*:?\s*$', re.MULTILINE)

EXAMINER_STYLE = (
    'Read the following IELTS examiner question aloud in a calm, neutral, '
    'professional voice, at an even pace. Read only the words given:\n\n'
)
NARRATOR_STYLE = (
    'Read the following IELTS Listening passage aloud clearly and steadily, '
    'as a recording for an exam. Read only the words given:\n\n'
)


class Command(BaseCommand):
    help = 'Generate Speaking question audio and Listening passage audio for draft exams.'

    def add_arguments(self, parser):
        parser.add_argument('--exam', type=int, help='Limit to one exam id.')
        parser.add_argument('--section', choices=['Speaking', 'Listening'])
        parser.add_argument('--replace', action='store_true',
                            help='Regenerate audio that already exists.')
        parser.add_argument('--voice', default=EXAMINER_VOICE)

    def handle(self, *args, **options):
        if not configured():
            raise CommandError('Set AI_ENABLED=1 and GEMINI_API_KEY first. Check with: manage.py ai_check')

        exams = Exam.objects.filter(published=False, section__in=['Speaking', 'Listening'])
        if options['exam']:
            exams = Exam.objects.filter(pk=options['exam'])
        if options['section']:
            exams = exams.filter(section=options['section'])
        exams = list(exams)
        if not exams:
            self.stdout.write(self.style.WARNING(
                'Mos qoralama test topilmadi. Nashr qilingan testga audio qo‘shib bo‘lmaydi — '
                'avval «Yangi versiyaga nusxalash (qoralama)» amalini ishlating.'))
            return

        made = failed = 0
        for exam in exams:
            if exam.published:
                self.stdout.write(self.style.ERROR(
                    f'#{exam.id} «{exam.title}» nashr qilingan — o‘zgartirilmaydi.'))
                continue
            self.stdout.write(f'\n#{exam.id} {exam.section} — {exam.title}')
            handler = self.speaking if exam.section == 'Speaking' else self.listening
            ok, bad = handler(exam, options)
            made += ok
            failed += bad

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'{made} ta yozuv yaratildi.') if made
                          else self.style.WARNING('Yangi yozuv yaratilmadi.'))
        if failed:
            self.stdout.write(self.style.ERROR(
                f'{failed} ta yozuv yaratilmadi. Yuqoridagi xato kodlariga qarang.'))

    def generate(self, text, style, voice, label):
        try:
            audio = speak(text, voice=voice, style=style)
        except AIError as exc:
            self.stdout.write(self.style.ERROR(f'   {label}: {exc}'))
            return None
        self.stdout.write(self.style.SUCCESS(f'   {label}: {len(audio) // 1024} KB'))
        return audio

    def speaking(self, exam, options):
        made = failed = 0
        for question in exam.questions.order_by('part', 'position'):
            if question.audio_file and not options['replace']:
                self.stdout.write(f'   {question.position}. o‘tkazildi (audio bor)')
                continue
            text = question.prompt.strip()
            if question.part == 2:
                # The cue card is read the way an examiner reads it: topic first,
                # then the points the candidate should cover.
                points = [p for p in question.choices if isinstance(p, str) and p.strip()]
                if points:
                    text = text + ' You should say: ' + '; '.join(p.strip().rstrip('.') for p in points) + '.'
            audio = self.generate(text, EXAMINER_STYLE, options['voice'],
                                  f'{question.position}. Part {question.part}')
            if audio is None:
                failed += 1
                continue
            question.audio_file.save(f'q{exam.id}-{question.position}.wav',
                                     ContentFile(audio), save=True)
            made += 1
        return made, failed

    def listening(self, exam, options):
        if exam.audio_file and not options['replace']:
            self.stdout.write('   o‘tkazildi (audio bor)')
            return 0, 0
        text = TRANSCRIPT_NOISE.sub('', exam.passage or '').strip()
        if not text:
            self.stdout.write(self.style.ERROR('   transkript bo‘sh — avval matnni yozing.'))
            return 0, 1
        audio = self.generate(text, NARRATOR_STYLE, options['voice'], 'transkript')
        if audio is None:
            return 0, 1
        exam.audio_file.save(f'listening-{exam.id}.wav', ContentFile(audio), save=True)
        self.stdout.write('   Endi admin panelda «Tekshirish va nashr qilish» amalini ishlating.')
        return 1, 0
