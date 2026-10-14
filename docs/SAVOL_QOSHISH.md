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

Baho chiqishi uchun `GEMINI_API_KEY` va `AI_ENABLED=1` kerak, hamda baholash ishchisi ishlab turishi kerak:

```bash
cd backend
.venv/bin/python manage.py assess_pending --watch
```

Kalit bo'lmasa, yozuvlar saqlanib turadi va kalit ulangach baholanadi — xuddi Writing kabi.

### Erkin suhbat mashqi — alohida narsa

`/dashboard/speaking` sahifasidagi **ovozli mashq** — bu imtihon emas. U Gemini Live orqali erkin suhbatlashadi, qo'shimcha savollar beradi va imtihon qoidalariga bo'ysunmaydi. U alohida imkoniyat sifatida qoladi va `VOICE_PRACTICE_ENABLED=1` hamda jonli kalit talab qiladi.

Imtihon rejimi uchun Live kerak emas.

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
