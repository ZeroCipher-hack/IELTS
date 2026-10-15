"""Server-side examiner speech, so the exam never depends on browser voices.

The runner used to fall back to the Web Speech API when a question carried no
recording. That fallback is unreliable by design: getVoices() is asynchronous,
and a Linux browser commonly ships no English voice at all, leaving the
candidate staring at a silent screen. Audio generated here is stored on the
question and simply played, which works on every device.

Output is 24 kHz mono 16-bit PCM wrapped in a WAV container -- what the Gemini
TTS models return. No credential, prompt or provider message is logged.
"""
import base64
import io
import re
import wave

from django.conf import settings

from .gemini import AIError, post

# One voice for the whole interview: a candidate must not hear the examiner
# change person between questions.
EXAMINER_VOICE = 'Kore'
SAMPLE_RATE = 24000
MAX_CHARS = 4500


def _wav(pcm: bytes) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(SAMPLE_RATE)
        out.writeframes(pcm)
    return buffer.getvalue()


def speak(text, voice=EXAMINER_VOICE, style=''):
    """Return WAV bytes for `text`. Raises AIError; never returns silence."""
    text = (text or '').strip()
    if not text:
        raise AIError('AI_TTS_EMPTY')
    if len(text) > MAX_CHARS:
        raise AIError('AI_TTS_TOO_LONG')
    model = settings.GEMINI_TTS_MODEL
    if not re.fullmatch(r'[A-Za-z0-9._-]+', model):
        raise AIError('AI_MODEL_INVALID')
    if not re.fullmatch(r'[A-Za-z]+', voice):
        raise AIError('AI_TTS_VOICE_INVALID')

    data = post(f'models/{model}:generateContent', {
        'contents': [{'role': 'user', 'parts': [{'text': (style + text) if style else text}]}],
        'generationConfig': {
            'responseModalities': ['AUDIO'],
            'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice}}},
        },
    }, limit=settings.EXAM_AUDIO_MAX_BYTES * 2, timeout=240)
    try:
        part = data['candidates'][0]['content']['parts'][0]
        encoded = part['inlineData']['data']
        mime = str(part['inlineData'].get('mimeType', ''))
    except (KeyError, IndexError, TypeError):
        raise AIError('AI_TTS_NO_AUDIO') from None
    if 'audio/' not in mime:
        raise AIError('AI_TTS_NO_AUDIO')
    try:
        pcm = base64.b64decode(encoded, validate=True)
    except Exception:
        raise AIError('AI_TTS_NO_AUDIO') from None
    # Two bytes a frame; a fraction of a second is a failure, not a recording.
    if len(pcm) < SAMPLE_RATE:
        raise AIError('AI_TTS_NO_AUDIO')
    return _wav(pcm)
