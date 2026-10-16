# Test va savol qo'shish qo'llanmasi

Bu qo'llanma admin panel orqali yangi test qo'shishni tushuntiradi. Dasturchi bo'lish shart emas.

Admin panel: `http://127.0.0.1:8000/admin/` (lokal) yoki `https://sizning-domeningiz/admin/`.

---

## Asosiy qoida: avval qoralama, keyin nashr

Har bir test ikki holatda bo'ladi:

| Holat | Ma'nosi |
|---|---|
| **Qoralama** | Tahrirlash mumkin. Talabalar ko'rmaydi. |
| **Nashr qilingan** | Talabalar ko'radi. **Boshqa o'zgartirib bo'lmaydi.** |

Nashr qilingan test o'zgarmas bo'lib qoladi — bu ataylab shunday. Agar talaba testni topshirayotgan bo'lsa, savol o'rtada o'zgarib ketmasligi kerak.

**Xato topsangiz nima qilish kerak?** Testni ro'yxatdan tanlang → «Yangi versiyaga nusxalash (qoralama)» amalini ishlating. Yangi qoralama yaratiladi, uni tuzatib, qayta nashr qilasiz.

---

## 1-qadam: Testni yaratish

Admin → **Exams** → **Qo'shish**.

**1. Test haqida**

| Maydon | Nima yoziladi |
|---|---|
| Test nomi | Masalan: `Academic Reading — Urban transport` |
| Bo'lim | Reading, Listening, Writing yoki Speaking |
| Davomiyligi | Soniyada. 600 = 10 daqiqa, 3600 = 1 soat |

**2. Material** — bo'limga qarab farq qiladi:

- **Reading** → «Matn / transkript» maydoniga o'qish matnini yozing. **Majburiy.**
- **Listening** → «Audio fayl» maydoniga yozuvni yuklang. Transkriptni «Matn / transkript» maydoniga qo'ying (ixtiyoriy, lekin dalil ko'rsatish uchun juda foydali).
- **Writing** → matn maydoniga umumiy ko'rsatma. Topshiriqlarning o'zi savollar bo'limiga yoziladi.

---

## 2-qadam: Savollarni qo'shish

Xuddi shu sahifaning pastida **Savollar** bo'limi bor. Har bir savol uchun alohida blok to'ldiriladi.

### Tartib raqami
1 dan boshlang, takrorlanmasin. Savollar shu raqam bo'yicha tartiblanadi.

### Savol matni
Talaba ko'radigan matn. Ingliz tilida yozing.

### Variantlar
**Har bir variant — alohida qator.** Vergul yoki qavs kerak emas.

To'g'ri:
```
TRUE
FALSE
NOT GIVEN
```

Bu maydonni **bo'sh qoldirsangiz**, savol ochiq javobli bo'ladi — talaba matn yozadi.

### To'g'ri javob(lar)
Bu ham **har bir javob alohida qatorda**.

- Variantlar bo'lsa, javob **aynan ulardan biri** bo'lishi shart. `TRUE` yozilgan bo'lsa, `True` deb yozsangiz xato beradi.
- Ochiq javobda bir nechta qabul qilinadigan yozilish berishingiz mumkin:

```
6
six
```

Talaba `6` yoki `six` yozsa ham to'g'ri hisoblanadi. Katta-kichik harf va ortiqcha bo'shliqlar avtomatik e'tiborga olinmaydi.

Reading va Listening uchun javob **majburiy**. Writing uchun bo'sh qoldiriladi (AI baholaydi).

### Ko'nikma turi
Masalan: `True / False / Not Given`, `Matching headings`, `Multiple choice`, `Short answer`.

Natijalar sahifasida talabaning zaif tomonlarini shu bo'yicha guruhlaydi. Bir xil turdagi savollarga bir xil nom bering.

### Matndagi dalil
Matn yoki transkriptdan **aynan ko'chirilgan** parcha. Natijada talabaga «javob mana shu yerda» deb ko'rsatiladi.

Ko'chirishda o'zgartirmang — tizim uni matndan qidiradi.

`NOT GIVEN` javobli savolda dalil bo'lmaydi, bo'sh qoldiring.

### Izoh
Nega bu javob to'g'ri. O'zbek tilida yozsa bo'ladi — talaba shuni o'qiydi.

---

## 3-qadam: Nashr qilish

**«Nashr qilingan» katagini o'zingiz belgilamang.**

Exams ro'yxatiga qayting → testni belgilang → yuqoridagi amallar ro'yxatidan **«Tekshirish va nashr qilish»** ni tanlang.

Bu amal avval xatolarni tekshiradi:

