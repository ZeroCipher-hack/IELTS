"""Create original demonstration exams. Never overwrites existing content.

Reading and Writing are published immediately. Listening is created as a DRAFT
on purpose: a Listening test cannot be published without audio, and the audio
recording has to be supplied by a person. Upload it in the admin, then run the
"Tekshirish va nashr qilish" action.
"""
from django.core.management.base import BaseCommand
from exams.models import Exam, Question

READING_TITLE = 'Urban gardens — original demo'
READING_PASSAGE = (
    'Urban gardens can be found on rooftops and school grounds. Residents manage many gardens '
    'together. A study of twelve gardens found that participants valued social contact as much as '
    'fresh vegetables. It did not compare the cost of garden produce with supermarket prices. Some '
    'gardens collect rainwater, but still need additional water during long dry periods. Gardens '
    'alone cannot feed an entire city.'
)
READING_ITEMS = [
    ('Urban gardens can be located on rooftops.', ['TRUE'],
     'Urban gardens can be found on rooftops and school grounds.',
     'Matnda tomlar aniq keltirilgan.'),
    ('Participants only valued vegetables.', ['FALSE'],
     'Participants valued social contact as much as fresh vegetables.',
     'Ijtimoiy aloqani ham qadrlashgan.'),
    ('Garden produce is cheaper than supermarket food.', ['NOT GIVEN'],
     'It did not compare the cost of garden produce with supermarket prices.',
     'Narxlar taqqoslanmagan.'),
    ('Gardens with rainwater tanks never need additional water.', ['FALSE'],
     'Still need additional water during long dry periods.',
     'Qo‘shimcha suv talab qilinadi.'),
    ('Gardens alone can feed an entire city.', ['FALSE'],
     'Gardens alone cannot feed an entire city.',
     'Da’vo matnga zid.'),
]

LISTENING_TITLE = 'Campus library tour — original demo'
LISTENING_PASSAGE = (
    'TRANSKRIPT\n\n'
    'Welcome to the campus library. The building opens at eight in the morning on weekdays and '
    'closes at ten in the evening. On Saturdays we close early, at five. The ground floor is the '
    'only place where you may talk, so group work happens there. Floors two and three are silent '
    'study areas.\n\n'
    'You can borrow up to six books at a time with a student card. Books are kept for three weeks, '
    'and you may renew them online twice unless another student has reserved the title. There is no '
    'charge for a late return, but your borrowing is suspended until the book comes back.\n\n'
    'The printing room is next to the main entrance. Printing costs ten cents a page in black and '
    'white. Finally, the library runs a free referencing workshop every Tuesday afternoon; you do '
    'not need to book a place.'
)
LISTENING_ITEMS = [
    ('The library closes at ten in the evening on weekdays.', ['TRUE', 'FALSE', 'NOT GIVEN'], ['TRUE'],
     'The building opens at eight in the morning on weekdays and closes at ten in the evening.',
     'Transkriptda ish kunlari uchun soat 10 aniq aytilgan.', 'True / False / Not Given'),
    ('Students may talk on the second floor.', ['TRUE', 'FALSE', 'NOT GIVEN'], ['FALSE'],
     'Floors two and three are silent study areas.',
     'Ikkinchi va uchinchi qavat — sukunat zonasi.', 'True / False / Not Given'),
    ('The library charges a fee for returning a book late.', ['TRUE', 'FALSE', 'NOT GIVEN'], ['FALSE'],
     'There is no charge for a late return, but your borrowing is suspended until the book comes back.',
     'Jarima yo‘q, lekin kitob olish to‘xtatiladi.', 'True / False / Not Given'),
    ('The library is busier during examination weeks.', ['TRUE', 'FALSE', 'NOT GIVEN'], ['NOT GIVEN'],
     '',
     'Transkriptda imtihon haftalari haqida hech narsa aytilmagan.', 'True / False / Not Given'),
    ('How many books can a student borrow at one time?', [], ['6', 'six'],
     'You can borrow up to six books at a time with a student card.',
     'Son bilan ham, so‘z bilan ham yozish qabul qilinadi.', 'Short answer'),
    ('On which day does the referencing workshop take place?', [], ['Tuesday'],
     'the library runs a free referencing workshop every Tuesday afternoon',
     'Hafta kuni transkriptdan olinadi.', 'Short answer'),
]

