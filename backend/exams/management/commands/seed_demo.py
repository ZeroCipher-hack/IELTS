from pathlib import Path
import shutil
import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from exams.models import Attempt, Exam, Question
from exams.services import validate_exam

LISTENING_SCRIPT = (
    "Good morning, everyone. Here are the details for Saturday's City History Walk. "
    "Please meet at the east entrance of the museum at quarter past nine. The coach leaves at half past nine, so arrive early. "
    "The walk costs eighteen pounds, including a packed lunch. Vegetarian lunches are available, but tell the office by Thursday. "
    "Bring a notebook and a waterproof jacket. The forecast says light rain in the afternoon. "
    "We expect to return to the museum at four o'clock. If you are delayed, call the coordinator, Ms Patel, on 01632 960 418. "
    "The group will visit the old station first, then the riverside market, and finally the clock tower. "
    "Please do not take photographs inside the archive room."
)

EXAMS = [
    {
        "title": "Urban gardens — original demo",
        "section": "Reading",
        "duration_seconds": 600,
        "passage": (
            "Urban gardens can be found on rooftops and school grounds. Residents manage many gardens together. "
            "A study of twelve gardens found that participants valued social contact as much as fresh vegetables. "
            "It did not compare the cost of garden produce with supermarket prices. Some gardens collect rainwater, "
            "but still need additional water during long dry periods. Gardens alone cannot feed an entire city."
        ),
        "questions": [
            ("Urban gardens can be located on rooftops.", ["TRUE", "FALSE", "NOT GIVEN"], ["TRUE"], "Urban gardens can be found on rooftops and school grounds.", "Matnda tomlar aniq keltirilgan.", "True / False / Not Given"),
            ("Participants only valued vegetables.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"], "Participants valued social contact as much as fresh vegetables.", "Ijtimoiy aloqani ham qadrlashgan.", "True / False / Not Given"),
            ("Garden produce is cheaper than supermarket food.", ["TRUE", "FALSE", "NOT GIVEN"], ["NOT GIVEN"], "It did not compare the cost of garden produce with supermarket prices.", "Narxlar taqqoslanmagan.", "True / False / Not Given"),
            ("Gardens with rainwater tanks never need additional water.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"], "Still need additional water during long dry periods.", "Qo‘shimcha suv talab qilinadi.", "True / False / Not Given"),
            ("Gardens alone can feed an entire city.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"], "Gardens alone cannot feed an entire city.", "Da’vo matnga zid.", "True / False / Not Given"),
        ],
    },
    {
        "title": "City History Walk — Listening practice",
        "section": "Listening",
        "duration_seconds": 480,
        "passage": LISTENING_SCRIPT,
        "audio_url": "browser-tts://passage",
        "questions": [
            ("Where should participants meet?", ["West entrance", "East entrance", "Main station"], ["East entrance"], LISTENING_SCRIPT, "Muzeyning sharqiy kirish joyi aytiladi.", "Multiple choice"),
            ("What time should participants meet?", ["9:00", "9:15", "9:30"], ["9:15"], LISTENING_SCRIPT, "“Quarter past nine” — 9:15.", "Multiple choice"),
            ("How much does the walk cost?", ["£16", "£18", "£20"], ["£18"], LISTENING_SCRIPT, "Narxi eighteen pounds.", "Multiple choice"),
            ("By which day must a vegetarian lunch be requested?", ["Wednesday", "Thursday", "Friday"], ["Thursday"], LISTENING_SCRIPT, "Ofisga payshanbagacha xabar berish kerak.", "Multiple choice"),
            ("What should participants bring because of the forecast?", ["A waterproof jacket", "A camera", "A map"], ["A waterproof jacket"], LISTENING_SCRIPT, "Yengil yomg‘ir kutilgani uchun suv o‘tkazmaydigan kurtka kerak.", "Multiple choice"),
            ("At what time is the group expected back?", ["3:30", "4:00", "4:30"], ["4:00"], LISTENING_SCRIPT, "Qaytish vaqti four o'clock.", "Multiple choice"),
            ("Who is the coordinator?", ["Ms Patel", "Mr Peters", "Ms Parker"], ["Ms Patel"], LISTENING_SCRIPT, "Muvofiqlashtiruvchi Ms Patel.", "Multiple choice"),
            ("Which place will the group visit first?", ["Riverside market", "Clock tower", "Old station"], ["Old station"], LISTENING_SCRIPT, "Birinchi manzil — eski vokzal.", "Multiple choice"),
        ],
    },
    {
        "title": "Community Libraries — Reading practice",
        "section": "Reading",
        "duration_seconds": 600,
        "passage": (
            "In the town of Westbridge, the central library began a mobile service in 2018. A small electric vehicle visits "
            "six neighbourhood stops every Tuesday and Friday. The service was designed for residents who live far from the "
            "town centre, including older people and families with young children. The vehicle carries about 900 books, "
            "although readers can reserve titles from the larger central collection. Reservations usually arrive on the next visit. "
            "The council funded the vehicle, while local volunteers help visitors choose books and use the online catalogue. "
            "During its first year, the service recorded 2,400 visits. This figure counts visits rather than individual readers, "
            "because some people came more than once. A later survey found that many users appreciated the regular schedule. "
            "It did not ask whether the service had increased reading among children. The library plans to add a seventh stop "
            "next year, but only if a suitable covered parking space can be found."
        ),
        "questions": [
            ("The mobile library began operating in 2018.", ["TRUE", "FALSE", "NOT GIVEN"], ["TRUE"], "The central library began a mobile service in 2018.", "Boshlanish sanasi matnda berilgan.", "True / False / Not Given"),
            ("The vehicle visits the neighbourhoods every weekday.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"], "A small electric vehicle visits six neighbourhood stops every Tuesday and Friday.", "Faqat seshanba va juma kunlari boradi.", "True / False / Not Given"),
            ("The vehicle carries more than 1,000 books.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"], "The vehicle carries about 900 books.", "Taxminan 900 ta kitob.", "True / False / Not Given"),
            ("Readers may reserve books from the central collection.", ["TRUE", "FALSE", "NOT GIVEN"], ["TRUE"], "Readers can reserve titles from the larger central collection.", "Markaziy fondan kitob band qilish mumkin.", "True / False / Not Given"),
            ("The council pays the volunteers a salary.", ["TRUE", "FALSE", "NOT GIVEN"], ["NOT GIVEN"], "Local volunteers help visitors choose books.", "Maosh haqida ma’lumot yo‘q.", "True / False / Not Given"),
            ("The first-year figure counts individual readers.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"], "This figure counts visits rather than individual readers.", "Hisob tashriflar bo‘yicha yuritilgan.", "True / False / Not Given"),
            ("The survey proved that children read more because of the service.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"], "It did not ask whether the service had increased reading among children.", "So‘rov bolalar o‘qishi oshganini tekshirmagan.", "True / False / Not Given"),
            ("A seventh stop depends on finding covered parking.", ["TRUE", "FALSE", "NOT GIVEN"], ["TRUE"], "Only if a suitable covered parking space can be found.", "Yopiq turargoh topilishiga bog‘liq.", "True / False / Not Given"),
        ],
    },
    {
        "title": "Coastal Wetlands — Reading evidence practice",
        "section": "Reading",
        "duration_seconds": 900,
        "passage": (
            "In 2019, the coastal town of Harbridge began restoring a wetland beside its old harbour. "
            "For decades, the site had been used for storing construction materials. The council removed waste and "
            "opened two shallow channels so that tidal water could return. Volunteers planted native reeds, "
            "but scientists allowed other plants to grow naturally. By 2022, surveys recorded 34 bird species "
            "at the site, compared with 19 before the work began. These numbers count species observed during "
            "survey visits, not the total number of individual birds. The restoration cost 1.2 million pounds; "
            "a regional environmental fund paid half, and the council paid the rest. "
            "An elevated wooden path now lets visitors see the wetland without walking through nesting areas. "
            "The path closes for two weeks each spring to reduce disturbance. A local school uses the site "
            "for science lessons, although the researchers have not measured any change in pupils' exam scores. "
            "The team hopes the wetland will reduce flooding nearby, but it has not yet collected enough data "
            "to confirm that effect. Next year, the council plans to test water quality every month."
        ),
        "questions": [
            ("The wetland had once stored building materials.", ["TRUE", "FALSE", "NOT GIVEN"], ["TRUE"],
             "For decades, the site had been used for storing construction materials.",
             "Matnda qurilish materiallari saqlangani bevosita aytilgan.", "True / False / Not Given"),
            ("The council planted every species now growing at the site.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"],
             "Volunteers planted native reeds, but scientists allowed other plants to grow naturally.",
             "Boshqa o‘simliklar tabiiy o‘sgan, hammasi ekilmagan.", "True / False / Not Given"),
            ("The surveys counted 34 individual birds in 2022.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"],
             "These numbers count species observed during survey visits, not the total number of individual birds.",
             "34 soni qush turlarini bildiradi, alohida qushlarni emas.", "True / False / Not Given"),
            ("The council paid the whole restoration cost.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"],
             "A regional environmental fund paid half, and the council paid the rest.",
             "Xarajatning yarmini hududiy jamg‘arma to‘lagan.", "True / False / Not Given"),
            ("The wooden path stays open throughout spring.", ["TRUE", "FALSE", "NOT GIVEN"], ["FALSE"],
             "The path closes for two weeks each spring to reduce disturbance.",
             "Yo‘lak bahorda ikki haftaga yopiladi.", "True / False / Not Given"),
            ("Science lessons improved pupils' exam scores.", ["TRUE", "FALSE", "NOT GIVEN"], ["NOT GIVEN"],
             "The researchers have not measured any change in pupils' exam scores.",
             "Baholar o‘zgargani o‘lchanmagan, natija aytilmagan.", "True / False / Not Given"),
            ("What fraction of the restoration cost did the regional fund pay?", [], ["half", "one half", "50%"],
             "A regional environmental fund paid half, and the council paid the rest.",
             "Jamg‘arma xarajatning yarmini qoplagan.", "Short answer"),
            ("How often will water quality be tested next year?", [], ["every month", "monthly"],
             "Next year, the council plans to test water quality every month.",
             "Suv sifati har oy tekshiriladi.", "Short answer"),
        ],
    },
    {
        "title": "Public Transport Trends — Writing Task 1 + Task 2 practice",
        "section": "Writing",
        "duration_seconds": 3600,
        "passage": "",
        "questions": [
            (
                "The table below shows the percentage of commuters in Westbridge who used three forms of transport in 2010 and 2020. "
                "Summarise the information by selecting and reporting the main features, and make comparisons where relevant. "
                "Write at least 150 words.\n\n"
                "Transport mode | 2010 | 2020\n"
                "Car | 62% | 45%\n"
                "Bus | 24% | 32%\n"
                "Bicycle | 14% | 23%",
                [],
                [],
                "",
                "",
                "Writing Task 1",
            ),
            (
                "Some people think city governments should make public transport free to reduce traffic and pollution. "
                "Others believe passengers should pay the full cost of their journeys. Discuss both views and give your own opinion. "
                "Write at least 250 words.",
                [],
                [],
                "",
                "",
                "Writing Task 2",
            ),
        ],
    },
]

