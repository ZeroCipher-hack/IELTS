'use client';
import Link from 'next/link';
import { ArrowRight, BookOpen, Headphones, Mic, PenLine, Plus, Target } from 'lucide-react';
import { useProduct } from '@/components/product/product-context';
import LoadingSkeleton from '@/components/product/loading-skeleton';

const sections = [
  { name: 'Listening', Icon: Headphones, detail: 'Audio · 4 parts' },
  { name: 'Reading', Icon: BookOpen, detail: 'Passages · 3 parts' },
  { name: 'Writing', Icon: PenLine, detail: 'Essay · 2 tasks' },
  { name: 'Speaking', Icon: Mic, detail: 'Conversation · 3 parts' },
] as const;

export default function DashboardPage() {
  const { t, say, user, displayName, history, free, historyLoading } = useProduct();
  if (historyLoading) return <LoadingSkeleton label={t.loading} />;

  const graded = history.filter((a) => a.state === 'graded' && a.result);
  const latest = graded[0];

  return (
    <>
      <div className="page-heading dashboard-welcome">
        <div>
          <span className="eyebrow">{say('SIZNING IELTS YO‘LINGIZ', 'YOUR IELTS JOURNEY', 'ВАШ ПУТЬ К IELTS')}</span>
          <h1>{t.welcome}{displayName ? `, ${displayName.split(' ')[0]}` : ''}!</h1>
          <p>{t.subtitle}</p>
        </div>
        <Link className="primary" href="/dashboard/tests"><Plus size={18} />{t.newExam}</Link>
      </div>
      <div className="dashboard-summary">
        <section className="panel latest-result">
          <span className="eyebrow">{t.latest}</span>
          {latest ? (
            <>
              <strong>{latest.result!.assessment ? latest.result!.band?.toFixed(1) : latest.result!.correct}<small>{latest.result!.assessment ? ' AI band' : ' / ' + latest.result!.total}</small></strong>
              <p>{latest.section} · {latest.title}</p>
              <Link className="text-button" href={`/dashboard/results/${latest.id}`}>{t.details}<ArrowRight size={16} /></Link>
            </>
          ) : (
            <>
              <h2>{t.noScore}</h2>
              <p>{t.noScoreNote}</p>
            </>
          )}
        </section>
        <Link className="target-card interactive-card" href="/dashboard/profile" aria-label={t.target}>
          <Target size={23} /><span>{t.target}</span><strong>{user!.target_band.toFixed(1)}</strong>
          <span className="target-action">{say('Maqsadni o‘zgartirish', 'Edit target', 'Изменить цель')} <ArrowRight size={16} /></span>
        </Link>
        <section className="panel">
          <span className="eyebrow">{t.attempts}</span>
          <strong className="attempt-count">{history.length}</strong>
          <p>{free ? t.free : t.used}</p>
          <Link className="text-button" href="/dashboard/results">{t.results}<ArrowRight size={16} /></Link>
        </section>
      </div>
      <div className="section-title">
        <h2>{say('Qaysi ko‘nikmani sinaymiz?', 'Choose your next challenge', 'Выберите навык')}</h2>
        <Link className="text-button" href="/dashboard/tests">{t.tests}<ArrowRight size={16} /></Link>
      </div>
      <div className="product-skill-grid">
        {sections.map(({ name, Icon, detail }) => {
          const a = graded.find((a) => a.section === name);
          const href = name === 'Speaking' ? '/dashboard/speaking' : `/dashboard/tests?section=${name}`;
          return (
            <Link className={'panel skill-action skill-' + name.toLowerCase()} key={name} href={href}>
              <span className="skill-icon"><Icon size={24} /></span>
              <h3>{name}</h3>
              <p>{detail}</p>
              <strong>{a ? (a.result!.assessment ? `${a.result!.band} AI band` : `${a.result!.correct} / ${a.result!.total}`) : '—'}</strong>
              <span className="skill-cta">{t.open}<ArrowRight size={18} /></span>
            </Link>
          );
        })}
      </div>
      <section className="panel dashboard-next">
        <div><span className="eyebrow">{t.plan}</span><p>{latest ? t.planNote : t.noPlan}</p></div>
        <Link className="secondary" href="/dashboard/plan">{t.open}<ArrowRight size={17} /></Link>
      </section>
    </>
  );
}