WRITING_TITLE = 'Academic Writing — original demo'
WRITING_PASSAGE = (
    'Ikkala topshiriqni ham bajaring. Task 2 bahoda ikki barobar og‘irroq hisoblanadi.\n'
    'Vaqt taqsimoti tavsiyasi: Task 1 uchun 20 daqiqa, Task 2 uchun 40 daqiqa.'
)
WRITING_ITEMS = [
    ('Task 1: The chart below shows the number of students who used the campus library each month '
     'during one academic year. Summarise the information by selecting and reporting the main '
     'features, and make comparisons where relevant. Write at least 150 words.',
     'Task 1'),
    ('Task 2: Some people believe that students learn more from working in groups, while others '
     'think independent study is more effective. Discuss both views and give your own opinion. '
     'Write at least 250 words.',
     'Task 2'),
]


class Command(BaseCommand):
    help = 'Create original demo exams for Reading, Listening and Writing; never overwrite existing content.'

    def handle(self, *args, **options):
        self.seed_reading()
        self.seed_listening()
        self.seed_writing()

    def seed_reading(self):
        if Exam.objects.filter(title=READING_TITLE).exists():
            self.stdout.write('Reading: allaqachon mavjud.')
            return
        exam = Exam.objects.create(title=READING_TITLE, section='Reading', duration_seconds=600,
                                   passage=READING_PASSAGE)
        for i, (prompt, answers, evidence, explanation) in enumerate(READING_ITEMS, 1):
            Question.objects.create(exam=exam, position=i, prompt=prompt,
                                    choices=['TRUE', 'FALSE', 'NOT GIVEN'], accepted_answers=answers,
                                    evidence=evidence, explanation=explanation,
                                    skill_tag='True / False / Not Given')
        exam.published = True
        exam.save()
        self.stdout.write(self.style.SUCCESS('Reading: yaratildi va nashr qilindi.'))

    def seed_listening(self):
        if Exam.objects.filter(title=LISTENING_TITLE).exists():
            self.stdout.write('Listening: allaqachon mavjud.')
            return
        exam = Exam.objects.create(title=LISTENING_TITLE, section='Listening', duration_seconds=900,
                                   passage=LISTENING_PASSAGE)
        for i, (prompt, choices, answers, evidence, explanation, tag) in enumerate(LISTENING_ITEMS, 1):
            Question.objects.create(exam=exam, position=i, prompt=prompt, choices=choices,
                                    accepted_answers=answers, evidence=evidence,
                                    explanation=explanation, skill_tag=tag)
        self.stdout.write(self.style.WARNING(
            'Listening: QORALAMA yaratildi (savollar va transkript tayyor).\n'
            '  Audio yo‘q, shuning uchun nashr qilinmadi. Admin panelda testni oching, '
            '«Audio fayl» maydoniga yozuvni yuklang, so‘ng ro‘yxatdan «Tekshirish va nashr qilish» '
            'amalini ishlating.'))

    def seed_writing(self):
        if Exam.objects.filter(title=WRITING_TITLE).exists():
            self.stdout.write('Writing: allaqachon mavjud.')
            return
        exam = Exam.objects.create(title=WRITING_TITLE, section='Writing', duration_seconds=3600,
                                   passage=WRITING_PASSAGE)
        for i, (prompt, tag) in enumerate(WRITING_ITEMS, 1):
            Question.objects.create(exam=exam, position=i, prompt=prompt, choices=[],
                                    accepted_answers=[], evidence='', explanation='', skill_tag=tag)
        exam.published = True
        exam.save()
        self.stdout.write(self.style.SUCCESS(
            'Writing: yaratildi va nashr qilindi. Baho AI ulanganda chiqadi (GEMINI_API_KEY + AI_ENABLED=1).'))