- nom bo'sh emasmi
- davomiylik 60–14400 soniya oralig'idami
- kamida bitta savol bormi
- Reading uchun matn bormi
- **Listening uchun audio bormi**
- Writing uchun ko'pi bilan ikkita topshiriqmi
- har bir savolda matn bormi
- javob kaliti variantlarga mos keladimi

Xato bo'lsa, qizil xabarda aynan nima noto'g'ri ekani yoziladi va test nashr qilinmaydi.

---

## Listening audiosi

Ikkita yo'l bor:

**1. Fayl yuklash (tavsiya etiladi).** «Audio fayl» maydoniga bosib, kompyuteringizdan faylni tanlang.

- Formatlar: `mp3`, `m4a`, `aac`, `ogg`, `oga`, `opus`, `wav`, `webm`
- Maksimal hajm: 40 MB (`EXAM_AUDIO_MAX_BYTES` bilan o'zgartiriladi)

**2. Tashqi havola.** Fayl boshqa serverda bo'lsa, «Yoki tashqi audio havolasi» maydoniga qo'ying. Havola **albatta `https://` bilan boshlanishi** kerak — `http://` qabul qilinmaydi.

Ikkalasi ham to'ldirilsa, **yuklangan fayl ustun turadi**.

### Audio chiqmasa

Ro'yxatdagi «Audio» ustuniga qarang:

- **fayl** (yashil) — fayl yuklangan, hammasi joyida
- **tashqi havola** — havola ishlatilyapti; havola ochilishini brauzerda tekshiring
- **YO'Q** (qizil) — audio biriktirilmagan, test nashr qilinmaydi

Agar test allaqachon nashr qilingan bo'lsa, audio maydoni qulflanadi. «Yangi versiyaga nusxalash» qiling, audioni qo'shing, qayta nashr qiling.

---

## Speaking testi

Speaking boshqa bo'limlardan farq qiladi: u **suhbat emas, ssenariy**. Imtihon oluvchi belgilangan savollarni beradi, talaba javob beradi, hech qanday maslahat yoki baho ko'rsatilmaydi.

Shuning uchun har bir savolga **qism** belgilanadi:

| Qism | Nima bo'ladi | Vaqt (har savolga) |
|---|---|---|
| **Part 1** | Tanishuv savollari: uy, ish, o'qish, qiziqishlar | 60 soniya |
| **Part 2** | Cue card — bitta mavzu, oldin 1 daqiqa tayyorgarlik | 120 soniya |
| **Part 3** | Part 2 mavzusiga bog'liq mavhum savollar | 90 soniya |

Vaqtlar qismdan kelib chiqib avtomatik belgilanadi — alohida kiritish shart emas.

### Qoidalar

Test nashr qilinishi uchun quyidagilar shart:

- kamida bitta **Part 1** savoli
- aynan bitta **Part 2** cue card
- kamida bitta **Part 3** savoli
- har bir savolda qism belgilangan bo'lishi (`—` qolmasligi)

### Part 2 cue card

Cue card uchun:

- **Savol matni** — mavzu sarlavhasi, masalan `Describe a skill you would like to learn.`
- **Variantlar** maydoni — cue card bandlari, har biri alohida qatorda:

```
What the skill is
Why you want to learn it
How you would go about learning it
And explain how this skill would change your daily life
```

Talaba avval 1 daqiqa tayyorgarlik ekranini ko'radi (cue card va taymer), keyin savol o'qiladi va yozuv boshlanadi.

### Savol audiosi

Har bir savolga **o'z audio faylini** yuklashingiz mumkin — imtihon oluvchining o'sha savolni o'qigan yozuvi.

Audio yuklamasangiz, **brauzer savol matnini ovoz bilan o'qiydi**. Bu ishlaydi, lekin ovoz sifati qurilmaga bog'liq va qurilmada inglizcha ovoz bo'lmasligi mumkin — u holda savol faqat ekranda ko'rinadi.

Haqiqiy imtihon tajribasi uchun har bir savolga yozuv yuklashni tavsiya qilamiz.

### Javob kaliti

Speaking uchun **To'g'ri javob(lar)** maydoni bo'sh qoldiriladi. Javoblar yozib olinadi va AI baholaydi.

### Baholash

Talaba barcha savollarga javob bergach, yozuvlar serverga yuboriladi va test `Baholash kutilmoqda` holatiga o'tadi.

Baho chiqishi uchun `GEMINI_API_KEY` va `AI_ENABLED=1` kerak, hamda baholash ishchisi ishlab turishi kerak.

Avval kalitni tekshiring — bu buyruq kalitning o‘zini ekranga chiqarmaydi:

```bash
cd backend
.venv/bin/python manage.py ai_check
```

Uchta qadam ketma-ket tekshiriladi: sozlama, kalit va model ro‘yxati, so‘ng haqiqiy so‘rov.
Xato bo‘lsa, aynan qaysi bosqichda va nima sababdan ekani yoziladi.

Hammasi joyida bo‘lsa, ishchini alohida terminalda ishga tushiring:

```bash
.venv/bin/python manage.py assess_pending --watch
```

Kalit bo'lmasa, yozuvlar saqlanib turadi va kalit ulangach baholanadi — xuddi Writing kabi.

### Erkin suhbat mashqi — alohida narsa

`/dashboard/speaking` sahifasidagi **ovozli mashq** — bu imtihon emas. U Gemini Live orqali erkin suhbatlashadi, qo'shimcha savollar beradi va imtihon qoidalariga bo'ysunmaydi. U alohida imkoniyat sifatida qoladi va `VOICE_PRACTICE_ENABLED=1` hamda jonli kalit talab qiladi.

Imtihon rejimi uchun Live kerak emas.

---

## Audioni avtomatik yaratish

Listening yozuvini yoki imtihon oluvchining ovozini qo'lda yozib o'tirmasdan, Gemini orqali yaratish mumkin:

```bash
cd backend
.venv/bin/python manage.py ai_check          # avval kalit ishlayotganini tekshiring
.venv/bin/python manage.py generate_audio
```

Buyruq **faqat qoralama** testlarga tegadi:

- **Speaking** — har bir savol uchun alohida yozuv. Part 2 cue card bandlari bilan birga o'qiladi.
- **Listening** — «Matn / transkript» maydonidagi matn to'liq o'qib, audio fayl sifatida biriktiriladi.

Mavjud audio o'chirilmaydi. Qayta yaratish uchun `--replace` qo'shing. Bitta testga cheklash: `--exam 7`.

Yaratilgandan keyin admin panelda «Tekshirish va nashr qilish» amalini ishlating.

> Ovoz sun'iy, lekin barqaror: brauzer ovoziga bog'liq emas va har bir qurilmada bir xil eshitiladi. Haqiqiy odam yozuvi baribir yaxshiroq — buni boshlang'ich material deb oling.

---

## 40 savollik testlar (band chiqishi uchun)

Loyihada ikkita to'liq uzunlikdagi ish bor. Ularni bir marta yaratib oling:

```bash
cd backend
.venv/bin/python manage.py seed_papers
```

| Ish | Holat |
|---|---|
| `Academic Reading — Movement, materials and memory` | 40 savol, **darhol nashr qilinadi** |
| `Listening — Riverside: services, work and study` | 40 savol + to'liq transkript, **qoralama** |

Listening'ni tugatish uchun audio kerak:

```bash
.venv/bin/python manage.py generate_audio --section Listening --publish
```

Buyruq audioning **tezligini va hajmini aytadi**:

```
davomiyligi 6:28, taxminan 145 so'z/daqiqa — IELTS tezligiga yaqin
fayl hajmi 3 MB
```

IELTS Listening ~140–150 so'z/daqiqa. `JUDA TEZ` yoki `JUDA SEKIN` chiqsa, eshitib ko'ring va `--replace` bilan qayta yarating. Ikkalasi ham yomon: tez bo'lsa talaba ulgurmaydi, sekin bo'lsa bu haqiqiy imtihonga tayyorlamaydi.

**ffmpeg o'rnating** — fayl MP3 ga siqiladi va ~6 barobar kichrayadi:

```bash
sudo apt install ffmpeg
```

Usiz WAV saqlanadi: bir xil ovoz, lekin 40 MB atrofida. Bu yuklash chegarasiga yaqin va mobil internetdagi talaba uchun og'ir.

### Limit (`AI_RATE_LIMIT`) chiqsa

Bepul Gemini kaliti daqiqasiga bir nechta so'rovga ruxsat beradi, TTS modeli esa eng qattiq cheklangani. Buyruq buni hisobga oladi:

- so'rovlar orasida **20 soniya** kutadi (`--delay 30` bilan ko'paytiring);
- limitga urilsa kutib, **qayta uradi** (`--retries`);
- uzun transkriptni bo'laklarga bo'lib o'qiydi va audioni birlashtiradi — 5400 belgilik transkript 3 ta so'rov bo'ladi, 42 ta emas.

