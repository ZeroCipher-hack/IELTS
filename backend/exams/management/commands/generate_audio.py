"""Generate examiner audio for draft exams, so no exam depends on browser speech.

Two jobs, both reading content that is already in the database:

  Speaking  one recording per question, in a single examiner voice;
  Listening one recording of the transcript stored in the exam's passage.

Only DRAFT exams are touched: a published exam is immutable by design, and an
attempt already in progress holds its own snapshot of the audio URL. Existing
audio is never overwritten unless --replace is given.
"""
import re

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from exams.gemini import AIError, configured
from exams.models import Exam
from exams.services import duplicate_exam, validate_exam
from exams.tts import EXAMINER_VOICE, SAMPLE_RATE, speak

# The transcript is stored for human reference and opens with a header line
# plus Uzbek framing; neither belongs in the recording.
TRANSCRIPT_NOISE = re.compile(r'^\s*(TRANSKRIPT|TRANSCRIPT)\s*:?\s*$', re.MULTILINE)

# Pace is not a detail. A candidate who fails because the recording outran
# them failed at nothing the exam is meant to measure. Official IELTS
# Listening runs at roughly 140-150 words a minute; a model left to its own
# devices reads far faster than that.
EXAMINER_STYLE = (
    'You are an IELTS examiner. Read the following question aloud in a calm, '
    'neutral, professional voice. Speak at a measured, unhurried pace -- about '
    '140 words per minute -- and leave a short pause after the question. '
    'Read only the words given, and do not add anything:\n\n'
)
NARRATOR_STYLE = (
    'You are recording the audio for an official IELTS Listening test. Read '
    'the passage below aloud slowly and very clearly, at about 140 words per '
    'minute -- noticeably slower than ordinary conversation, so a candidate '
    'can write answers while listening. Pause for about one second between '
    'sentences and about two seconds between paragraphs. Read only the words '
    'given, and do not add anything:\n\n'
)


class Command(BaseCommand):
    help = 'Generate Speaking question audio and Listening passage audio for draft exams.'

    def add_arguments(self, parser):
        parser.add_argument('--exam', type=int, help='Limit to one exam id.')
        parser.add_argument('--section', choices=['Speaking', 'Listening'])
        parser.add_argument('--replace', action='store_true',
                            help='Regenerate audio that already exists.')
        parser.add_argument('--voice', default=EXAMINER_VOICE)
        parser.add_argument('--duplicate', action='store_true',
                            help='Copy published exams to new drafts first, then give those drafts audio.')
        parser.add_argument('--publish', action='store_true',
                            help='Validate and publish each draft once its audio is complete.')

    def handle(self, *args, **options):
        if not configured():
            raise CommandError('Set AI_ENABLED=1 and GEMINI_API_KEY first. Check with: manage.py ai_check')

        wanted = ['Speaking', 'Listening']
        if options['exam']:
            exams = Exam.objects.filter(pk=options['exam'])
        else:
            exams = Exam.objects.filter(published=options['duplicate'], section__in=wanted)
        if options['section']:
            exams = exams.filter(section=options['section'])
        exams = list(exams)

        if options['duplicate']:
            # A published exam is immutable, so audio is added to a COPY. The
            # live exam keeps serving until the new version is published, and
            # attempts already running are untouched: they hold a snapshot.
            copies = []
            for source in exams:
                if not source.published:
                    copies.append(source)
                    continue
                copy = duplicate_exam(source)
                self.stdout.write(f'#{source.id} nusxalandi -> #{copy.id} (qoralama)')
                copies.append(copy)
            exams = copies
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
            if options['publish'] and not bad:
                self.publish(exam)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'{made} ta yozuv yaratildi.') if made
                          else self.style.WARNING('Yangi yozuv yaratilmadi.'))
        if failed:
            self.stdout.write(self.style.ERROR(
                f'{failed} ta yozuv yaratilmadi. Yuqoridagi xato kodlariga qarang.'))

    def publish(self, exam):
        try:
            validate_exam(exam)
        except ValidationError as exc:
            self.stdout.write(self.style.ERROR('   nashr qilinmadi: ' + ' '.join(exc.messages)))
            return
        exam.published = True
        exam.save()
        self.stdout.write(self.style.SUCCESS(f'   nashr qilindi (#{exam.id}).'))

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
        self.report_pace(audio, text)
        if not options['publish']:
            self.stdout.write('   Endi admin panelda «Tekshirish va nashr qilish» amalini ishlating.')
        return 1, 0

    def report_pace(self, audio, text):
        """Say out loud how fast the recording is, because too fast is unusable."""
        seconds = max(1, (len(audio) - 44) / (SAMPLE_RATE * 2))
        wpm = round(len(text.split()) / (seconds / 60))
        verdict = self.style.SUCCESS('IELTS tezligiga yaqin') if wpm <= 175 else self.style.WARNING(
            'JUDA TEZ — IELTS ~140-150 so‘z/daqiqa. Eshitib ko‘ring; kerak bo‘lsa --replace bilan qayta yarating')
        self.stdout.write(f'   davomiyligi {int(seconds)}s, taxminan {wpm} so‘z/daqiqa — {verdict}')
