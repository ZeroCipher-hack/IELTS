'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowRight, BookOpen, Headphones, LockKeyhole, Mic, PenLine, Sparkles } from 'lucide-react';
import { useProduct } from '@/components/product/product-context';
import LoadingSkeleton from '@/components/product/loading-skeleton';

const sections = [
  { name: 'Listening', Icon: Headphones, detail: 'Audio · 4 parts' },
  { name: 'Reading', Icon: BookOpen, detail: 'Passages · 3 parts' },
  { name: 'Writing', Icon: PenLine, detail: 'Essay · 2 tasks' },
  { name: 'Speaking', Icon: Mic, detail: 'Conversation · 3 parts' },
] as const;

export default function TestsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { t, say, exams, free, history, catalogLoading, busy } = useProduct();
  const [sectionFilter, setSectionFilter] = useState(searchParams.get('section') || 'All');

  if (catalogLoading) return <LoadingSkeleton label={t.loading} view="tests" />;

  async function start(exam: (typeof exams)[number]) {
    if (!free && !exam.has_access && !history.some((a) => a.state === 'in_progress' && a.section === exam.section && a.title === exam.title)) {
      router.push(`/dashboard/payments?exam=${encodeURIComponent(exam.title)}`);
      return;
    }
    if (exam.section === 'Writing' && !window.confirm(t.writingNotice)) return;
    router.push(`/dashboard/tests/${exam.id}`);
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">{say('KEYINGI QADAM', 'YOUR NEXT STEP', 'СЛЕДУЮЩИЙ ШАГ')}</span>
          <h1>{t.tests}</h1>
          <p>{free ? t.free : t.used}</p>
        </div>
        <Link className="secondary" href="/dashboard/results">{t.results}<ArrowRight size={17} /></Link>
      </div>

      <section className="full-test premium-exam">
        <div>
          <span className="badge"><Sparkles size={14} /> IELTS ACADEMIC</span>
          <h2>{t.fullExam}</h2>
          <p>Listening · Reading · Writing · Speaking</p>
          <p className="availability-note">{t.fullNote}</p>
          <span className="premium-price">≈ 200 000 UZS</span>
        </div>
        <Link className="secondary" href="/dashboard/payments?exam=IELTS%20Academic">
          <LockKeyhole size={18} />{say('Mavjudlik holati', 'Availability details', 'Статус доступа')}<ArrowRight size={18} />
        </Link>
      </section>

      <div className="test-filters">
        {['All', ...sections.map((s) => s.name)].map((name) => (
          <button key={name} aria-pressed={sectionFilter === name} onClick={() => setSectionFilter(name)}>
            {name === 'All' ? say('Barchasi', 'All', 'Все') : name}
          </button>
        ))}
      </div>

      <div className="product-test-grid">
        {sections
          .filter((s) => sectionFilter === 'All' || s.name === sectionFilter)
          .flatMap(({ name, Icon, detail }) => {
            const entries = exams.filter((e) => e.section === name);
            if (entries.length) {
              return entries.map((exam) => {
                const locked = (!free && !exam.has_access) || name === 'Speaking';
                return (
                  <section className={'panel exam-card skill-' + name.toLowerCase()} key={exam.id}>
                    <div className="exam-card-top">
                      <span className="skill-icon"><Icon size={24} /></span>
                      <span className="access-badge">
                        {locked ? (
                          <><LockKeyhole size={13} />{name === 'Speaking' ? say('Ovozli mashq', 'Voice practice', 'Голосовая практика') : say('Pullik', 'Paid', 'Платно')}</>
                        ) : free ? t.free : say('Kirish mavjud', 'Access granted', 'Доступ открыт')}
                      </span>
                    </div>
                    <span className="eyebrow">{name}</span>
                    <h2>{exam.title}</h2>
                    {name === 'Speaking' && (
                      <p className="availability-note">
                        {say('Ovozli imtihon tayyorlanmoqda. Ochilish sanasi hali belgilanmagan.', 'The voice exam is in development. A launch date has not been set.', 'Голосовой экзамен в разработке. Дата запуска ещё не определена.')}
                      </p>
                    )}
                    <p>{exam.question_count} {t.questions} · {Math.round(exam.duration_seconds / 60)} {t.minutes}</p>
                    <button
                      className={locked ? 'secondary' : 'primary'}
                      disabled={busy}
                      onClick={() => (name === 'Speaking' ? router.push('/dashboard/speaking') : void start(exam))}
                    >
                      {locked ? <LockKeyhole size={16} /> : <ArrowRight size={16} />}{' '}
                      {name === 'Speaking' ? say('Ovozli mashq', 'Voice practice', 'Голосовая практика') : locked ? say('Mavjudlik holati', 'Availability details', 'Статус доступа') : t.start}
                    </button>
                  </section>
                );
              });
            }
            return [
              <section className={'panel exam-card skill-' + name.toLowerCase()} key={name}>
                <div className="exam-card-top">
                  <span className="skill-icon"><Icon size={24} /></span>
                  <span className="access-badge"><LockKeyhole size={13} />{t.soon}</span>
                </div>
                <span className="eyebrow">IELTS ACADEMIC</span>
                <h2>{name}</h2>
                <p>{detail}</p>
                <p className="availability-note">
                  {name === 'Speaking'
                    ? say('Ovozli imtihon tayyorlanmoqda. Ochilish sanasi hali belgilanmagan.', 'The voice exam is in development. A launch date has not been set.', 'Голосовой экзамен в разработке. Дата запуска ещё не определена.')
                    : say('Test materiallari hali nashr qilinmagan.', 'Test materials have not been published yet.', 'Материалы теста ещё не опубликованы.')}
                </p>
                <button className="secondary" onClick={() => (name === 'Speaking' ? router.push('/dashboard/speaking') : router.push(`/dashboard/payments?exam=${encodeURIComponent(name)}`))}>
                  {name === 'Speaking' ? <Mic size={16} /> : <LockKeyhole size={16} />}{' '}
                  {name === 'Speaking' ? say('Ovozli mashq', 'Voice practice', 'Голосовая практика') : say('Mavjudlik holati', 'Availability details', 'Статус доступа')}
                  <ArrowRight size={16} />
                </button>
              </section>,
            ];
          })}
      </div>
    </>
  );
}