Google javobida **qancha kutish kerakligini** aytadi va buyruq aynan shu raqamga amal qiladi — taxmin qilmaydi.

### «Kunlik limit tugadi»

Bepul kvota ikki xil: daqiqalik va **kunlik**. Kunligi tugasa, kutish umuman yordam bermaydi — buyruq darhol to'xtaydi va shuni aytadi. Kvota Tinch okeani vaqti bilan yarim tunda yangilanadi.

Bunday holatda:

1. **Avval Listening'ni tugating** — u atigi 3 ta so'rov oladi va **usiz to'liq imtihon umuman boshlanmaydi**.
2. Speaking audiosiz ham ishlaydi: savollarni brauzer ovoz bilan o'qiydi, o'qiy olmasa ekranda ko'rsatadi. Ya'ni Speaking audiosi — yaxshilanish, to'siq emas.

**Eng muhimi: buyruqni qayta ishga tushirish xavfsiz.** Allaqachon yaratilgan yozuvlar o'tkazib yuboriladi, `--duplicate` esa yangi nusxa yasamasdan **mavjud qoralamani davom ettiradi**. Ya'ni limit tugagach bir necha soatdan keyin yana ishga tushirsangiz, qolgan yozuvlargina yaratiladi.

### Nashr qilingan testga audio qo'shish

