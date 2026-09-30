# IELTSQA’da test qo‘shish — o‘zbekcha qo‘llanma

## Tayyor sinov materiallarini bazaga kiritish

Loyiha papkasida quyidagilarni ishga tushiring:

    cd backend
    source .venv/bin/activate
    DJANGO_DEBUG=1 python manage.py seed_demo

Buyruq mavjud savollarni o‘zgartirmaydi. Eski demo Listening audio manbasi yaroqsiz bo‘lsa tuzatadi. Kompyuterda `espeak-ng` mavjud bo‘lsa, demo uchun lokal WAV ham yaratadi va davom etayotgan demo urinishlariga ulaydi. U original sinov materiallarini qo‘shadi:

- Listening: City History Walk — 8 savol. `espeak-ng` bo‘lsa WAV fayl yaratiladi; bo‘lmasa brauzerning sintetik ovozi sinab ko‘riladi. Ikkalasi ham mashq uchun sinov ovozi.
- Reading: Community Libraries — 8 ta True / False / Not Given savoli.
- Reading: Coastal Wetlands — 8 ta dalil topish, True / False / Not Given va qisqa javob savoli.
- Writing: Public Transport Trends — Task 1 va Task 2. AI kaliti va worker ishlamasa, javoblar saqlanadi, bahosi kutilayotgan holatda qoladi.
- Avvalgi Urban gardens Reading demosi saqlanadi.

Speaking alohida savol-javob testi emas: mavjud AI Speaking mashq sahifasi orqali ishlaydi. Uni sinash uchun serverda AI kaliti va kerakli Speaking sozlamalari yoqilgan bo‘lishi kerak. To‘liq imtihonda sozlanmagan bo‘lsa o‘tkazib yuborish mumkin.

Buyruqdan keyin localhost’ni yangilang, Testlar sahifasiga o‘ting. Lokal ./dev.sh sinov rejimida nashr qilingan testlarni ochadi.

### Brauzerda Listening ovozi eshitilmasa

Kali/Linux tizimida bir marta `sudo apt install espeak-ng` bajaring. Keyin `bash dev.sh` ni qayta ishga tushiring. `Demo audio tayyor: /media/exam_audio/demo-city-history-walk.wav` yozuvi chiqishi kerak. Frontendda Listening testini qayta oching; faol urinishdagi saqlangan javoblar saqlanadi. Audio `/media/` orqali Next.js tomonidan Django’dan uzatiladi. Brauzer orqali sintetik ovoz chiqmasa ham lokal WAV ijro etiladi.

## AI xatolarni qanday tushuntiradi

Reading va Listening javoblari doim testdagi javob kaliti bilan hisoblanadi. Xato bo‘lsa, AI matn yoki transkriptga tayangan holda nima uchun xato ekanini va uni qanday tuzatishni qo‘shimcha tushuntiradi. AI bandni o‘zgartirmaydi. Kalit sozlanmagan, AI kvotasi tugagan yoki xato bo‘lgan holatda ham savolning to‘g‘ri javobi, dalili va muallif yozgan izohi ko‘rinadi.

AI tahlil uchun `backend/.env` faylida `AI_ENABLED=1` va `GEMINI_API_KEY=...` bo‘lsin. `bash dev.sh` ni qayta ishga tushiring: `assess_pending --watch` worker'i fon rejimida tahlil qiladi, natija sahifasi tayyor bo‘lganda yangilanadi. Javoblar AI xizmatiga server tomonidan yuboriladi; kalit frontendga chiqmaydi. Listening audio fayli AI xizmatiga yuborilmaydi: tushuntirish uchun testning passage/transkript matni va javob kaliti ishlatiladi. Haqiqiy Listening testida transkriptni «Yashirin audio transkripti (AI uchun)» maydoniga kiriting. U foydalanuvchiga yuborilmaydi. Passage maydoni faqat sintetik demo uchun ishlatiladi; ovoz ishlamasa uning matni ko‘rinadi.

Writing va Speaking ilgari mavjud AI baholash oqimidan foydalanadi. Writing bahosi AI yo‘q bo‘lsa kutadi; Speaking uchun mikrofon va Gemini Live ulanishi kerak.

