"""Generated examiner audio: a real recording or a clear failure, never silence."""
import base64
import io
import json
import shutil
import tempfile
import wave
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from .gemini import AIError
from .models import Exam, Question
from .tts import SAMPLE_RATE, speak

MEDIA = tempfile.mkdtemp()
PCM = b'\x01\x00' * SAMPLE_RATE * 2  # two seconds


def reply(pcm=PCM, mime='audio/L16;codec=pcm;rate=24000'):
    return {'candidates': [{'content': {'parts': [
        {'inlineData': {'mimeType': mime, 'data': base64.b64encode(pcm).decode()}}]}}]}


@override_settings(AI_ENABLED=True, GEMINI_API_KEY='k', GEMINI_TTS_MODEL='gemini-2.5-flash-preview-tts')
class SpeakTests(TestCase):
    def test_pcm_comes_back_as_a_playable_wav(self):
        with patch('exams.tts.post', return_value=reply()) as called:
            audio = speak('Can you tell me about the place where you live?')
        self.assertEqual(audio[:4], b'RIFF')
        with wave.open(io.BytesIO(audio)) as handle:
            self.assertEqual(handle.getnchannels(), 1)
            self.assertEqual(handle.getsampwidth(), 2)
            self.assertEqual(handle.getframerate(), SAMPLE_RATE)
            self.assertEqual(handle.getnframes(), SAMPLE_RATE * 2)
        request = called.call_args.args[1]
        self.assertEqual(request['generationConfig']['responseModalities'], ['AUDIO'])

    def test_the_response_cap_is_raised_for_audio(self):
        """Audio is megabytes of base64; the 1 MiB JSON cap would reject it."""
        with patch('exams.tts.post', return_value=reply()) as called:
            speak('Hello')
        self.assertGreater(called.call_args.kwargs['limit'], 8 * 1024 * 1024)

    def test_empty_and_overlong_text_never_reach_the_provider(self):
        from .tts import MAX_TOTAL_CHARS
        with patch('exams.tts.post') as called:
            for text in ('', '   ', 'x' * (MAX_TOTAL_CHARS + 1)):
                with self.subTest(text=text[:10]), self.assertRaises(AIError):
                    speak(text)
            called.assert_not_called()

    def test_an_injected_model_or_voice_name_is_refused(self):
        with patch('exams.tts.post') as called:
            with override_settings(GEMINI_TTS_MODEL='../../auth_tokens'):
                with self.assertRaises(AIError):
                    speak('Hello')
            with self.assertRaises(AIError):
                speak('Hello', voice='Kore:generateContent')
            called.assert_not_called()

    def test_a_reply_without_audio_is_an_error_not_an_empty_file(self):
        for broken in ({'candidates': []},
                       {'candidates': [{'content': {'parts': [{'text': 'sorry'}]}}]},
                       reply(mime='text/plain'),
                       reply(pcm=b'\x00' * 64)):
            with self.subTest(), patch('exams.tts.post', return_value=broken):
                with self.assertRaises(AIError):
                    speak('Hello')