def attach_demo_audio(exam, stdout):
    """Prefer a real local WAV for the unmodified Listening demo."""
    if exam.audio_file or exam.audio_url not in ('', 'browser-tts://passage') or exam.passage != LISTENING_SCRIPT:
        return False
    name = 'exam_audio/demo-city-history-walk.wav'
    target = Path(settings.MEDIA_ROOT) / name
    if not target.is_file():
        engine = shutil.which('espeak-ng')
        if not engine:
            stdout.write('Demo audio: espeak-ng topilmadi. sudo apt install espeak-ng')
            return False
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run([engine, '-v', 'en-gb', '-s', '135', '-w', str(target), LISTENING_SCRIPT],
                           check=True, capture_output=True, timeout=30)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            target.unlink(missing_ok=True)
            stdout.write('Demo audio yaratilmadi; espeak-ng ni tekshiring.')
            return False
    if not target.is_file() or target.stat().st_size <= 44:
        target.unlink(missing_ok=True)
        stdout.write('Demo audio fayli bo‘sh; espeak-ng ni tekshiring.')
        return False
    exam.audio_file.name = name
    exam.audio_url = ''
    exam.save(update_fields=['audio_file', 'audio_url'])
    for attempt in Attempt.objects.filter(exam=exam, state='in_progress'):
        snapshot = attempt.snapshot
        if snapshot.get('passage') == LISTENING_SCRIPT and snapshot.get('audio_url') in ('', 'browser-tts://passage'):
            snapshot['audio_url'] = exam.audio_file.url
            attempt.snapshot = snapshot
            attempt.save(update_fields=['snapshot'])
    stdout.write(f'Demo audio tayyor: {exam.audio_file.url}')
    return True


