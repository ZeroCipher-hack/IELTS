"""Uploaded audio must be audio rather than renamed HTML."""
import io
import wave

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from .validators import validate_audio_upload


class AudioUploadTests(SimpleTestCase):
    def test_rejects_renamed_html_and_wrong_mime(self):
        with self.assertRaises(ValidationError):
            validate_audio_upload(SimpleUploadedFile('script.mp3', b'<html><script>alert(1)</script>', content_type='audio/mpeg'))
        with self.assertRaises(ValidationError):
            validate_audio_upload(SimpleUploadedFile('clip.wav', b'RIFF1234WAVEfmt ', content_type='text/html'))

    def test_accepts_real_wave_file_and_restores_position(self):
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(16000)
            output.writeframes(b'\0' * 512)
        audio = SimpleUploadedFile('clip.wav', buffer.getvalue(), content_type='audio/wav')
        validate_audio_upload(audio)
        self.assertEqual(audio.tell(), 0)
