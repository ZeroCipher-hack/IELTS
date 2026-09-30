from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase, override_settings
from django.urls import path

from .media import serve_audio

urlpatterns = [path('media/exam_audio/<path:path>', serve_audio)]


class DevelopmentAudioTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.folder = self.root / 'exam_audio'
        self.folder.mkdir()
        self.audio = self.folder / 'sample.wav'
        self.audio.write_bytes(b'RIFFabcdWAVE' + b'0123456789')
        override = override_settings(MEDIA_ROOT=self.root, ROOT_URLCONF=__name__, DEBUG=True)
        override.enable()
        self.addCleanup(override.disable)

    def test_full_and_range_audio_responses(self):
        url = '/media/exam_audio/sample.wav'
        full = self.client.get(url)
        self.assertEqual(full.status_code, 200)
        self.assertEqual(full['Content-Type'], 'audio/wav')
        self.assertEqual(full['Accept-Ranges'], 'bytes')
        self.assertEqual(full['X-Content-Type-Options'], 'nosniff')
        self.assertIn('inline', full['Content-Disposition'])
        self.assertEqual(b''.join(full.streaming_content), self.audio.read_bytes())
        part = self.client.get(url, HTTP_RANGE='bytes=0-3')
        self.assertEqual(part.status_code, 206)
        self.assertEqual(part['Content-Range'], f'bytes 0-3/{self.audio.stat().st_size}')
        self.assertEqual(part['Content-Length'], '4')
        self.assertEqual(b''.join(part.streaming_content), b'RIFF')
        suffix = self.client.get(url, HTTP_RANGE='bytes=-4')
        self.assertEqual(b''.join(suffix.streaming_content), b'6789')
        self.assertEqual(self.client.head(url, HTTP_RANGE='bytes=0-3').status_code, 206)

    def test_invalid_range_and_unsafe_files(self):
        invalid = self.client.get('/media/exam_audio/sample.wav', HTTP_RANGE='bytes=999-')
        self.assertEqual(invalid.status_code, 416)
        self.assertEqual(invalid['Content-Range'], f'bytes */{self.audio.stat().st_size}')
        self.assertEqual(self.client.get('/media/exam_audio/sample.wav', HTTP_RANGE='bytes=0-1,5-6').status_code, 416)
        (self.folder / 'page.html').write_text('<script>alert(1)</script>')
        self.assertEqual(self.client.get('/media/exam_audio/page.html').status_code, 404)
        (self.folder / 'escape.wav').symlink_to(self.root / 'other.wav')
        (self.root / 'other.wav').write_bytes(b'RIFF')
        self.assertEqual(self.client.get('/media/exam_audio/escape.wav').status_code, 404)