## Django admin orqali o‘zingiz test qo‘shish

1. Superuser bo‘lmasa yarating:

       cd backend
       source .venv/bin/activate
       DJANGO_DEBUG=1 python manage.py createsuperuser

2. Backend ishlab turganida http://127.0.0.1:8001/admin/ ga kiring.
3. Exams → Add exam ni tanlang.
4. Sarlavha, bo‘lim, davomiylik va bo‘limga tegishli matnni kiriting. Listening uchun `Audio file` maydoniga MP3, WAV, OGG, M4A yoki WebM yozuvini yuklang (ko‘pi bilan 20 MB) yoki ishlaydigan HTTPS audio manzilini kiriting. Ikkalasi ham bo‘lsa yuklangan fayl ishlatiladi.
5. Questions qismida har bir savol, variantlar va javob kalitini kiriting.
6. Testlar ro‘yxatiga qayting, qoralamani tanlang va “Tekshirish va nashr qilish” amalini bajaring. Xato xabari chiqsa tuzatib, qayta nashr qiling.
7. Frontenddagi Testlar sahifasini yangilang. To‘liq imtihonda yangi testni ishlatish uchun `/dashboard/full-exam` sahifasidagi Listening, Reading va Writing tanlovlaridan kerakli testni belgilang.

Nashr qilingan test urinishlarga snapshot sifatida nusxalanadi va admin orqali tahrirlanmaydi. Tuzatish kerak bo‘lsa, ro‘yxatdan testni tanlab “Yangi versiyaga nusxalash” qiling. Yangi qoralamani tahrirlab nashr qiling.

### Bo‘lim bo‘yicha kerakli maydonlar

| Bo‘lim | Kerakli ma’lumotlar |
|---|---|
| Listening | Yuklangan audio fayl yoki ishlaydigan HTTPS audio manzili, savollar, variantlar va to‘g‘ri javoblar. Audio skriptini yashirin transkript maydoniga kiriting; passage demo uchun, foydalanuvchiga ko‘rinishi mumkin. |
| Reading | Matn, savollar, variantlar va javob kalitlari. True / False / Not Given variantlarini aynan TRUE, FALSE, NOT GIVEN deb yozing. |
| Writing | Prompt; admin panelda variantlar va javob kaliti maydonlarini bo‘sh qoldiring. Hozirgi demo Task 1 uchun raqamlarni matnli jadval ko‘rinishida beradi; rasmli diagrammani AI baholashga nashr qilmang. |
| Speaking | Admin’dagi Speaking savol to‘plamlari ishlatiladi. AI mashqi alohida yoqiladi; to‘liq IELTS Speaking baholashi deb ko‘rsatmang. |

Admin panelga audio yuklasangiz, fayl `backend/media/exam_audio/` papkasida, fayl nomi esa SQLite bazasida saqlanadi. `backend/db.sqlite3` bazani zaxiralashning o‘zi yetmaydi: `backend/media/` papkasini ham saqlang. Lokal `dev.sh` media fayllarini uzatadi; production serverda `/media/` uchun doimiy storage va serving alohida sozlanadi. Tashqi HTTPS havola ishlatsangiz, brauzerda login talab qilmasdan ochilishi kerak. Faqat foydalanish huquqingiz bor audio qo‘shing.

## JSON fayl bilan Listening testi kiritish

JSON import qoralama yaratadi; avtomatik nashr qilinmaydi. Masalan, listening-demo.json:

    {
      "title": "Museum Booking — Listening practice",
      "section": "Listening",
      "duration_seconds": 600,
      "passage": "",
      "audio_url": "https://example.org/audio/museum-booking.mp3",
      "questions": [
        {
          "prompt": "What time does the tour begin?",
          "choices": ["9:00", "9:30", "10:00"],
          "accepted_answers": ["9:30"],
          "skill_tag": "Multiple choice",
          "evidence": "The tour begins at half past nine.",
          "explanation": "Half past nine is 9:30."
        }
      ]
    }

