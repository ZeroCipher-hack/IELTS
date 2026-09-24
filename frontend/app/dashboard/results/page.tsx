'use client';
import Link from 'next/link';
import { ArrowRight, BarChart3 } from 'lucide-react';
import { useProduct } from '@/components/product/product-context';
import LoadingSkeleton from '@/components/product/loading-skeleton';

export default function ResultsPage() {
  const { t, history, historyLoading, language, exams } = useProduct();
  if (historyLoading) return <LoadingSkeleton label={t.loading} view="results" />;

  const status = (a: (typeof history)[number]) => (a.state === 'graded' ? t.graded : a.state === 'in_progress' ? t.progress : t.pending);
  // Attempt'da exam_id yo'q — davom etayotgan urinishni section+title bo'yicha katalogdagi examga bog'laymiz.
  const resumeHref = (a: (typeof history)[number]) => {
    const exam = exams.find((e) => e.section === a.section && e.title === a.title);
    return exam ? `/dashboard/tests/${exam.id}` : '/dashboard/tests';
  };

  return (
    <>
      <div className="page-heading"><div><h1>{t.results}</h1><p>{t.historyNote}</p></div></div>
      <section className="panel history-panel">
        {history.length ? (
          <div className="history-table">
            <div className="history-table-head"><span>{t.tests}</span><span>{t.date}</span><span>{t.score}</span><span>{t.status}</span><span /></div>
            {history.map((a) => (
              <div className="history-table-row" key={a.id}>
                <div><strong>{a.title}</strong><small>{a.section}</small></div>
                <span>{new Date(a.started_at).toLocaleDateString(language)}</span>
                <strong>{a.result ? (a.result.assessment ? `${a.result.band} AI band` : `${a.result.correct} / ${a.result.total}`) : '—'}</strong>
                <span>{status(a)}</span>
                <Link className="text-button" href={a.state === 'in_progress' ? resumeHref(a) : `/dashboard/results/${a.id}`}>
                  {a.state === 'in_progress' ? t.resume : t.open}<ArrowRight size={15} />
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-workspace">
            <BarChart3 aria-hidden="true" />
            <h2>{t.noScore}</h2>
            <p>{t.emptyHistory}</p>
            <Link className="primary" href="/dashboard/tests">{t.newExam}<ArrowRight size={18} /></Link>
          </div>
        )}
      </section>
    </>
  );
}
