'use client';
import Link from 'next/link';
import { ArrowRight, CalendarDays } from 'lucide-react';
import { useProduct } from '@/components/product/product-context';
import LoadingSkeleton from '@/components/product/loading-skeleton';

export default function PlanPage() {
  const { t, say, history, historyLoading } = useProduct();
  if (historyLoading) return <LoadingSkeleton label={t.loading} />;

  const graded = history.filter((a) => a.state === 'graded' && a.result);
  const latest = graded[0];

  return (
    <>
      <div className="page-heading plan-heading"><div><h1>{t.plan}</h1><p>{latest ? t.planNote : t.noPlan}</p></div></div>
      {!latest && (
        <section className="empty-workspace">
          <CalendarDays aria-hidden="true" />
          <h2>{say('Rejangiz natijadan boshlanadi', 'Your plan starts with a result', 'Ваш план начинается с результата')}</h2>
          <p>{t.noPlan}</p>
          <Link className="primary" href="/dashboard/tests">{t.newExam}<ArrowRight size={18} /></Link>
        </section>
      )}
      {latest && (
        <>
          <p className="badge">{latest.title}</p>
          {latest.result?.assessment ? (
            <div className="product-plan">
              {latest.result.assessment.tasks.map((task) => (
                <section className="panel" key={task.position}>
                  <h2>{latest.section === 'Speaking' ? 'Speaking' : 'Task ' + task.position}</h2>
                  <p>{task.improvement}</p>
                </section>
              ))}
            </div>
          ) : latest.result?.weekly_plan?.length ? (
            <div className="product-plan">
              {Array.from({ length: 7 }, (_, i) => {
                const items = latest.result!.weekly_plan!;
                const item = items[Math.floor(i / 2) % items.length];
                return (
                  <section className="panel plan-day" key={i}>
                    <span className="plan-number">{String(i + 1).padStart(2, '0')}</span>
                    <div>
                      <span className="eyebrow">{t.day} {i + 1} · 20 {t.minutes}</span>
                      <h2>{i === 6 ? t.results : item.tag}</h2>
                      <p>{i === 6 ? t.reflectTask : i % 2 ? t.practiceTask : t.reviewTask}</p>
                      <p className="product-muted">{t.questions}: {item.question_positions.join(', ')} · {item.wrong} / {item.total} {t.wrong.toLowerCase()}</p>
                      <Link className="text-button" href={`/dashboard/results/${latest.id}`}>{t.details}<ArrowRight size={16} /></Link>
                    </div>
                  </section>
                );
              })}
            </div>
          ) : (
            <p className="panel">{t.noMistakes}</p>
          )}
        </>
      )}
    </>
  );
}