Import buyrug‘i:

    cd backend
    source .venv/bin/activate
    DJANGO_DEBUG=1 python manage.py import_exam /path/to/listening-demo.json

example.org manzilini haqiqiy, ishlaydigan HTTPS audio URL bilan almashtiring. Terminal chiqargan ID bilan admin panelda qoralamani ochib, tekshirib nashr qiling.

## Javob kalitini kiritish

- Multiple choice: choices ichidan to‘g‘ri variantni accepted_answers ichiga aynan ko‘chiring.
- Qisqa javob: choices bo‘sh ro‘yxat bo‘lsin; qabul qilinadigan javoblarni accepted_answers ichiga yozing. Muqobil imlolarni ham qo‘shing.
- True / False / Not Given: choices = ["TRUE", "FALSE", "NOT GIVEN"].
- Writing: choices va accepted_answers bo‘sh ro‘yxat bo‘ladi; topshiriq prompt ichida.

## Muhim

Repo ichidagi materiallar original mashq savollari, haqiqiy IELTS imtihonidan olinmagan. Listening sintetik ovozi bilan beriladigan demo oqimni tekshiradi, lekin haqiqiy audio sifati yoki IELTS imtihon darajasini tasdiqlamaydi. Reading va Listening natijasi xom to‘g‘ri javob soni. Writing bahosi AI sozlamalari va worker ishlashiga bog‘liq. Rasmiy IELTS bandi va’da qilinmaydi.

## Reading testini admin paneldan kiritish

1. `/admin/` ga staff hisob bilan kiring. Exams → Add orqali qoralama yarating.
2. Section: Reading. Duration seconds: 3600 — 60 daqiqa. Passage maydoniga matnni kiriting; paragraflar orasida bo‘sh qator qoldiring.
3. Savol qo‘shing: raqam, inglizcha savol va savol turini yozing. Variantlar uchun har qatorga bitta variant kiriting; qisqa javobda variantlarni bo‘sh qoldiring.
4. To‘g‘ri javoblar maydonida har qatorga bitta qabul qilinadigan javob yozing. JSON yozish kerak emas.
5. Dalil maydoniga matndan aynan jumlani ko‘chiring. NOT GIVEN uchun dalilni bo‘sh qoldiring. Tushuntirishda javobni topish usuli va xatoni takrorlamaslik yo‘lini yozing. Bu izoh faqat xato javobda ko‘rsatiladi.
6. Saqlang. Testlar ro‘yxatida qoralamani belgilang va «Tekshirish va nashr qilish» amalini bajaring. Keyingi tahrir uchun «Yangi versiyaga nusxalash»dan foydalaning.

AI izohlari uchun backend va baholash worker’ida `AI_ENABLED=1` hamda `GEMINI_API_KEY` sozlangan bo‘lishi kerak. AI ishlamasa ham javob kaliti bo‘yicha natija va admin kiritgan dalil/izoh saqlanadi.

## Listening: audio va savollarni admin paneldan yuklash

1. `http://127.0.0.1:8001/admin/` → Exams → Add exam. Section: Listening. Nom kiriting, vaqtni soniyalarda yozing (masalan, 10 daqiqa = 600).
2. «Listening audio» qismida Audio fayl → Choose file orqali MP3/WAV/OGG/M4A/WebM yuklang. Hajmi 20 MB dan oshmasin. Bevosita HTTPS audio havola ham mumkin; yuklangan fayl ustun turadi.
3. Yashirin audio transkripti maydoniga yozuvning aniq matnini kiriting. AI shu matnga tayangan holda xatoni tushuntiradi. Passage’ni haqiqiy test uchun bo‘sh qoldiring.
4. Savollar → yana bir savol qo‘shish. Quyidagi misolni kiriting:

| Maydon | Misol |
|---|---|
| Savol raqami | 1 |
| Savol | How much does the walk cost? |
| Javob variantlari | Har qatorga: £16, £18, £20 |
| To‘g‘ri javoblar | £18 |
| Matndan aniq dalil | The walk costs eighteen pounds. |
| Tushuntirish | Yozuvda eighteen aytilgan, eighty emas. Keyingi safar -teen va -ty tovushlariga e’tibor bering. |
| Savol turi | Multiple choice |

