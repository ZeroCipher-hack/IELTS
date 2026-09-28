'use client';
import Link from 'next/link';
import { ArrowRight, BookOpen, Headphones, Mic, PenLine, Play, Sparkles, Target, Trophy } from 'lucide-react';
import { useProduct } from '@/components/product/product-context';
import LoadingSkeleton from '@/components/product/loading-skeleton';

const sections = [
  { name: 'Listening', Icon: Headphones, detail: ['Audio topshiriqlar', 'Audio practice', 'Аудио задания'] as const },
  { name: 'Reading', Icon: BookOpen, detail: ['Matnni tushunish', 'Reading passages', 'Чтение и понимание'] as const },
  { name: 'Writing', Icon: PenLine, detail: ['Task 1 va Task 2', 'Task 1 and Task 2', 'Задания Task 1 и Task 2'] as const },
  { name: 'Speaking', Icon: Mic, detail: ['AI bilan gapirish', 'Speak with AI', 'Разговор с ИИ'] as const },
] as const;

export default function DashboardPage() {
  const { t, say, user, displayName, history, free, historyLoading } = useProduct();
  if (historyLoading) return <LoadingSkeleton label={t.loading} />;

  const graded = history.filter((a) => a.state === 'graded' && a.result);
  const latest = graded[0];

  return (
    <div className="dashboard-home">
      <section className="dashboard-hero">
        <div className="dashboard-hero-copy">
          <span className="dashboard-kicker"><Sparkles size={15} /> IELTSQA · {say('O‘QUV MARKAZI', 'STUDY SPACE', 'УЧЕБНОЕ ПРОСТРАНСТВО')}</span>
          <h1>{t.welcome}{displayName ? `, ${displayName.split(' ')[0]}` : ''}!</h1>
          <p>{say('Bugungi mashqingizni tanlang va IELTS ko‘nikmalaringizni bosqichma-bosqich mustahkamlang.', 'Choose a practice and build your IELTS skills step by step.', 'Выберите тренировку и шаг за шагом развивайте навыки IELTS.')}</p>
          <div className="dashboard-hero-actions">
            <Link className="primary" href="/dashboard/full-exam"><Play size={17} />{say('To‘liq imtihonni boshlash', 'Start full exam', 'Начать полный экзамен')}</Link>
            <Link className="secondary" href="/dashboard/tests">{say('Bo‘lim testlari', 'Section tests', 'Тесты по разделам')}<ArrowRight size={17} /></Link>
          </div>
        </div>
        <Link className="dashboard-full-exam-card" href="/dashboard/full-exam">
          <div className="dashboard-full-exam-top"><span className="dashboard-full-exam-icon"><Trophy size={20} /></span><span className="dashboard-full-exam-tag">{say('TO‘LIQ IELTS', 'FULL IELTS', 'ПОЛНЫЙ IELTS')}</span></div>
          <strong>{say('To‘rtta ko‘nikma, bitta imtihon', 'Four skills, one exam', 'Четыре навыка, один экзамен')}</strong>
          <span className="dashboard-exam-sections">Listening <i /> Reading <i /> Writing <i /> Speaking</span>
          <span className="dashboard-full-exam-link">{say('Imtihon haqida', 'Explore exam', 'Открыть экзамен')}<ArrowRight size={17} /></span>
        </Link>
      </section>

      <section className="dashboard-summary dashboard-overview" aria-label={say('Natijalar va hisob', 'Results and account', 'Результаты и аккаунт')}>
        <article className="panel dashboard-stat latest-result">
          <div className="dashboard-stat-top"><span className="dashboard-stat-icon"><Trophy size={18} /></span><span className="eyebrow">{t.latest}</span></div>
          {latest ? (
            <>
              <strong>{latest.result!.assessment ? latest.result!.band?.toFixed(1) : latest.result!.correct}<small>{latest.result!.assessment ? ' AI band' : ' / ' + latest.result!.total}</small></strong>
              <p>{latest.section} · {latest.title}</p>
              <Link className="text-button" href={`/dashboard/results/${latest.id}`}>{t.details}<ArrowRight size={16} /></Link>
            </>
          ) : (
            <><h2>{t.noScore}</h2><p>{t.noScoreNote}</p></>
          )}
        </article>
        <Link className="target-card interactive-card dashboard-stat" href="/dashboard/profile" aria-label={t.target}>
          <div className="dashboard-stat-top"><span className="dashboard-stat-icon"><Target size={18} /></span><span className="eyebrow">{t.target}</span></div>
          <strong>{user!.target_band.toFixed(1)}</strong>
          <span className="target-action">{say('Maqsad bandi', 'Target band', 'Целевой балл')}<ArrowRight size={16} /></span>
        </Link>
        <article className="panel dashboard-stat">
          <div className="dashboard-stat-top"><span className="dashboard-stat-icon"><BookOpen size={18} /></span><span className="eyebrow">{t.attempts}</span></div>
          <strong className="attempt-count">{history.length}</strong>
          <p>{free ? t.free : t.used}</p>
          <Link className="text-button" href="/dashboard/results">{t.results}<ArrowRight size={16} /></Link>
        </article>
      </section>

      <div className="dashboard-section-heading">
        <div><span className="eyebrow">{say('MASHQNI TANLANG', 'PICK A PRACTICE', 'ВЫБЕРИТЕ ТРЕНИРОВКУ')}</span><h2>{say('Qaysi ko‘nikmani sinaymiz?', 'Choose your next challenge', 'Выберите следующий навык')}</h2></div>
        <Link className="text-button" href="/dashboard/tests">{say('Barcha testlar', 'All tests', 'Все тесты')}<ArrowRight size={16} /></Link>
      </div>
      <div className="product-skill-grid dashboard-skill-grid">
        {sections.map(({ name, Icon, detail }) => {
          const sectionHistory = history.filter((a) => a.section === name);
          const result = graded.find((a) => a.section === name);
          const href = name === 'Speaking' ? '/dashboard/speaking' : `/dashboard/tests?section=${name}`;
          return (
            <Link className={'panel skill-action skill-' + name.toLowerCase()} key={name} href={href}>
              <div className="dashboard-skill-top"><span className="skill-icon"><Icon size={23} /></span><span className="dashboard-skill-count">{sectionHistory.length ? `${sectionHistory.length} ${say('urinish', 'attempts', 'попыток')}` : say('Yangi', 'New', 'Новое')}</span></div>
              <div className="dashboard-skill-name"><h3>{name}</h3><p>{say(...detail)}</p></div>
              <div className="dashboard-skill-result"><span>{result ? say('Oxirgi natija', 'Latest result', 'Последний результат') : say('Hozircha natija yo‘q', 'No result yet', 'Пока нет результата')}</span><strong>{result ? (result.result!.assessment ? `${result.result!.band} AI band` : `${result.result!.correct} / ${result.result!.total}`) : '—'}</strong></div>
              <span className="skill-cta">{t.open}<ArrowRight size={18} /></span>
            </Link>
          );
        })}
      </div>

      <section className="panel dashboard-next dashboard-plan-card">
        <div className="dashboard-plan-icon"><Sparkles size={19} /></div>
        <div className="dashboard-plan-copy"><span className="eyebrow">{t.plan}</span><p>{latest ? t.planNote : t.noPlan}</p></div>
        <Link className="secondary" href="/dashboard/plan">{say('Rejani ko‘rish', 'View study plan', 'Открыть план')}<ArrowRight size={17} /></Link>
      </section>
    </div>
  );
}
