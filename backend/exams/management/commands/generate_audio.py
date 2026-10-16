"""Generate examiner audio for draft exams, so no exam depends on browser speech.

Two jobs, both reading content that is already in the database:

  Speaking  one recording per question, in a single examiner voice;
  Listening one recording of the transcript stored in the exam's passage.

Only DRAFT exams are touched: a published exam is immutable by design, and an
attempt already in progress holds its own snapshot of the audio URL. Existing
audio is never overwritten unless --replace is given.
"""
import re
import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from exams.gemini import AIError, configured
from exams.models import Exam
from exams.services import duplicate_exam, validate_exam
from exams.tts import EXAMINER_VOICE, SAMPLE_RATE, compress, duration, retime, speak

# The transcript is stored for human reference and opens with a header line
# plus Uzbek framing; neither belongs in the recording.
TRANSCRIPT_NOISE = re.compile(r'^\s*(TRANSKRIPT|TRANSCRIPT)\s*:?\s*$', re.MULTILINE)

# Free Gemini tiers count requests per minute, and the speech models are the
# tightest of them. Spacing requests out costs minutes; not spacing them out
# costs the whole run.
DEFAULT_DELAY = 20.0

# Waiting can fix a per-minute limit and a network blip. It cannot fix a
# malformed reply, a bad model name or an exhausted daily quota.
RETRYABLE = {'AI_RATE_LIMIT', 'AI_UNAVAILABLE'}