@override_settings(MEDIA_ROOT=MEDIA, AI_ENABLED=True, GEMINI_API_KEY='k')
class GenerateAudioCommandTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA, ignore_errors=True)
        super().tearDownClass()

    def speaking_draft(self):
        exam = Exam.objects.create(title='S', section='Speaking', duration_seconds=900)
        Question.objects.create(exam=exam, position=1, part=1, prompt='Where do you live?')
        Question.objects.create(exam=exam, position=2, part=2, prompt='Describe a skill.',
                                choices=['What the skill is', 'Why you want to learn it'])
        return exam

    def run_command(self, **kwargs):
        out = io.StringIO()
        kwargs.setdefault('delay', 0)
        call_command('generate_audio', stdout=out, stderr=out, **kwargs)
        return out.getvalue()

    def test_every_speaking_question_gets_its_own_recording(self):
        exam = self.speaking_draft()
        with patch('exams.management.commands.generate_audio.speak', return_value=b'RIFFfake') as spoke:
            self.run_command()
        self.assertEqual(spoke.call_count, 2)
        self.assertTrue(all(q.audio_file for q in exam.questions.all()))

    def test_the_cue_card_is_read_with_its_points(self):
        self.speaking_draft()
        with patch('exams.management.commands.generate_audio.speak', return_value=b'RIFFfake') as spoke:
            self.run_command()
        spoken = spoke.call_args_list[1].args[0]
        self.assertIn('You should say', spoken)
        self.assertIn('What the skill is', spoken)

    def test_existing_audio_is_kept_unless_replace_is_asked_for(self):
        self.speaking_draft()
        with patch('exams.management.commands.generate_audio.speak', return_value=b'RIFFfake'):
            self.run_command()
        with patch('exams.management.commands.generate_audio.speak', return_value=b'RIFFnew') as spoke:
            self.run_command()
            spoke.assert_not_called()
            self.run_command(replace=True)
            self.assertEqual(spoke.call_count, 2)

    def test_a_published_exam_is_never_touched(self):
        exam = self.speaking_draft()
        exam.published = True
        exam.save()
        with patch('exams.management.commands.generate_audio.speak') as spoke:
            output = self.run_command(exam=exam.id)
        spoke.assert_not_called()
        self.assertIn('nashr qilingan', output)

    def test_listening_audio_is_made_from_the_stored_transcript(self):
        exam = Exam.objects.create(title='L', section='Listening', duration_seconds=900,
                                   passage='TRANSKRIPT\n\nWelcome to the campus library.')
        Question.objects.create(exam=exam, position=1, prompt='Q', accepted_answers=['TRUE'])
        with patch('exams.management.commands.generate_audio.speak', return_value=b'RIFFfake') as spoke:
            self.run_command()
        exam.refresh_from_db()
        self.assertTrue(exam.audio_file)
        self.assertNotIn('TRANSKRIPT', spoke.call_args.args[0],
                         'the header is a note to staff, not words to read aloud')

    def test_a_provider_failure_is_reported_and_leaves_no_file(self):
        exam = self.speaking_draft()
        # A broken reply, not a rate limit: waiting cannot fix it, so this
        # exercises the plain failure path without the backoff machinery.
        with patch('exams.management.commands.generate_audio.speak', side_effect=AIError('AI_TTS_NO_AUDIO')):
            output = self.run_command()
        self.assertIn('AI_TTS_NO_AUDIO', output)
        self.assertIn('yaratilmadi', output)
        self.assertFalse(any(q.audio_file for q in exam.questions.all()))

    @override_settings(AI_ENABLED=False, GEMINI_API_KEY='')
    def test_without_a_key_it_refuses_instead_of_half_working(self):
        with self.assertRaises(CommandError):
            self.run_command()