5. Qisqa javobli savolda variantlarni bo‘sh qoldiring. Qabul qilinadigan har bir javobni alohida qatorga yozing, masalan `18` va `eighteen`. Javob uzunligi yoki format qoidasini savolning o‘zida yozing; platforma yangi so‘z-limit qoidasi qo‘shmaydi.
6. Saqlang. Exams ro‘yxatida testni belgilang → «Tekshirish va nashr qilish» → Go. Frontend → Testlar → Listening orqali oching, Play recording tugmasini bosing. Vaqt va progress audio boshlangandan keyin yangilanadi.
7. Avval bitta javobni ataylab noto‘g‘ri topshirib tekshiring: natijada kalit, dalil va tahririy izoh chiqadi. AI yoqilgan va worker ishlayotgan bo‘lsa, qo‘shimcha nima uchun xato va keyingi qadam izohi keladi.

Audio yo‘q bo‘lsa: faylni admin orqali yuklash eng sodda yo‘l. Demo uchun Kali’da `sudo apt install espeak-ng`, keyin `bash dev.sh` ishlating. Brauzerda inglizcha ovoz yo‘q bo‘lsa, sintetik fallback o‘rniga namuna matni ko‘rsatiladi. Bu holat haqiqiy Listening sinovi hisoblanmaydi.

JSON import ham `listening_transcript` maydonini qabul qiladi. Import audio faylni o‘zi yuklamaydi: importdan keyin faylni admin orqali biriktiring (yoki JSON’da bevosita HTTPS `audio_url` kiriting). Nashr qilingan testlar uchun «Yangi versiyaga nusxalash» orqali qoralama yarating.

## Writing: Task 1 va Task 2 kiritish

1. Admin → Exams → Add exam. Section: Writing, duration_seconds: 3600. Nom yozib, «Save and continue editing» bosing: Writing uchun soddalashtirilgan forma ochiladi.
2. Writing materiallari maydoniga Task 1 jadvali yoki qo‘shimcha ma’lumotni matn shaklida kiriting. U topshiruvchiga ko‘rsatiladi va AI’ga JSON ma’lumot sifatida yuboriladi. Rasmli diagramma yuklash hozircha mavjud emas.
3. Savol qo‘shing: raqam **1**, prompt — Task 1 topshirig‘i, jadval va barcha kerakli raqamlar. Masalan: “Summarise the transport figures below. Write at least 150 words.”
4. Yana savol qo‘shing: raqam **2**, prompt — Task 2 mavzusi va yo‘riqnomasi. Masalan: “Some people think public transport should be free. Discuss both views and give your own opinion. Write at least 250 words.” Variantlar va to‘g‘ri javob kaliti kerak emas.
5. Saqlang, ro‘yxatdan «Tekshirish va nashr qilish» amalini bajaring. Alohida Task 2 mashqi uchun faqat raqam 2 bilan topshiriq qo‘shish mumkin.
6. Frontend → Writing → test. So‘z sanog‘i har bir Task uchun alohida; 150/250 tavsiyasi topshirishni bloklamaydi va avtomatik ball kamaytirmaydi. Bitta server muddati amal qiladi; 20/40 daqiqa tavsiyasi alohida majburiy timer emas.
7. Javobni topshirgach, AI_ENABLED=1, GEMINI_API_KEY va assess_pending worker ishlasa baho keladi. Kalit yo‘q yoki AI xato bo‘lsa javob saqlanadi, taxminiy baho o‘ylab topilmaydi.
8. Natijada har Task bahosi, to‘rtta mezon, javobdan dalil va yaxshilash tavsiyasi ko‘rinadi. Yangi AI hisobotlarida ko‘pi bilan uchta aniq xato uchun asl jumla, izoh va tuzatilgan inglizcha jumla bo‘ladi; mavjud eski hisobotlar o‘z holicha ochiladi.

Task 1 — kamida 150 so‘z, taxminan 20 daqiqa; Task 2 — kamida 250 so‘z, taxminan 40 daqiqa va ikki baravar vazn. Manba: https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-writing . Baho AI mashq taxmini; rasmiy IELTS natijasi emas.