# IELTS Listening is spoken at roughly 140-150 words a minute. Outside this
# band the recording is not the exam the candidate is preparing for.
PACE_TARGET = '140-150'
PACE_WANTED = 145
PACE_SLOW = 110
PACE_FAST = 180

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
    'the passage below aloud clearly and steadily, at the natural pace of a '
    'news presenter -- about 145 words per minute. Do NOT read slowly or '
    'drag out the words; an IELTS recording is spoken at ordinary speed, just '
    'clearly. Keep normal sentence rhythm and do not add extra pauses. '
    'Read only the words given, and do not add anything:\n\n'
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
                            help='Copy a published exam to a new draft first, then give that draft audio. '
                                 'Needs --exam, or --all to do it for every published exam in scope.')
        parser.add_argument('--all', action='store_true',
                            help='With --duplicate: act on every matching published exam, not one.')
        parser.add_argument('--retime', action='store_true',
                            help='Correct the speed of audio that already exists. Uses no provider requests.')
        parser.add_argument('--publish', action='store_true',
                            help='Validate and publish each draft once its audio is complete.')
        parser.add_argument('--delay', type=float, default=DEFAULT_DELAY,
                            help='Seconds to wait between provider requests (free tiers are '
                                 f'measured per minute). Default {DEFAULT_DELAY:g}.')
        parser.add_argument('--retries', type=int, default=2,
                            help='Times to wait out a rate limit before giving up on a recording.')

    def handle(self, *args, **options):
        # --retime reworks audio that already exists and talks to nobody, so it
        # must not demand a key -- it is exactly what you reach for when the
        # quota is gone.
        if not options['retime'] and not configured():
            raise CommandError('Set AI_ENABLED=1 and GEMINI_API_KEY first. Check with: manage.py ai_check')

        wanted = ['Speaking', 'Listening']
        if options['exam']:
            exams = Exam.objects.filter(pk=options['exam'])
        else:
            exams = Exam.objects.filter(published=options['duplicate'], section__in=wanted)
        if options['section']:
            exams = exams.filter(section=options['section'])
        exams = list(exams)

        if options['duplicate'] and not options['exam'] and not options['all']:
            names = ', '.join(f'#{e.id} {e.title}' for e in exams)
            raise CommandError(
                'Nusxalash qaysi testga tegishli ekanini ayting: --exam <id>.\n'
                'Hammasiga tegishli bo‘lsa --all qo‘shing (har biri alohida so‘rov va '
                'alohida nashr qilingan test yaratadi).\n'
                f'Hozirgi nomzodlar: {names or "yo‘q"}')
        if options['duplicate']:
            # A published exam is immutable, so audio is added to a COPY. The
            # live exam keeps serving until the new version is published, and
            # attempts already running are untouched: they hold a snapshot.
            copies = []
            for source in exams:
                if not source.published:
                    copies.append(source)
                    continue
                existing = self.unfinished_copy(source)
                if existing is not None:
                    # Resume. Making a second copy on every run would strand
                    # the audio already paid for -- which is exactly what a
                    # rate limit makes you do: run the command again.
                    self.stdout.write(f'#{source.id}: mavjud qoralama #{existing.id} davom ettirilmoqda')
                    copies.append(existing)
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

        self.spoken_at = None
        self.exhausted = False
        self.unusable = False
        made = failed = 0
        for exam in exams:
            if self.exhausted:
                break
            if exam.published:
                # Naming the problem without naming the remedy just stops the
                # operator; the remedy is one flag away.
                flags = '--duplicate' + (' --retime' if options['retime'] else '')
                self.stdout.write(self.style.ERROR(
                    f'#{exam.id} «{exam.title}» nashr qilingan — o‘zgartirilmaydi.\n'
                    f'   Yangi versiya yarating:\n'
                    f'     manage.py generate_audio --exam {exam.id} {flags} --publish'))
                continue
            self.stdout.write(f'\n#{exam.id} {exam.section} — {exam.title}')
            self.unusable = False
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
        if self.exhausted:
            self.stdout.write(self.style.WARNING(
                '\nKunlik bepul kvota tugadi. Kutish yordam bermaydi — kvota Tinch okeani '
                'vaqti bilan yarim tunda yangilanadi.\n'
                'Yaratilgan yozuvlar saqlandi. Ertaga AYNAN SHU buyruqni qayta ishlating: '
                'u qolganidan davom etadi, yangi nusxa yaratmaydi.\n'
                'Avval Listening’ni tugating (u kamroq so‘rov oladi va usiz to‘liq imtihon '
                'boshlanmaydi); Speaking audiosiz ham ishlaydi — savollarni brauzer o‘qiydi.'))

    @staticmethod
    def unfinished_copy(source):
        """The draft of `source` that is furthest along, if one exists.

        Several may exist from earlier interrupted runs; the useful one is
        whichever already holds the most audio, not the newest.
        """
        drafts = Exam.objects.filter(title=source.title, section=source.section, published=False)
        best, best_score = None, -1
        for draft in drafts:
            score = (1 if draft.audio_file else 0) + sum(
                1 for question in draft.questions.all() if question.audio_file)
            if score > best_score or (score == best_score and best and draft.id > best.id):
                best, best_score = draft, score
        return best

    def publish(self, exam):
        if self.unusable:
            # Publishing a recording this command just called unusable would
            # put it in front of candidates over its own objection.
            self.stdout.write(self.style.ERROR(
                '   nashr qilinmadi: audio tezligi IELTS doirasidan tashqarida.'))
            return
        try:
            validate_exam(exam)
        except ValidationError as exc:
            self.stdout.write(self.style.ERROR('   nashr qilinmadi: ' + ' '.join(exc.messages)))
            return
        exam.published = True
        exam.save()
        self.stdout.write(self.style.SUCCESS(f'   nashr qilindi (#{exam.id}).'))

    def generate(self, text, style, voice, label, options):
        """One recording, pacing itself and waiting out a rate limit.

        A free-tier key is measured per minute, and a request refused for
        quota has still cost the wait. Spacing requests out and backing off is
        the difference between finishing a paper and collecting eight errors.
        """
        delay = max(0.0, options['delay'])
        attempts = max(0, options['retries']) + 1
        for attempt in range(1, attempts + 1):
            if self.spoken_at is not None and delay:
                wait = delay - (time.monotonic() - self.spoken_at)
                if wait > 0:
                    time.sleep(wait)
            try:
                audio = speak(text, voice=voice, style=style,
                              on_piece=lambda i, n: self.piece(i, n, label, delay))
            except AIError as exc:
                self.spoken_at = time.monotonic()
                code = str(exc)
                if getattr(exc, 'per_day', False):
                    # A daily cap does not lift by waiting. Saying so is worth
                    # more than three more sleeps and the same error.
                    self.exhausted = True
                    self.stdout.write(self.style.ERROR(f'   {label}: kunlik limit tugadi'))
                    return None
                if code not in RETRYABLE or attempt == attempts:
                    self.stdout.write(self.style.ERROR(f'   {label}: {exc}'))
                    return None
                # Google states how long to wait; its number beats any guess.
                backoff = getattr(exc, 'retry_after', None)
                backoff = (backoff + 5) if backoff else delay * (2 ** attempt) + 30
                self.stdout.write(self.style.WARNING(
                    f'   {label}: {code} — {int(backoff)}s kutilmoqda ({attempt}/{attempts - 1})'))
                time.sleep(backoff)
                continue
            self.spoken_at = time.monotonic()
            self.stdout.write(self.style.SUCCESS(f'   {label}: {len(audio) // 1024} KB'))
            return audio
        return None

    def piece(self, index, total, label, delay):
        """Pace the requests WITHIN one long recording as well as between them."""
        if total > 1:
            self.stdout.write(f'   {label}: qism {index + 1}/{total}…', ending='\r')
        if index and delay:
            time.sleep(delay)

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
                                  f'{question.position}. Part {question.part}', options)
            if audio is None:
                failed += 1
                if self.exhausted:
                    break
                continue
            stored, extension = compress(audio)
            question.audio_file.save(f'q{exam.id}-{question.position}.{extension}',
                                     ContentFile(stored), save=True)
            made += 1
        return made, failed

    def listening(self, exam, options):
        text = TRANSCRIPT_NOISE.sub('', exam.passage or '').strip()
        if not text:
            self.stdout.write(self.style.ERROR('   transkript bo‘sh — avval matnni yozing.'))
            return 0, 1

        if options['retime']:
            return self.retime_existing(exam, text)
        if exam.audio_file and not options['replace']:
            self.stdout.write('   o‘tkazildi (audio bor)')
            return 0, 0

        audio = self.generate(text, NARRATOR_STYLE, options['voice'], 'transkript', options)
        if audio is None:
            return 0, 1
        stored, extension = compress(audio)
        seconds = max(1.0, (len(audio) - 44) / (SAMPLE_RATE * 2))
        stored, extension, seconds = self.correct(stored, extension, text, seconds)
        exam.audio_file.save(f'listening-{exam.id}.{extension}', ContentFile(stored), save=True)
        self.report_pace(seconds, text, len(stored))
        if not options['publish']:
            self.stdout.write('   Endi admin panelda «Tekshirish va nashr qilish» amalini ishlating.')
        return 1, 0

    def correct(self, data, extension, text, seconds):
        """Pull the reading speed into the IELTS band by retiming the audio.

        Asking the model for a pace does not work: the same instruction gave
        66 words a minute one run and 187 the next. Measuring and correcting
        is exact, keeps the pitch, and costs no provider request -- which is
        the whole budget when a free quota is the binding constraint.
        """
        words = len(text.split())
        wpm = words / (seconds / 60)
        if PACE_SLOW <= wpm <= PACE_FAST:
            return data, extension, seconds
        # A playback SPEED, not a ratio of rates: reading at 187 when 145 is
        # wanted must be played at 145/187, which makes it longer and slower.
        speed = PACE_WANTED / wpm
        fixed, new_extension = retime(data, extension, speed)
        if fixed is data:
            self.stdout.write(self.style.WARNING(
                '   tezlikni to‘g‘rilab bo‘lmadi (ffmpeg kerak): sudo apt install ffmpeg'))
            return data, extension, seconds
        measured = duration(fixed, new_extension) or (seconds / speed)
        self.stdout.write(
            f'   tezlik to‘g‘rilandi: {round(wpm)} → {round(words / (measured / 60))} so‘z/daqiqa')
        return fixed, new_extension, measured

    def retime_existing(self, exam, text):
        """Fix the speed of a recording already made. No provider request."""
        if not exam.audio_file:
            self.stdout.write(self.style.ERROR('   audio yo‘q — avval yarating.'))
            return 0, 1
        exam.audio_file.open('rb')
        try:
            data = exam.audio_file.read()
        finally:
            exam.audio_file.close()
        extension = exam.audio_file.name.rsplit('.', 1)[-1].lower()
        seconds = duration(data, extension)
        if seconds is None:
            self.stdout.write(self.style.ERROR(
                '   davomiylikni o‘lchab bo‘lmadi (ffprobe kerak): sudo apt install ffmpeg'))
            return 0, 1
        fixed, new_extension, measured = self.correct(data, extension, text, seconds)
        if fixed is data:
            self.report_pace(seconds, text, len(data))
            return 0, 0
        exam.audio_file.save(f'listening-{exam.id}.{new_extension}', ContentFile(fixed), save=True)
        self.report_pace(measured, text, len(fixed))
        return 1, 0

    def report_pace(self, seconds, text, size):
        """Report the reading speed and the file size, and judge BOTH ends.

        An earlier version only guarded against a recording that raced, and so
        passed one read at 66 words a minute -- half IELTS pace -- as fine. A
        recording that drags is just as unusable: it is not the exam the
        candidate is preparing for, and it is twice the download.
        """
        seconds = max(1.0, seconds)
        wpm = round(len(text.split()) / (seconds / 60))
        again = ' Eshitib ko‘ring va --replace bilan qayta yarating.'
        if wpm < PACE_SLOW or wpm > PACE_FAST:
            self.unusable = True
            label = 'JUDA SEKIN' if wpm < PACE_SLOW else 'JUDA TEZ'
            verdict = self.style.ERROR(f'{label} — IELTS ~{PACE_TARGET} so‘z/daqiqa.' + again)
        else:
            verdict = self.style.SUCCESS('IELTS tezligiga yaqin')
        self.stdout.write(
            f'   davomiyligi {int(seconds // 60)}:{int(seconds % 60):02d}, '
            f'taxminan {wpm} so‘z/daqiqa — {verdict}')

        ceiling = settings.EXAM_AUDIO_MAX_BYTES
        shown = f'{size / 1024 / 1024:.1f} MB' if size >= 1024 * 1024 else f'{size // 1024} KB'
        self.stdout.write(f'   fayl hajmi {shown}')
        if size > ceiling * 0.8:
            self.stdout.write(self.style.WARNING(
                f'   DIQQAT: chegara {ceiling // 1024 // 1024} MB ga yaqin. '
                'ffmpeg o‘rnatilsa fayl MP3 ga siqiladi va ~6 barobar kichrayadi: '
                'sudo apt install ffmpeg'))
