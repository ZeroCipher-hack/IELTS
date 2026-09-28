"""Validate uploaded audio by declared type and file signature."""
from pathlib import Path

from django.core.exceptions import ValidationError


ALLOWED_MIMES = {
    '.mp3': {'audio/mpeg', 'audio/mp3'},
    '.wav': {'audio/wav', 'audio/x-wav', 'audio/wave'},
    '.ogg': {'audio/ogg', 'application/ogg'},
    '.m4a': {'audio/mp4', 'audio/x-m4a'},
    '.webm': {'audio/webm', 'video/webm'},
}


def validate_audio_upload(value):
    if value.size > 20 * 1024 * 1024:
        raise ValidationError('Audio fayl 20 MB dan oshmasin.')
    extension = Path(value.name).suffix.lower()
    mime = getattr(value, 'content_type', None)
    if extension not in ALLOWED_MIMES or (mime and mime.lower() not in ALLOWED_MIMES[extension]):
        raise ValidationError('Audio formati qo‘llab-quvvatlanmaydi.')
    value.open('rb')
    position = value.tell()
    try:
        header = value.read(16)
    finally:
        value.seek(position)
    valid = {
        '.mp3': header.startswith(b'ID3') or (len(header) >= 2 and header[0] == 0xff and header[1] & 0xe0 == 0xe0),
        '.wav': header.startswith(b'RIFF') and header[8:12] == b'WAVE',
        '.ogg': header.startswith(b'OggS'),
        '.m4a': header[4:8] == b'ftyp',
        '.webm': header.startswith(b'\x1aE\xdf\xa3'),
    }
    if not valid[extension]:
        raise ValidationError('Audio fayl sarlavhasi noto‘g‘ri.')
