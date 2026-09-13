export type Lang = "uz" | "en" | "ru";

export const LANGS: Lang[] = ["uz", "en", "ru"];

type Dict = {
  nav: { features: string; how: string; pricing: string; login: string };
  ctaPrimary: string;
  hero: {
    title: string;
    subtitle: string;
    cta: string;
    ctaNote: string;
    secondary: string;
    mockTitle: string;
    mockBand: string;
    mockOverall: string;
  };
  trust: string[];
  how: { title: string; steps: { title: string; text: string }[] };
  features: {
    title: string;
    subtitle: string;
    soon: string;
    items: { name: string; text: string; soon?: boolean }[];
  };
  why: { title: string; items: { title: string; text: string }[] };
  status: { badge: string; title: string; text: string };
  proof: { title: string; subtitle: string; placeholder: string };
  finalCta: { title: string; text: string; button: string };
  footer: { tagline: string; contact: string; privacy: string; terms: string; rights: string };
};

export const t: Record<Lang, Dict> = {
  uz: {
    nav: { features: "Xususiyatlar", how: "Qanday ishlaydi", pricing: "Narxlar", login: "Kirish" },
    ctaPrimary: "Bepul boshlash",
    hero: {
      title: "IELTS Academic imtihonini real formatda onlayn mashq qiling",
      subtitle:
        "Listening, Reading, Writing va Speaking — to'rtta ko'nikma bo'yicha haqiqiy imtihon tartibida tayyorlaning va darhol natija oling.",
      cta: "Bepul urinishni boshlash",
      ctaNote: "Bitta bepul urinish — karta talab qilinmaydi",
      secondary: "Qanday ishlashini ko'rish",
      mockTitle: "Natijalar paneli namunasi",
      mockBand: "Ko'nikmalar bo'yicha taqsimot",
      mockOverall: "Umumiy ball",
    },
    trust: ["4 ta ko'nikma", "Darhol natija", "O'zbek, ingliz, rus tillarida"],
    how: {
      title: "Qanday ishlaydi",
      steps: [
        { title: "Ro'yxatdan o'ting", text: "Hisob yarating va bepul urinishingizni oling." },
        {
          title: "Testni topshiring",
          text: "Reading, Listening va Writing bo'yicha real formatda test topshiring.",
        },
        {
          title: "Rejangizni oling",
          text: "Darhol batafsil hisobot va zaif tomonlaringiz bo'yicha haftalik reja.",
        },
      ],
    },
    features: {
      title: "To'rtta ko'nikma, bitta platforma",
      subtitle: "Har bir bo'lim haqiqiy IELTS Academic tartibiga mos.",
      soon: "Tez orada",
      items: [
        { name: "Listening", text: "Audio bilan real vaqt rejimida, avtomatik va aniq baholash." },
        { name: "Reading", text: "Academic matnlar, mavjud savol turlari, darhol natija." },
        { name: "Writing", text: "Task 1 va Task 2 uchun batafsil, dalilga asoslangan izohlar." },
        { name: "Speaking", text: "Uch qismli suhbat mashqi ishlab chiqilmoqda.", soon: true },
      ],
    },
    why: {
      title: "Nega IELTSQA",
      items: [
        {
          title: "Darhol va aniq baholash",
          text: "Reading va Listening natijalari determinik tarzda, kutishsiz hisoblanadi.",
        },
        {
          title: "Xatolar dalil bilan",
          text: "Matnning aynan qaysi qismi yoki javobingiz qayeri noto'g'ri bo'lganini ko'rsatamiz.",
        },
        {
          title: "Shaxsiy haftalik reja",
          text: "Zaif tomonlaringizdan kelib chiqib, haftalik mashg'ulot rejasi tuziladi.",
        },
        {
          title: "Toza imtihon muhiti",
          text: "Chalg'itmaydigan interfeys va haqiqiy taymer bilan imtihon tajribasi.",
        },
      ],
    },
    status: {
      badge: "Ochiq ma'lumot",
      title: "Hozirgi holat",
      text: "Bu hozircha pullik mahsulot emas — birinchi urinish bepul, keyingi kirish administrator orqali beriladi. To'lov tizimi tez orada ishga tushadi.",
    },
    proof: {
      title: "Talabalar fikri",
      subtitle: "Bu joy haqiqiy fikrlar bilan to'ldiriladi.",
      placeholder: "Sharh uchun joy — keyinroq to'ldiriladi.",
    },
    finalCta: {
      title: "IELTS'ga bugun tayyorlanishni boshlang",
      text: "Bitta bepul urinish bilan darajangizni bilib oling.",
      button: "Bepul boshlash",
    },
    footer: {
      tagline: "IELTS Academic mock imtihonlari — o'zbek talabalari uchun.",
      contact: "Bog'lanish",
      privacy: "Maxfiylik",
      terms: "Foydalanish shartlari",
      rights: "Barcha huquqlar himoyalangan.",
    },
  },
  en: {
    nav: { features: "Features", how: "How it works", pricing: "Pricing", login: "Log in" },
    ctaPrimary: "Start free",
    hero: {
      title: "Practice the real IELTS Academic format online",
      subtitle:
        "Prepare across all four skills — Listening, Reading, Writing and Speaking — in exam conditions and get results immediately.",
      cta: "Start your free attempt",
      ctaNote: "One free attempt — no credit card",
      secondary: "See how it works",
      mockTitle: "Results dashboard",
      mockBand: "Skill breakdown",
      mockOverall: "Overall band",
    },
    trust: ["4 skills", "Instant results", "Uzbek, English, Russian"],
    how: {
      title: "How it works",
      steps: [
        { title: "Sign up", text: "Create an account and claim your free attempt." },
        {
          title: "Take the test",
          text: "Sit Reading, Listening and Writing in the real exam format.",
        },
        {
          title: "Get your plan",
          text: "Receive a detailed report and a weekly plan built around your weak spots.",
        },
      ],
    },
    features: {
      title: "Four skills, one platform",
      subtitle: "Every section follows the real IELTS Academic structure.",
      soon: "Coming soon",
      items: [
        { name: "Listening", text: "Timed audio sections with automatic, precise scoring." },
        { name: "Reading", text: "Academic passages, available question types, instant results." },
        { name: "Writing", text: "Evidence-based feedback on Task 1 and Task 2." },
        { name: "Speaking", text: "Three-part interview practice is in development.", soon: true },
      ],
    },
    why: {
      title: "Why IELTSQA",
      items: [
        {
          title: "Instant, deterministic scoring",
          text: "Reading and Listening are scored the same way every time, with no waiting.",
        },
        {
          title: "Mistakes backed by evidence",
          text: "We show exactly which part of the text or your answer went wrong.",
        },
        {
          title: "Personal weekly plan",
          text: "A study plan generated from the weak spots in your own results.",
        },
        {
          title: "Clean exam interface",
          text: "A distraction-free screen with a real exam timer.",
        },
      ],
    },
    status: {
      badge: "Full transparency",
      title: "Where we are today",
      text: "This is not a paid product yet — the first attempt is free and further access is granted by an administrator. Payments are coming soon.",
    },
    proof: {
      title: "Student feedback",
      subtitle: "Real feedback will be added here.",
      placeholder: "Placeholder for a review — to be filled in later.",
    },
    finalCta: {
      title: "Start preparing for IELTS today",
      text: "Find out your level with one free attempt.",
      button: "Start free",
    },
    footer: {
      tagline: "IELTS Academic mock exams for Uzbek students.",
      contact: "Contact",
      privacy: "Privacy",
      terms: "Terms of use",
      rights: "All rights reserved.",
    },
  },
  ru: {
    nav: { features: "Возможности", how: "Как это работает", pricing: "Цены", login: "Войти" },
    ctaPrimary: "Начать бесплатно",
    hero: {
      title: "Тренируйте настоящий формат IELTS Academic онлайн",
      subtitle:
        "Готовьтесь по всем четырём навыкам — Listening, Reading, Writing и Speaking — в условиях экзамена и получайте результат сразу.",
      cta: "Начать бесплатную попытку",
      ctaNote: "Одна бесплатная попытка — без карты",
      secondary: "Посмотреть, как это работает",
      mockTitle: "Панель результатов",
      mockBand: "Разбор по навыкам",
      mockOverall: "Общий балл",
    },
    trust: ["4 навыка", "Мгновенный результат", "Узбекский, английский, русский"],
    how: {
      title: "Как это работает",
      steps: [
        { title: "Зарегистрируйтесь", text: "Создайте аккаунт и получите бесплатную попытку." },
        {
          title: "Пройдите тест",
          text: "Reading, Listening и Writing в настоящем экзаменационном формате.",
        },
        {
          title: "Получите план",
          text: "Подробный отчёт и недельный план по вашим слабым местам.",
        },
      ],
    },
    features: {
      title: "Четыре навыка, одна платформа",
      subtitle: "Каждый раздел повторяет структуру настоящего IELTS Academic.",
      soon: "Скоро",
      items: [
        { name: "Listening", text: "Аудио по таймеру и точная автоматическая оценка." },
        { name: "Reading", text: "Академические тексты, доступные типы заданий, результат сразу." },
        { name: "Writing", text: "Обоснованная обратная связь по Task 1 и Task 2." },
        { name: "Speaking", text: "Практика интервью из трёх частей в разработке.", soon: true },
      ],
    },
    why: {
      title: "Почему IELTSQA",
      items: [
        {
          title: "Мгновенная точная оценка",
          text: "Reading и Listening считаются детерминированно и без ожидания.",
        },
        {
          title: "Ошибки с доказательством",
          text: "Показываем, какая именно часть текста или ответа была неверной.",
        },
        {
          title: "Личный недельный план",
          text: "План занятий формируется из ваших слабых мест.",
        },
        {
          title: "Чистый интерфейс экзамена",
          text: "Ничего лишнего и настоящий экзаменационный таймер.",
        },
      ],
    },
    status: {
      badge: "Честно и открыто",
      title: "Текущий статус",
      text: "Это пока не платный продукт — первая попытка бесплатна, дальнейший доступ выдаёт администратор. Оплата появится скоро.",
    },
    proof: {
      title: "Отзывы студентов",
      subtitle: "Здесь появятся настоящие отзывы.",
      placeholder: "Место для отзыва — заполним позже.",
    },
    finalCta: {
      title: "Начните подготовку к IELTS сегодня",
      text: "Узнайте свой уровень за одну бесплатную попытку.",
      button: "Начать бесплатно",
    },
    footer: {
      tagline: "Пробные экзамены IELTS Academic для студентов Узбекистана.",
      contact: "Контакты",
      privacy: "Конфиденциальность",
      terms: "Условия использования",
      rights: "Все права защищены.",
    },
  },
};


