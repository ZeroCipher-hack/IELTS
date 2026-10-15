"""Generated examiner audio: a real recording or a clear failure, never silence."""
import base64
import io
import shutil
import tempfile
import wave
from unittest.mock import patch

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
        with patch('exams.tts.post') as called:
            for text in ('', '   ', 'x' * 5000):
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
        with patch('exams.management.commands.generate_audio.speak', side_effect=AIError('AI_RATE_LIMIT')):
            output = self.run_command()
        self.assertIn('AI_RATE_LIMIT', output)
        self.assertIn('yaratilmadi', output)
        self.assertFalse(any(q.audio_file for q in exam.questions.all()))

    @override_settings(AI_ENABLED=False, GEMINI_API_KEY='')
    def test_without_a_key_it_refuses_instead_of_half_working(self):
        with self.assertRaises(CommandError):
            self.run_command()
