"""Admin form helpers.

The catalog stores `choices` and `accepted_answers` as JSON lists. Typing raw
JSON (`["TRUE", "FALSE"]`) in the admin is the single biggest reason adding a
question feels opaque, so these fields are edited as one value per line and
converted on the way in and out. Nothing about the stored shape changes.
"""
from django import forms
from django.core.exceptions import ValidationError

from .models import Exam, Question


class LinesWidget(forms.Textarea):
    """Renders a JSON list as one item per line."""

    def format_value(self, value):
        if isinstance(value, list):
            return '\n'.join(str(v) for v in value)
        if isinstance(value, str) and value.strip().startswith('['):
            # Django hands back the serialized JSON when a form redisplays after an error.
            import json
            try:
                parsed = json.loads(value)
            except ValueError:
                return value
            if isinstance(parsed, list):
                return '\n'.join(str(v) for v in parsed)
        return value


class LinesField(forms.JSONField):
    """One value per line, stored as a JSON list of strings."""

    widget = LinesWidget

    def to_python(self, value):
        if value in self.empty_values:
            return []
        if isinstance(value, list):
            return value
        items = [line.strip() for line in str(value).replace('\r\n', '\n').split('\n')]
        return [item for item in items if item]

    def bound_data(self, data, initial):
        return data

    def has_changed(self, initial, data):
        return self.to_python(initial) != self.to_python(data)


class QuestionForm(forms.ModelForm):
    choices = LinesField(
        required=False,
        widget=LinesWidget(attrs={'rows': 4, 'placeholder': 'TRUE\nFALSE\nNOT GIVEN'}),
        label='Variantlar',
        help_text='Har bir variant — alohida qator. Bo‘sh qoldirsangiz, savol ochiq javobli bo‘ladi '
                  '(talaba matn yozadi).',
    )
    accepted_answers = LinesField(
        required=False,
        widget=LinesWidget(attrs={'rows': 3, 'placeholder': 'TRUE'}),
        label='To‘g‘ri javob(lar)',
        help_text='Har bir to‘g‘ri javob — alohida qator. Variantlar bo‘lsa, javob aynan ulardan biri '
                  'bo‘lishi shart. Ochiq javobda bir nechta qabul qilinadigan yozilish berishingiz mumkin '
                  '(masalan: colour va color). Reading va Listening uchun majburiy.',
    )

    class Meta:
        model = Question
        fields = ['position', 'prompt', 'choices', 'accepted_answers', 'skill_tag', 'evidence', 'explanation']
        labels = {
            'position': 'Tartib raqami',
            'prompt': 'Savol matni',
            'skill_tag': 'Ko‘nikma turi',
            'evidence': 'Matndagi dalil',
            'explanation': 'Izoh (talabaga)',
        }
        help_texts = {
            'position': 'Savollar shu raqam bo‘yicha tartiblanadi. 1 dan boshlang, takrorlanmasin.',
            'prompt': 'Talaba ko‘radigan savol. Ingliz tilida yozing.',
            'skill_tag': 'Masalan: True / False / Not Given, Matching headings, Multiple choice. '
                         'Natijalar sahifasida zaif tomonlarni guruhlash uchun ishlatiladi.',
            'evidence': 'Matn yoki transkriptdan AYNAN ko‘chirilgan parcha. Natijada talabaga shu ko‘rsatiladi.',
            'explanation': 'Nega bu javob to‘g‘ri. O‘zbek tilida yozsa bo‘ladi.',
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = '__all__'
        labels = {
            'title': 'Test nomi',
            'section': 'Bo‘lim',
            'duration_seconds': 'Davomiyligi (soniya)',
            'passage': 'Matn / transkript',
            'audio_file': 'Audio fayl',
            'audio_url': 'Yoki tashqi audio havolasi',
            'published': 'Nashr qilingan',
        }
        help_texts = {
            'duration_seconds': '600 = 10 daqiqa, 3600 = 1 soat. 60 dan 14400 gacha.',
            'passage': 'Reading uchun — o‘qish matni (majburiy). Listening uchun — transkript '
                       '(ixtiyoriy, lekin dalil ko‘rsatish uchun foydali). Writing uchun — umumiy ko‘rsatma.',
        }

    def clean(self):
        data = super().clean()
        section = data.get('section')
        if section == 'Listening' and not data.get('audio_file') and not (data.get('audio_url') or '').startswith('https://'):
            raise ValidationError({'audio_file': 'Listening testi uchun audio fayl yuklang yoki HTTPS havolasi qo‘ying.'})
        if section == 'Reading' and not (data.get('passage') or '').strip():
            raise ValidationError({'passage': 'Reading testi uchun matn kerak.'})
        return data