Nashr qilingan test o'zgarmas. Buyruq uni **nusxalab**, nusxaga audio qo'yadi va kerak bo'lsa nashr qiladi:

```bash
.venv/bin/python manage.py generate_audio --section Speaking --duplicate --publish
```

Eski versiya joyida qoladi va ishlayotgan urinishlar buzilmaydi. To'liq imtihon har doim eng yangi nashr qilingan testni oladi, shuning uchun yangi versiya avtomatik ishlatiladi.

---

## To'liq imtihon (IELTS Academic)

Talaba «Imtihonlar» sahifasidan **To'liq imtihonni boshlash** tugmasini bosadi. To'rtta bo'lim ketma-ket topshiriladi: Listening → Reading → Writing → Speaking.

Har bir bo'lim uchun **o'sha bo'limdagi eng yangi nashr qilingan test** olinadi. Agar biror bo'limda nashr qilingan test bo'lmasa, imtihon umuman boshlanmaydi va qaysi bo'lim yetishmayotgani yoziladi.

### Band qachon chiqadi

| Bo'lim | Band manbai |
|---|---|
| Listening, Reading | Faqat test **aynan 40 savoldan** iborat bo'lsa, jadval bo'yicha taxmin |
| Writing, Speaking | AI baholashi (kalit kerak) |

**40 savoldan kam testda band chiqarilmaydi** — faqat to'g'ri javoblar soni ko'rsatiladi. Bu ataylab shunday: 6 ta savoldan 5 tasi to'g'ri bo'lsa, bu «band 8» degani emas, va noto'g'ri band talabani chalg'itadi.

**Umumiy band to'rttala bo'limda ham band bo'lgandagina chiqadi.** Uchta band va bitta xom ball — umumiy band emas.

Umumiy band to'rtta bandning o'rtachasi, IELTS qoidasi bo'yicha yaxlitlanadi (`.25` va `.75` yuqoriga).

Barcha bandlar **taxminiy** — rasmiy IELTS natijasi emas, va shunday deb belgilanadi.

---

## Ko'p savolni birdan yuklash

Bitta-bitta kiritish uzoq bo'lsa, JSON fayldan import qiling:

```bash
cd backend
.venv/bin/python manage.py import_exam savollar.json
```

Fayl ko'rinishi:

```json
{
  "title": "Academic Reading — Urban transport",
  "section": "Reading",
  "duration_seconds": 1200,
  "passage": "O'qish matni shu yerda...",
  "questions": [
    {
      "prompt": "Cycling increased after the new lanes opened.",
      "choices": ["TRUE", "FALSE", "NOT GIVEN"],
      "accepted_answers": ["TRUE"],
      "skill_tag": "True / False / Not Given",
      "evidence": "Cycling rose by a third in the year after the lanes opened.",
      "explanation": "Matnda o'sish aniq keltirilgan."
    },
    {
      "prompt": "How many new lanes were built?",
      "choices": [],
      "accepted_answers": ["12", "twelve"],
      "skill_tag": "Short answer",
      "evidence": "Twelve new lanes were built.",
      "explanation": "Son matndan olinadi."
    }
  ]
}
```

Tartib raqamlari avtomatik qo'yiladi. Import **qoralama** yaratadi — nashr qilishni admin paneldan qilasiz.

Listening uchun import qilgandan keyin admin panelda audio faylni yuklashingiz kerak.

---

## Tez eslatma

| Muammo | Sabab |
|---|---|
| «Javob kaliti variantlarga mos emas» | Javobda yozilgan matn variantlar ro'yxatida yo'q. Harfma-harf bir xil bo'lsin. |
| «Listening uchun audio fayl yuklang...» | Audio biriktirilmagan yoki havola `https://` bilan boshlanmagan. |
| Testni tahrirlab bo'lmayapti | Test nashr qilingan. Nusxa oling. |
| Talaba testni ko'rmayapti | Test nashr qilinmagan, yoki talabada bepul urinish qolmagan. |
| Audio ko'rinmayapti | Bo'lim Listening emas, yoki test boshlangan vaqtda audio hali biriktirilmagan edi. Yangi urinish boshlanishi kerak. |
