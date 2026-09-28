"""Local development audio delivery with single-byte-range support."""
import re
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django.utils.http import content_disposition_header, http_date
from django.views.decorators.http import require_http_methods


AUDIO_TYPES = {
    '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.ogg': 'audio/ogg',
    '.m4a': 'audio/mp4', '.webm': 'audio/webm',
}


def chunks(path, start, length):
    with path.open('rb') as source:
        source.seek(start)
        while length:
            block = source.read(min(length, 64 * 1024))
            if not block:
                break
            length -= len(block)
            yield block


def unsatisfiable(size):
    response = HttpResponse(status=416)
    response['Content-Range'] = f'bytes */{size}'
    response['Accept-Ranges'] = 'bytes'
    response['X-Content-Type-Options'] = 'nosniff'
    return response


@require_http_methods(['GET', 'HEAD'])
def serve_audio(request, path):
    root = Path(settings.MEDIA_ROOT).resolve()
    filename = (root / 'exam_audio' / path).resolve()
    if not filename.is_relative_to(root / 'exam_audio') or filename.suffix.lower() not in AUDIO_TYPES or not filename.is_file():
        raise Http404('Audio not found.')
    size = filename.stat().st_size
    modified = http_date(filename.stat().st_mtime)
    requested = request.headers.get('Range')
    if request.headers.get('If-Range') and request.headers['If-Range'] != modified:
        requested = None
    start, end = 0, size - 1
    if requested:
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested.strip())
        if not match or size == 0 or not any(match.groups()):
            return unsatisfiable(size)
        first, last = match.groups()
        if first:
            start = int(first)
            end = min(int(last), end) if last else end
        else:
            start = max(0, size - int(last))
        if start >= size or start > end or (not first and int(last) == 0):
            return unsatisfiable(size)
    status = 206 if requested else 200
    if request.method == 'HEAD':
        response = HttpResponse(status=status, content_type=AUDIO_TYPES[filename.suffix.lower()])
    elif requested:
        response = StreamingHttpResponse(chunks(filename, start, end - start + 1), status=status,
                                         content_type=AUDIO_TYPES[filename.suffix.lower()])
    else:
        response = FileResponse(filename.open('rb'), content_type=AUDIO_TYPES[filename.suffix.lower()])
    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = end - start + 1 if requested else size
    response['Last-Modified'] = modified
    response['Content-Disposition'] = content_disposition_header(False, filename.name)
    response['X-Content-Type-Options'] = 'nosniff'
    if requested:
        response['Content-Range'] = f'bytes {start}-{end}/{size}'
    return response
