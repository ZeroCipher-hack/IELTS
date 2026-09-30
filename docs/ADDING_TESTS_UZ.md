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

AI tahlil uchun `backend/.env` faylida `AI_ENABLED=1` va `GEMINI_API_KEY=...` bo‘lsin. `bash dev.sh` ni qayta ishga tushiring: `assess_pending --watch` worker'i fon rejimida tahlil qiladi, natija sahifasi tayyor bo‘lganda yangilanadi. Javoblar AI xizmatiga server tomonidan yuboriladi; kalit frontendga chiqmaydi. Listening audio fayli AI xizmatiga yuborilmaydi: tushuntirish uchun testning passage/transkript matni va javob kaliti ishlatiladi. Haqiqiy Listening testida transkriptni foydalanuvchiga ko‘rsatishni istamasangiz, AI izohi uchun hozircha uni passage maydoniga qo‘shmang; savolga yozilgan tahririy dalil va izohlar ishlatiladi.

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
| Listening | Yuklangan audio fayl yoki ishlaydigan HTTPS audio manzili, savollar, variantlar va to‘g‘ri javoblar. Haqiqiy testda audio skriptini passage maydoniga kiritmang — foydalanuvchiga ko‘rinadi. |
| Reading | Matn, savollar, variantlar va javob kalitlari. True / False / Not Given variantlarini aynan TRUE, FALSE, NOT GIVEN deb yozing. |
| Writing | Prompt; admin panelda variantlar va javob kaliti maydonlarini bo‘sh qoldiring. Hozirgi demo Task 1 uchun raqamlarni matnli jadval ko‘rinishida beradi; rasmli diagrammani AI baholashga nashr qilmang. |
| Speaking | Admin savollaridan foydalanmaydi. AI mashqi alohida yoqiladi; to‘liq IELTS Speaking baholashi deb ko‘rsatmang. |

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