// Keep promotional copy aligned with the currently available product.
t.uz.hero.subtitle = "Mavjud testlarni topshiring, javoblaringizni tahlil qiling va keyingi mashqlar uchun haftalik reja oling.";
t.en.hero.subtitle = "Take available tests, review your answers and get a weekly plan for your next practice sessions.";
t.ru.hero.subtitle = "Проходите доступные тесты, разбирайте ответы и получайте недельный план практики.";
t.uz.features.subtitle = "Mavjud testlar va sinovdagi imkoniyatlar bilan tanishing.";
t.en.features.subtitle = "Explore available tests and features currently in testing.";
t.ru.features.subtitle = "Доступные тесты и функции на стадии тестирования.";
t.uz.features.items[3].text = "AI sozlanganida uch qismli ovozli mashq. Hozircha band bahosi berilmaydi.";
t.en.features.items[3].text = "Three-part voice practice when AI is configured. No band score yet.";
t.ru.features.items[3].text = "Голосовая практика из трёх частей при подключённом ИИ. Пока без оценки band.";
t.uz.features.soon = "Sinovda"; t.en.features.soon = "Pilot"; t.ru.features.soon = "Тестирование";
t.uz.how.steps[2].text = "Baholangan javoblardan batafsil hisobot va haftalik reja oling. AI tekshiruvi vaqt olishi mumkin.";
t.en.how.steps[2].text = "Get a report and weekly plan from assessed answers. AI assessment may take time.";
t.ru.how.steps[2].text = "Получите отчёт и план по оценённым ответам. Проверка ИИ может занять время.";
t.uz.finalCta.text = "Mavjud bo‘limlardan bittasini bir marta bepul sinab ko‘ring. Natijalar rasmiy IELTS bahosi emas.";
t.en.finalCta.text = "Try one available section once for free. Results are not official IELTS scores.";
t.ru.finalCta.text = "Попробуйте один доступный раздел бесплатно один раз. Результаты не являются официальной оценкой IELTS.";
