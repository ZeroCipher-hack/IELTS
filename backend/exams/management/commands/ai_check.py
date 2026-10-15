"""Diagnose the Gemini connection without ever printing the credential.

The transport in exams.gemini deliberately collapses every provider failure
into AI_PROVIDER_ERROR so nothing leaks into application logs. That is right
for request handling and useless for setup, where the operator needs to know
WHICH thing is wrong. This command talks to Google directly and reports only
the HTTP status and Google's own error enum (a fixed vocabulary such as
PERMISSION_DENIED or RESOURCE_EXHAUSTED) -- never the key, never the body.
"""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand

ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/'

REASONS = {
    400: 'So‘rov rad etildi. Ko‘p hollarda kalit noto‘g‘ri ko‘chirilgan (bo‘shliq, yarmi tushib qolgan).',
    401: 'Kalit tanilmadi. Google AI Studio’da yangi kalit oling.',
    403: 'Kalitga ruxsat yo‘q: o‘chirilgan, cheklangan yoki bu model uchun yaroqsiz.',
    404: 'Model topilmadi. GEMINI_WRITING_MODEL nomini tekshiring.',
    429: 'Bepul limit tugagan. Bir necha daqiqa kutib qayta urinib ko‘ring.',
    500: 'Google tomonida vaqtinchalik xato. Qayta urinib ko‘ring.',
    503: 'Google tomonida band. Qayta urinib ko‘ring.',
}


def call(path, data=None):
    """Return (payload, None) or (None, human_reason). Raises nothing."""
    request = Request(
        ENDPOINT + path,
        data=json.dumps(data).encode() if data is not None else None,
        headers={'Content-Type': 'application/json', 'x-goog-api-key': settings.GEMINI_API_KEY},
        method='POST' if data is not None else 'GET',
    )
    try:
        with urlopen(request, timeout=45) as response:
            return json.loads(response.read(2 * 1024 * 1024)), None
    except HTTPError as exc:
        status = ''
        try:
            body = json.loads(exc.read(64 * 1024))
            value = body.get('error', {}).get('status')
            if isinstance(value, str) and value.isascii() and value.replace('_', '').isalpha():
                status = value
        except Exception:
            pass
        reason = REASONS.get(exc.code, 'Google kutilmagan javob qaytardi.')
        return None, f'HTTP {exc.code}{" " + status if status else ""} — {reason}'
    except (URLError, TimeoutError, OSError) as exc:
        return None, f'Tarmoqqa chiqa olmadim ({type(exc).__name__}). Internet yoki proksini tekshiring.'
    except ValueError:
        return None, 'Javob JSON emas edi.'


class Command(BaseCommand):
    help = 'Check that AI_ENABLED, GEMINI_API_KEY and the configured model actually work. Prints no secrets.'

    def add_arguments(self, parser):
        parser.add_argument('--offline', action='store_true',
                            help='Only check local configuration; do not contact Google.')

    def handle(self, *args, **options):
        ok = self.style.SUCCESS
        bad = self.style.ERROR
        warn = self.style.WARNING
        model = settings.GEMINI_WRITING_MODEL

        self.stdout.write('1. Mahalliy sozlama')
        self.stdout.write(f'   AI_ENABLED      : {ok("1 (yoqilgan)") if settings.AI_ENABLED else bad("0 (o‘chirilgan)")}')
        self.stdout.write(f'   GEMINI_API_KEY  : {ok("o‘rnatilgan") if settings.GEMINI_API_KEY else bad("YO‘Q")}')
        self.stdout.write(f'   Writing modeli  : {model}')
        self.stdout.write(f'   Ovozli mashq    : {"yoqilgan" if settings.VOICE_PRACTICE_ENABLED else "o‘chirilgan (imtihon uchun kerak emas)"}')

        if not settings.AI_ENABLED or not settings.GEMINI_API_KEY:
            self.stdout.write(bad('\nTo‘xtadi: backend/.env faylida AI_ENABLED=1 va GEMINI_API_KEY=... bo‘lishi kerak.'))
            self.stdout.write('Keyin shu buyruqni qayta ishlating. Kalitning o‘zi hech qachon ekranga chiqmaydi.')
            return
        if options['offline']:
            self.stdout.write(ok('\nMahalliy sozlama joyida. Google bilan aloqa tekshirilmadi (--offline).'))
            return

        self.stdout.write('\n2. Kalit va modellar ro‘yxati')
        payload, reason = call('models')
        if reason:
            self.stdout.write(bad(f'   XATO: {reason}'))
            return
        listed = payload.get('models') or []
        names, usable = [], []
        for entry in listed:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get('name', '')).removeprefix('models/')
            if not name:
                continue
            names.append(name)
            if 'generateContent' in (entry.get('supportedGenerationMethods') or []):
                usable.append(name)
        usable.sort()
        self.stdout.write(ok(f'   Kalit ishlayapti. {len(names)} model ko‘rinadi.'))
        if model in names:
            self.stdout.write(ok(f'   «{model}» ro‘yxatda bor.'))
        else:
            self.stdout.write(bad(f'   «{model}» ro‘yxatda YO‘Q.'))
            self.stdout.write('   Mavjudlaridan birini tanlang (.env da GEMINI_WRITING_MODEL=...):')
            for name in usable[:12]:
                self.stdout.write(f'     - {name}')
            return

        self.stdout.write('\n3. Haqiqiy baholash so‘rovi')
        payload, reason = call(f'models/{model}:generateContent', {
            'contents': [{'role': 'user', 'parts': [{'text': 'Return JSON only: {"ok": true}'}]}],
            'generationConfig': {'responseMimeType': 'application/json', 'maxOutputTokens': 400,
                                 'responseSchema': {'type': 'OBJECT', 'properties': {'ok': {'type': 'BOOLEAN'}},
                                                    'required': ['ok']}},
        })
        if reason:
            self.stdout.write(bad(f'   XATO: {reason}'))
            return
        try:
            text = payload['candidates'][0]['content']['parts'][0]['text']
            answered = json.loads(text).get('ok') is True
        except Exception:
            answered = False
        if not answered:
            self.stdout.write(warn('   Javob keldi, lekin kutilgan JSON emas. Model nomini tekshiring.'))
            return

        self.stdout.write(ok('   Model javob berdi va JSON sxemasiga bo‘ysundi.'))
        self.stdout.write(ok('\nHammasi tayyor. Endi baholash ishchisini ishga tushiring:'))
        self.stdout.write('   .venv/bin/python manage.py assess_pending --watch')
