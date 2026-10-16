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
import shutil
import subprocess
import tempfile
import wave

from django.conf import settings

from .gemini import AIError, post

# One voice for the whole interview: a candidate must not hear the examiner
# change person between questions.
EXAMINER_VOICE = 'Kore'
SAMPLE_RATE = 24000
# One request's worth of text. A Listening transcript is several times this,
# so it is read in pieces and the audio is joined; the pieces are cut at
# paragraph and sentence boundaries so no join lands inside a sentence.
MAX_CHARS = 2400
# A whole paper, not a single request: the real ceiling on one recording.
MAX_TOTAL_CHARS = 40000


def split(text, limit=MAX_CHARS):
    """Pack `text` into as FEW request-sized pieces as the limit allows.

    Every piece is one request, and a free-tier key has very few of those, so
    packing matters: a transcript of short dialogue lines must not become one
    request per line. Paragraphs are filled up to the limit, an oversized
    paragraph is divided at sentence ends, and only a single sentence longer
    than the limit is ever cut mid-sentence.
    """
    units = []
    for block in [b.strip() for b in text.split('\n\n') if b.strip()]:
        if len(block) <= limit:
            units.append(block)
            continue
        for sentence in re.split(r'(?<=[.!?])\s+', block):
            while len(sentence) > limit:
                units.append(sentence[:limit])
                sentence = sentence[limit:]
            if sentence:
                units.append(sentence)

    pieces, current = [], ''
    for unit in units:
        joined = (current + '\n\n' + unit) if current else unit
        if len(joined) <= limit:
            current = joined
        else:
            if current:
                pieces.append(current)
            current = unit
    if current:
        pieces.append(current)
    return pieces


def _wav(pcm: bytes) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(SAMPLE_RATE)
        out.writeframes(pcm)
    return buffer.getvalue()


def speak(text, voice=EXAMINER_VOICE, style='', on_piece=None):
    """Return WAV bytes for `text`. Raises AIError; never returns silence.

    Text longer than one request is read in pieces and the audio joined.
    `on_piece(index, total)` is called before each request so a caller can
    show progress and pace itself against a rate limit.
    """
    text = (text or '').strip()
    if not text:
        raise AIError('AI_TTS_EMPTY')
    if len(text) > MAX_TOTAL_CHARS:
        raise AIError('AI_TTS_TOO_LONG')
    pieces = split(text)
    if not pieces:
        raise AIError('AI_TTS_EMPTY')
    frames = []
    for index, piece in enumerate(pieces):
        if on_piece:
            on_piece(index, len(pieces))
        frames.append(_pcm(piece, voice, style))
    return _wav(b''.join(frames))


def _pcm(text, voice, style):
    """One request: raw PCM for one piece of text."""
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
    if len(pcm) < SAMPLE_RATE // 2:
        raise AIError('AI_TTS_NO_AUDIO')
    return pcm


def compress(wav, kbps=64):
    """Return (bytes, extension): MP3 when ffmpeg is here, else the WAV.

    A 24 kHz 16-bit WAV costs 48 KB a second, so a Listening recording runs to
    tens of megabytes -- near the upload ceiling, and a cruel download for a
    candidate on mobile data. Speech at 64 kbps mono is indistinguishable here
    and roughly a tenth of the size. Falling back to WAV is fine; it only
    costs bandwidth, so a missing ffmpeg must never fail the run.
    """
    if not shutil.which('ffmpeg'):
        return wav, 'wav'
    with tempfile.TemporaryDirectory() as folder:
        source = f'{folder}/in.wav'
        target = f'{folder}/out.mp3'
        with open(source, 'wb') as handle:
            handle.write(wav)
        try:
            subprocess.run(
                ['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-i', source,
                 '-ac', '1', '-codec:a', 'libmp3lame', '-b:a', f'{int(kbps)}k', target],
                check=True, capture_output=True, timeout=600)
            with open(target, 'rb') as handle:
                data = handle.read()
        except (subprocess.SubprocessError, OSError):
            return wav, 'wav'
    # Trust the result only if it is plausible: smaller, and not empty.
    if not data.startswith((b'ID3', b'\xff\xfb', b'\xff\xf3', b'\xff\xf2')) or not 0 < len(data) < len(wav):
        return wav, 'wav'
    return data, 'mp3'