@override_settings(MEDIA_ROOT=MEDIA, AI_ENABLED=True, GEMINI_API_KEY='k')
class PublishedExamAudioTests(TestCase):
    """Adding audio to a live exam goes through a new version, never in place."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA, ignore_errors=True)
        super().tearDownClass()

    def speaking(self, published=True):
        exam = Exam.objects.create(title='S', section='Speaking', duration_seconds=900,
                                   passage='Guidance.')
        Question.objects.create(exam=exam, position=1, part=1, prompt='Where do you live?',
                                accepted_answers=[])
        Question.objects.create(exam=exam, position=2, part=2, prompt='Describe a skill.',
                                choices=['What it is'], accepted_answers=[])
        Question.objects.create(exam=exam, position=3, part=3, prompt='Why learn skills?',
                                accepted_answers=[])
        exam.published = published
        exam.save()
        return exam

    def run_command(self, **kwargs):
        out = io.StringIO()
        kwargs.setdefault('delay', 0)
        call_command('generate_audio', stdout=out, stderr=out, **kwargs)
        return out.getvalue()

    def test_duplicate_leaves_the_live_exam_untouched(self):
        live = self.speaking()
        with patch('exams.management.commands.generate_audio.speak', return_value=b'RIFFfake'):
            self.run_command(duplicate=True)
        live.refresh_from_db()
        self.assertTrue(live.published)
        self.assertFalse(any(q.audio_file for q in live.questions.all()),
                         'the published exam must not gain audio in place')
        copy = Exam.objects.exclude(pk=live.pk).get()
        self.assertFalse(copy.published)
        self.assertEqual(copy.version, live.version + 1)
        self.assertEqual(copy.questions.count(), 3)
        self.assertTrue(all(q.audio_file for q in copy.questions.all()))

    def test_publish_makes_the_new_version_the_live_one(self):
        live = self.speaking()
        with patch('exams.management.commands.generate_audio.speak', return_value=b'RIFFfake'):
            output = self.run_command(duplicate=True, publish=True)
        self.assertIn('nashr qilindi', output)
        newest = Exam.objects.filter(section='Speaking', published=True).order_by('-id').first()
        self.assertNotEqual(newest.pk, live.pk)
        self.assertTrue(all(q.audio_file for q in newest.questions.all()))

    def test_an_incomplete_draft_is_not_published(self):
        exam = Exam.objects.create(title='S', section='Speaking', duration_seconds=900)
        Question.objects.create(exam=exam, position=1, part=1, prompt='Only a Part 1.',
                                accepted_answers=[])
        with patch('exams.management.commands.generate_audio.speak', return_value=b'RIFFfake'):
            output = self.run_command(publish=True)
        exam.refresh_from_db()
        self.assertFalse(exam.published)
        self.assertIn('nashr qilinmadi', output)

    def test_without_duplicate_a_published_exam_is_skipped(self):
        live = self.speaking()
        with patch('exams.management.commands.generate_audio.speak') as spoke:
            self.run_command(exam=live.id)
        spoke.assert_not_called()
        self.assertEqual(Exam.objects.count(), 1, 'no copy may be made unless asked for')


@override_settings(MEDIA_ROOT=MEDIA, AI_ENABLED=True, GEMINI_API_KEY='k')
class PaceReportTests(TestCase):
    """Reading speed is reported, because a recording that races is unusable."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA, ignore_errors=True)
        super().tearDownClass()

    def listening(self, words):
        exam = Exam.objects.create(title='L', section='Listening', duration_seconds=900,
                                   passage=' '.join(['word'] * words))
        Question.objects.create(exam=exam, position=1, prompt='Q', accepted_answers=['yes'])
        return exam

    def run_with(self, words, seconds):
        from exams.tts import SAMPLE_RATE
        audio = b'R' * (44 + SAMPLE_RATE * 2 * seconds)
        self.listening(words)
        out = io.StringIO()
        with patch('exams.management.commands.generate_audio.speak', return_value=audio):
            call_command('generate_audio', stdout=out, stderr=out, delay=0)
        return out.getvalue()

    def test_an_exam_paced_recording_passes(self):
        output = self.run_with(words=145, seconds=60)
        self.assertIn('145 so‘z/daqiqa', output)
        self.assertIn('IELTS tezligiga yaqin', output)

    def test_a_racing_recording_is_called_out(self):
        output = self.run_with(words=280, seconds=60)
        self.assertIn('JUDA TEZ', output)
        self.assertIn('--replace', output)

    def test_a_dragging_recording_is_called_out_too(self):
        """A real run read at 66 wpm -- half IELTS pace -- and was passed as
        fine, because only the fast end was ever checked."""
        output = self.run_with(words=66, seconds=60)
        self.assertIn('66 so‘z/daqiqa', output)
        self.assertIn('JUDA SEKIN', output)
        self.assertNotIn('yaqin', output)
        self.assertIn('--replace', output)

    def test_both_edges_of_the_accepted_band(self):
        from exams.management.commands.generate_audio import PACE_FAST, PACE_SLOW
        for wpm in (PACE_SLOW, PACE_FAST):
            with self.subTest(wpm=wpm):
                self.assertIn('IELTS tezligiga yaqin', self.run_with(words=wpm, seconds=60))
        for wpm in (PACE_SLOW - 1, PACE_FAST + 1):
            with self.subTest(wpm=wpm):
                self.assertNotIn('IELTS tezligiga yaqin', self.run_with(words=wpm, seconds=60))

    def test_a_file_near_the_upload_ceiling_is_flagged(self):
        from django.conf import settings
        ceiling = settings.EXAM_AUDIO_MAX_BYTES
        from exams.tts import SAMPLE_RATE
        seconds = int(ceiling * 0.95) // (SAMPLE_RATE * 2)
        output = self.run_with(words=145 * seconds // 60, seconds=seconds)
        self.assertIn('DIQQAT', output)
        self.assertIn('ffmpeg', output)


class CompressTests(TestCase):
    """A 40 MB WAV is a cruel download; MP3 is the same speech a tenth the size."""

    def wav(self, seconds=3):
        import math
        import struct
        from exams.tts import SAMPLE_RATE
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(SAMPLE_RATE)
            out.writeframes(b''.join(struct.pack('<h', int(8000 * math.sin(i / 18.0)))
                                     for i in range(SAMPLE_RATE * seconds)))
        return buffer.getvalue()

    def test_a_recording_is_made_much_smaller(self):
        from exams.tts import compress
        source = self.wav()
        data, extension = compress(source)
        if extension == 'wav':
            self.skipTest('ffmpeg is not installed in this environment')
        self.assertEqual(extension, 'mp3')
        self.assertLess(len(data), len(source) / 3)

    def test_without_ffmpeg_the_wav_is_kept_rather_than_failing(self):
        from exams.tts import compress
        source = self.wav()
        with patch('exams.tts.shutil.which', return_value=None):
            data, extension = compress(source)
        self.assertEqual((data, extension), (source, 'wav'))

    def test_a_failed_encode_falls_back_instead_of_storing_rubbish(self):
        import subprocess
        from exams.tts import compress
        source = self.wav()
        with patch('exams.tts.shutil.which', return_value='/usr/bin/ffmpeg'), \
                patch('exams.tts.subprocess.run',
                      side_effect=subprocess.CalledProcessError(1, 'ffmpeg')):
            self.assertEqual(compress(source), (source, 'wav'))

    def test_an_implausible_result_is_rejected(self):
        """An empty or non-MP3 output must never be stored as the exam audio."""
        from exams.tts import compress
        source = self.wav()

        def write_rubbish(args, **kwargs):
            with open(args[-1], 'wb') as handle:
                handle.write(b'')
            return subprocess.CompletedProcess(args, 0)

        import subprocess
        with patch('exams.tts.shutil.which', return_value='/usr/bin/ffmpeg'), \
                patch('exams.tts.subprocess.run', side_effect=write_rubbish):
            self.assertEqual(compress(source), (source, 'wav'))

    def test_the_stored_file_is_named_by_what_it_actually_is(self):
        from exams.tts import compress
        _, extension = compress(self.wav())
        self.assertIn(extension, ('mp3', 'wav'))
        from django.conf import settings
        self.assertIn(extension, settings.EXAM_AUDIO_EXTENSIONS)


class SplitTests(TestCase):
    """Long text becomes as few requests as the limit allows, losing nothing."""

    def test_short_text_is_one_request(self):
        from .tts import split
        self.assertEqual(split('Hello there.'), ['Hello there.'])

    def test_short_paragraphs_are_packed_not_split_one_per_line(self):
        """A transcript of dialogue lines must not become a request per line."""
        from .tts import split
        text = '\n\n'.join(f'SPEAKER: line number {i}.' for i in range(40))
        pieces = split(text, limit=400)
        self.assertLess(len(pieces), 10)
        self.assertTrue(all(len(p) <= 400 for p in pieces))

    def test_an_oversized_paragraph_breaks_at_sentence_ends(self):
        from .tts import split
        text = ' '.join(f'This is sentence number {i}.' for i in range(60))
        pieces = split(text, limit=200)
        self.assertTrue(all(len(p) <= 200 for p in pieces))
        for piece in pieces:
            self.assertTrue(piece.rstrip().endswith('.'), piece)

    def test_a_single_overlong_sentence_is_cut_rather_than_dropped(self):
        from .tts import split
        text = 'word ' * 500
        pieces = split(text, limit=100)
        self.assertTrue(all(len(p) <= 100 for p in pieces))
        self.assertEqual(''.join(pieces).replace(' ', ''), text.replace(' ', ''))

    def test_no_word_is_lost_from_a_real_transcript(self):
        from .papers.listening_campus import TRANSCRIPT
        from .tts import split
        pieces = split(TRANSCRIPT)
        self.assertEqual(''.join(pieces).replace(' ', '').replace('\n', ''),
                         TRANSCRIPT.replace(' ', '').replace('\n', ''))


@override_settings(AI_ENABLED=True, GEMINI_API_KEY='k')
class LongNarrationTests(TestCase):
    def test_a_transcript_too_long_for_one_request_is_read_in_pieces(self):
        from .papers.listening_campus import TRANSCRIPT
        from .tts import split
        expected = len(split(TRANSCRIPT))
        self.assertGreater(expected, 1, 'this transcript is the case under test')
        with patch('exams.tts._pcm', return_value=PCM) as called:
            audio = speak(TRANSCRIPT)
        self.assertEqual(called.call_count, expected)
        with wave.open(io.BytesIO(audio)) as handle:
            self.assertEqual(handle.getnframes(), SAMPLE_RATE * 2 * expected)

    def test_the_pieces_are_joined_in_order(self):
        with patch('exams.tts._pcm', side_effect=lambda t, v, s: t.encode()) as called:
            speak('A' * 2000 + '\n\n' + 'B' * 2000 + '\n\n' + 'C' * 2000)
        spoken = [call.args[0] for call in called.call_args_list]
        self.assertEqual([p[0] for p in spoken], ['A', 'B', 'C'])

    def test_a_whole_book_is_still_refused(self):
        with patch('exams.tts._pcm') as called:
            with self.assertRaises(AIError):
                speak('x' * 50000)
            called.assert_not_called()


@override_settings(MEDIA_ROOT=MEDIA, AI_ENABLED=True, GEMINI_API_KEY='k')
class RateLimitTests(TestCase):
    """A rate limit must cost a wait, not the run."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA, ignore_errors=True)
        super().tearDownClass()

    def listening_draft(self):
        exam = Exam.objects.create(title='L', section='Listening', duration_seconds=900,
                                   passage='Welcome to the library.')
        Question.objects.create(exam=exam, position=1, prompt='Q', accepted_answers=['yes'])
        return exam

    def run_command(self, **kwargs):
        out = io.StringIO()
        kwargs.setdefault('delay', 0)
        call_command('generate_audio', stdout=out, stderr=out, **kwargs)
        return out.getvalue()

    def test_a_rate_limit_is_waited_out_and_the_recording_still_made(self):
        exam = self.listening_draft()
        attempts = [AIError('AI_RATE_LIMIT'), b'RIFFfake']

        def answer(*args, **kwargs):
            result = attempts.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

        with patch('exams.management.commands.generate_audio.speak', side_effect=answer), \
                patch('exams.management.commands.generate_audio.time.sleep') as slept:
            output = self.run_command()
        exam.refresh_from_db()
        self.assertTrue(exam.audio_file, 'the retry must actually produce the recording')
        self.assertIn('AI_RATE_LIMIT', output)
        self.assertIn('kutilmoqda', output)
        self.assertTrue(slept.called, 'a rate limit must be waited out, not retried at once')

    def test_retries_are_bounded(self):
        self.listening_draft()
        with patch('exams.management.commands.generate_audio.speak',
                   side_effect=AIError('AI_RATE_LIMIT')) as spoke, \
                patch('exams.management.commands.generate_audio.time.sleep'):
            output = self.run_command(retries=2)
        self.assertEqual(spoke.call_count, 3)
        self.assertIn('AI_RATE_LIMIT', output)

    def test_an_error_that_is_not_a_rate_limit_is_not_retried(self):
        self.listening_draft()
        with patch('exams.management.commands.generate_audio.speak',
                   side_effect=AIError('AI_TTS_NO_AUDIO')) as spoke, \
                patch('exams.management.commands.generate_audio.time.sleep'):
            self.run_command(retries=5)
        self.assertEqual(spoke.call_count, 1, 'waiting cannot fix a broken reply')


@override_settings(MEDIA_ROOT=MEDIA, AI_ENABLED=True, GEMINI_API_KEY='k')
class ResumeTests(TestCase):
    """An interrupted run must be resumable, not restarted from nothing."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA, ignore_errors=True)
        super().tearDownClass()

    def speaking(self):
        exam = Exam.objects.create(title='S', section='Speaking', duration_seconds=900)
        for position, part in ((1, 1), (2, 2), (3, 3)):
            Question.objects.create(exam=exam, position=position, part=part,
                                    prompt=f'Prompt {position}',
                                    choices=['A point'] if part == 2 else [], accepted_answers=[])
        exam.published = True
        exam.save()
        return exam

    def run_command(self, **kwargs):
        out = io.StringIO()
        kwargs.setdefault('delay', 0)
        call_command('generate_audio', stdout=out, stderr=out, **kwargs)
        return out.getvalue()

    def test_a_second_run_resumes_the_same_draft(self):
        live = self.speaking()
        failing = [b'RIFF1', AIError('AI_RATE_LIMIT'), AIError('AI_RATE_LIMIT')]

        def answer(*args, **kwargs):
            result = failing.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

        with patch('exams.management.commands.generate_audio.speak', side_effect=answer), \
                patch('exams.management.commands.generate_audio.time.sleep'):
            self.run_command(duplicate=True, retries=0)
        drafts = Exam.objects.filter(published=False)
        self.assertEqual(drafts.count(), 1)
        self.assertEqual(sum(1 for q in drafts.get().questions.all() if q.audio_file), 1)

        with patch('exams.management.commands.generate_audio.speak', return_value=b'RIFF2'), \
                patch('exams.management.commands.generate_audio.time.sleep'):
            output = self.run_command(duplicate=True)
        self.assertIn('davom ettirilmoqda', output)
        self.assertEqual(Exam.objects.filter(published=False).count(), 1,
                         'a second copy would strand the audio already paid for')
        draft = Exam.objects.get(published=False)
        self.assertTrue(all(q.audio_file for q in draft.questions.all()))
        self.assertEqual(Exam.objects.filter(pk=live.pk, published=True).count(), 1)

    def test_the_furthest_along_draft_wins_when_several_exist(self):
        """Earlier versions of this command left a trail of empty copies."""
        live = self.speaking()
        from exams.services import duplicate_exam
        empty = duplicate_exam(live)
        partial = duplicate_exam(live)
        question = partial.questions.first()
        question.audio_file.save('x.wav', ContentFile(b'RIFF'), save=True)
        with patch('exams.management.commands.generate_audio.speak', return_value=b'RIFFnew'):
            output = self.run_command(duplicate=True)
        self.assertIn(f'#{partial.id}', output)
        self.assertNotIn(f'davom ettirilmoqda\n\n#{empty.id}', output)
        empty.refresh_from_db()
        self.assertFalse(any(q.audio_file for q in empty.questions.all()))


class ThrottleDetailTests(TestCase):
    """Google says how long to wait and which quota ran out. Read both."""

    def throttle(self, details):
        from urllib.error import HTTPError
        body = json.dumps({'error': {'code': 429, 'status': 'RESOURCE_EXHAUSTED',
                                     'message': 'Quota exceeded for key AIzaSECRET',
                                     'details': details}}).encode()
        return HTTPError('https://x', 429, 'Too Many Requests', {}, io.BytesIO(body))

    def raised(self, details):
        from .gemini import post
        with override_settings(AI_ENABLED=True, GEMINI_API_KEY='k'):
            with patch('exams.gemini.urlopen', side_effect=self.throttle(details)):
                with self.assertRaises(AIError) as caught:
                    post('models/x:generateContent', {})
        return caught.exception

    def test_the_retry_delay_is_read(self):
        error = self.raised([{'@type': 'type.googleapis.com/google.rpc.RetryInfo',
                              'retryDelay': '27s'}])
        self.assertEqual(str(error), 'AI_RATE_LIMIT')
        self.assertEqual(error.retry_after, 27)
        self.assertFalse(error.per_day)

    def test_a_daily_quota_is_recognised(self):
        error = self.raised([{'@type': 'type.googleapis.com/google.rpc.QuotaFailure',
                              'violations': [{'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier'}]}])
        self.assertTrue(error.per_day)

    def test_a_per_minute_quota_is_not_mistaken_for_a_daily_one(self):
        error = self.raised([{'@type': 'type.googleapis.com/google.rpc.QuotaFailure',
                              'violations': [{'quotaId': 'GenerateRequestsPerMinutePerProjectPerModel-FreeTier'}]}])
        self.assertFalse(error.per_day)

    def test_the_provider_message_never_survives(self):
        """That message quotes the rejected key back."""
        error = self.raised([{'retryDelay': '5s'}])
        self.assertNotIn('AIzaSECRET', str(error))
        self.assertNotIn('Quota', str(error))

    def test_a_nonsense_delay_is_ignored_rather_than_trusted(self):
        for delay in ('not-a-delay', '99999999s', '', None, {'s': 1}):
            with self.subTest(delay=delay):
                error = self.raised([{'retryDelay': delay}])
                self.assertIn(error.retry_after, (None, 3600))

    def test_a_body_that_is_not_json_still_gives_a_rate_limit(self):
        from urllib.error import HTTPError
        from .gemini import post
        broken = HTTPError('https://x', 429, 'Too Many', {}, io.BytesIO(b'<html>nope'))
        with override_settings(AI_ENABLED=True, GEMINI_API_KEY='k'):
            with patch('exams.gemini.urlopen', side_effect=broken):
                with self.assertRaises(AIError) as caught:
                    post('models/x:generateContent', {})
        self.assertEqual(str(caught.exception), 'AI_RATE_LIMIT')
        self.assertIsNone(caught.exception.retry_after)

    def test_a_non_429_is_still_a_plain_provider_error(self):
        from urllib.error import HTTPError
        from .gemini import post
        forbidden = HTTPError('https://x', 403, 'Forbidden', {}, io.BytesIO(b'{}'))
        with override_settings(AI_ENABLED=True, GEMINI_API_KEY='k'):
            with patch('exams.gemini.urlopen', side_effect=forbidden):
                with self.assertRaises(AIError) as caught:
                    post('models/x:generateContent', {})
        self.assertEqual(str(caught.exception), 'AI_PROVIDER_ERROR')


@override_settings(MEDIA_ROOT=MEDIA, AI_ENABLED=True, GEMINI_API_KEY='k')
class DailyQuotaTests(TestCase):
    """A daily cap stops the run; it does not cost three more sleeps."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA, ignore_errors=True)
        super().tearDownClass()

    def speaking(self):
        exam = Exam.objects.create(title='S', section='Speaking', duration_seconds=900)
        for position, part in ((1, 1), (2, 2), (3, 3)):
            Question.objects.create(exam=exam, position=position, part=part,
                                    prompt=f'Prompt {position}',
                                    choices=['A point'] if part == 2 else [], accepted_answers=[])
        return exam

    def exhausted(self):
        error = AIError('AI_RATE_LIMIT')
        error.per_day = True
        error.retry_after = None
        return error

    def run_command(self, **kwargs):
        out = io.StringIO()
        kwargs.setdefault('delay', 0)
        call_command('generate_audio', stdout=out, stderr=out, **kwargs)
        return out.getvalue()

    def test_a_daily_cap_stops_at_once_without_sleeping(self):
        self.speaking()
        with patch('exams.management.commands.generate_audio.speak',
                   side_effect=self.exhausted()) as spoke, \
                patch('exams.management.commands.generate_audio.time.sleep') as slept:
            output = self.run_command(retries=5)
        self.assertEqual(spoke.call_count, 1, 'waiting cannot lift a daily cap')
        slept.assert_not_called()
        self.assertIn('kunlik limit', output.lower())

    def test_the_operator_is_told_what_to_do_tomorrow(self):
        self.speaking()
        with patch('exams.management.commands.generate_audio.speak', side_effect=self.exhausted()):
            output = self.run_command()
        self.assertIn('Ertaga', output)
        self.assertIn('davom etadi', output)

    def test_work_already_done_is_kept(self):
        exam = self.speaking()
        answers = [b'RIFFone', self.exhausted()]

        def answer(*args, **kwargs):
            result = answers.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

        with patch('exams.management.commands.generate_audio.speak', side_effect=answer):
            self.run_command()
        self.assertEqual(sum(1 for q in exam.questions.all() if q.audio_file), 1)

    def test_a_stated_retry_delay_is_used_instead_of_a_guess(self):
        self.speaking()
        error = AIError('AI_RATE_LIMIT')
        error.per_day = False
        error.retry_after = 27
        with patch('exams.management.commands.generate_audio.speak', side_effect=error), \
                patch('exams.management.commands.generate_audio.time.sleep') as slept:
            output = self.run_command(retries=1, delay=0)
        self.assertIn('32s', output)
        self.assertIn(32, [int(call.args[0]) for call in slept.call_args_list])

    def test_a_network_blip_is_retried_too(self):
        self.speaking()
        attempts = [AIError('AI_UNAVAILABLE'), b'RIFFok', b'RIFFok', b'RIFFok']

        def answer(*args, **kwargs):
            result = attempts.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

        with patch('exams.management.commands.generate_audio.speak', side_effect=answer), \
                patch('exams.management.commands.generate_audio.time.sleep'):
            self.run_command()
        exam = Exam.objects.get()
        self.assertTrue(all(q.audio_file for q in exam.questions.all()))
