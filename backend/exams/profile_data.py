"""Validate optional contact details and normalize small, private avatars."""
import base64
import binascii
import io
import re
from PIL import Image, ImageOps, UnidentifiedImageError


def profile_fields(data):
    cleaned = {}
    for key, limit in [('phone', 24), ('city', 80), ('institution', 160)]:
        if key not in data:
            continue
        value = data[key]
        if not isinstance(value, str) or len(value) > limit:
            raise ValueError(f'{key}: qiymat juda uzun yoki noto‘g‘ri.')
        value = value.strip()
        if key == 'phone' and value:
            value = re.sub(r'[\s()\-]', '', value)
            if not re.fullmatch(r'\+[1-9][0-9]{7,14}', value):
                raise ValueError('Telefonni davlat kodi bilan kiriting: +998901234567.')
        cleaned[key] = value
    if 'learner_type' in data:
        if data['learner_type'] not in ('', 'school', 'university', 'learning_center', 'independent'):
            raise ValueError('O‘quvchi turi noto‘g‘ri.')
        cleaned['learner_type'] = data['learner_type']
    if 'avatar' in data:
        cleaned['avatar'] = normalize_avatar(data['avatar'])
    return cleaned


def normalize_avatar(value):
    if value == '':
        return ''
    if not isinstance(value, str) or len(value) > 350000:
        raise ValueError('Avatar hajmi juda katta.')
    if not re.match(r'^data:image/(jpeg|png|webp);base64,', value):
        raise ValueError('JPG, PNG yoki WebP rasm tanlang.')
    try:
        raw = base64.b64decode(value.split(',', 1)[1], validate=True)
        with Image.open(io.BytesIO(raw)) as source:
            if source.format not in ('JPEG', 'PNG', 'WEBP') or max(source.size) > 2048:
                raise ValueError('Avatar o‘lchami juda katta yoki turi noto‘g‘ri.')
            source.load()
            image = ImageOps.fit(ImageOps.exif_transpose(source).convert('RGB'), (256, 256))
            # Copy pixels into a fresh image to discard metadata before persistence.
            clean = Image.new('RGB', image.size)
            clean.paste(image)
            output = io.BytesIO()
            clean.save(output, format='JPEG', quality=85)
        return 'data:image/jpeg;base64,' + base64.b64encode(output.getvalue()).decode('ascii')
    except (binascii.Error, OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise ValueError('Rasmni o‘qib bo‘lmadi. Boshqa rasm tanlang.') from exc