## Speaking mashqini sinash

Speaking savollari admin’dagi «Speaking savol to‘plamlari» orqali kiritiladi. To‘plam nashr qilinmagan bo‘lsa, backend’dagi `exams/voice.py` standart skripti ishlatiladi: Part 1 tanish mavzular, Part 2 bitta cue card, Part 3 cue card mavzusiga bog‘liq umumiy savollar. Bu original mashq materiali, rasmiy imtihon savollari emas.

1. Backend’da AI_ENABLED=1, VOICE_PRACTICE_ENABLED=1 va GEMINI_API_KEY sozlangan bo‘lsin. Kalitni frontendga kiritmang. `bash dev.sh` worker’ni ham ishga tushiradi.
2. Speaking sahifasida mikrofon va ovozni tekshiring. Rozilikni belgilang, suhbatni boshlang. Localhost yoki HTTPS va mikrofon ruxsati kerak.
3. Savollar qat’iy tartibda beriladi. Mos kelmagan AI gaplari belgilangan savol bilan almashtiriladi; matni ko‘rinadi. Part 1/3 vaqti birinchi savol tugagach, Part 2’dagi 2 daqiqa esa taklif tugagach boshlanadi.
4. Part 1’dan keyin 1 daqiqa tayyorlanish: cue card va shaxsiy qisqa qaydlar. Qaydlar AI’ga yuborilmaydi; faqat shu ochiq sahifada saqlanadi. Part 2 davomida o‘qish mumkin, tahrirlash yopiladi. Part 2 taklifidan keyin qo‘shimcha AI savollari ijro etilmaydi.
5. Mashq tugagach «Baholash va natijani saqlash» bosing. Audio va nomzod transkripti yuboriladi; baho worker orqali keladi. Audio yetarli bo‘lmasa, tizim band o‘ylab topmaydi.
6. Refresh yoki chiqishda yuborilmagan yozuv va qaydlar yo‘qoladi. Ulanish uzilgan mashq natijasi to‘liq imtihon sifatida ko‘rsatilmaydi. Jonli mikrofon/Gemini sinovi alohida tekshirilishi kerak.

## Speaking savollarini admin’dan kiritish

1. `/admin/` → **Speaking savol to‘plamlari** → Add. To‘plam nomi va versiyani yozing.
2. Part 1 maydoniga har qatorga bitta inglizcha tanish mavzu savoli kiriting. Masalan: “What do you study?” va “What do you enjoy about your studies?”
3. Part 2 mavzusiga bitta cue card yozing: “Describe a library you have visited.” Tayanch punktlar maydoniga 3–5 ta punktni alohida qatorlarda yozing: “Where it is”, “When you visited”, “Why you remember it”.
4. Part 3 maydoniga shu mavzuga bog‘liq umumiy savollar yozing: “Why are libraries important for communities?” Savollarni kerakli tartibda kiriting; AI tartibni almashtirmaydi.
5. Saqlang. To‘plamlar ro‘yxatida qoralamani belgilang → «Tekshirish va nashr qilish». Part 1: 1–15 savol, Part 3: 1–12 savol, har savol/punkt 500 belgigacha.
6. Speaking sahifasini yangilang: to‘plam nomi va versiyasi ko‘rinadi. Oxirgi nashr qilingan to‘plam yangi suhbat uchun olinadi. Boshqa to‘plam nashr qilinsa ham, boshlangan suhbat eski to‘plamida davom etadi.
7. Nashr qilingan to‘plam o‘zgartirilmaydi va admin’dan o‘chirilmaydi. «Yangi versiyaga nusxalash» bilan qoralama yarating, tahrirlab nashr qiling. Yangi to‘plamlar eski natijalarni qayta baholamaydi.

Bu bo‘limda audio yoki javob kaliti yuklanmaydi: imtihon oluvchi savollarni o‘qiydi, topshiruvchi mikrofon orqali javob beradi. Savollar original mashq uchun; ularni kiritish AI ulanishi va worker o‘rnini bosmaydi.