class Command(BaseCommand):
    help = "Seed original IELTS-style Reading, Listening and Writing practice material without overwriting existing exams."

    def handle(self, *args, **options):
        created = 0
        backfilled_audio = 0
        for spec in EXAMS:
            existing = Exam.objects.filter(title=spec["title"]).first()
            if existing:
                # Older local demo rows may predate the browser TTS fallback. Only
                # fill a missing audio source; never replace a real URL or content.
                audio_url = spec.get("audio_url", "")
                usable_audio = bool(existing.audio_file) or existing.audio_url.startswith("https://") or existing.audio_url == "browser-tts://passage"
                if existing.section == "Listening" and audio_url and not usable_audio:
                    existing.audio_url = audio_url
                    existing.save(update_fields=["audio_url"])
                    for attempt in Attempt.objects.filter(exam=existing, state="in_progress"):
                        snapshot = attempt.snapshot
                        saved_audio = str(snapshot.get("audio_url") or "")
                        if not (saved_audio.startswith("https://") or saved_audio == "browser-tts://passage"):
                            snapshot["audio_url"] = audio_url
                            attempt.snapshot = snapshot
                            attempt.save(update_fields=["snapshot"])
                    backfilled_audio += 1
                    self.stdout.write(self.style.SUCCESS(f"Repaired Listening demo playback source: {spec['title']}"))
                else:
                    self.stdout.write(f"Already exists, kept unchanged: {spec['title']}")
                if existing.section == 'Listening':
                    attach_demo_audio(existing, self.stdout)
                continue
            questions = spec["questions"]
            exam_data = {key: value for key, value in spec.items() if key != "questions"}
            exam = Exam.objects.create(**exam_data, published=False)
            for position, (prompt, choices, answers, evidence, explanation, skill_tag) in enumerate(questions, 1):
                Question.objects.create(
                    exam=exam,
                    position=position,
                    prompt=prompt,
                    choices=choices,
                    accepted_answers=answers,
                    evidence=evidence,
                    explanation=explanation,
                    skill_tag=skill_tag,
                )
            try:
                validate_exam(exam)
            except ValidationError:
                exam.delete()
                raise
            exam.published = True
            exam.save(update_fields=["published"])
            if exam.section == 'Listening':
                attach_demo_audio(exam, self.stdout)
            created += 1
            self.stdout.write(self.style.SUCCESS(f"Created and published: {exam.title}"))
        self.stdout.write(self.style.SUCCESS(f"Seed complete. New exams: {created}; Listening sources repaired: {backfilled_audio}."))
