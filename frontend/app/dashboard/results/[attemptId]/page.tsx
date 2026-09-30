'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useProduct } from '@/components/product/product-context';
import { api, type Attempt } from '@/components/product/api';
import ResultReport from '@/components/product/result-report';
import LoadingSkeleton from '@/components/product/loading-skeleton';

export default function ResultDetailPage() {
  const router = useRouter();
  const params = useParams<{ attemptId: string }>();
  const { t, language, setError, load } = useProduct();
  const [refreshing, setRefreshing] = useState(false);
  const [attempt, setAttempt] = useState<Attempt | null>(null);

  useEffect(() => {
    let alive = true;
    api<Attempt>(`attempts/${params.attemptId}/`)
      .then((a) => { if (alive) setAttempt(a); })
      .catch((e) => setError((e as Error).message));
    return () => { alive = false; };
  }, [params.attemptId, setError]);

  // Hali baholanmagan bo'lsa — polling.
  useEffect(() => {
    if (!attempt || !(attempt.state === 'awaiting_assessment' && attempt.assessment_status !== 'failed' && attempt.assessment_status !== 'disabled') && !(['pending','running'].includes(attempt.tutoring_status || '') && !attempt.result?.tutoring)) return;
    let alive = true;
    let pending = false;
    const id = setInterval(() => {
      if (pending) return;
      pending = true;
      api<Attempt>(`attempts/${attempt.id}/`)
        .then((a) => { if (!alive) return; setAttempt(a); if (attempt.state === 'awaiting_assessment' && a.state === 'graded') void load(true).catch(() => {}); })
        .catch(() => {})
        .finally(() => { pending = false; });
    }, 5000);
    return () => { alive = false; clearInterval(id); };
  }, [attempt, load]);

  async function refresh() {
    setRefreshing(true);
    try { setAttempt(await api<Attempt>(`attempts/${params.attemptId}/`)); }
    catch (error) { setError((error as Error).message); }
    finally { setRefreshing(false); }
  }

  if (!attempt) return <LoadingSkeleton label={t.loading} />;

  return (
    <>
      <button className="text-button no-print" onClick={() => router.back()}>← {t.back}</button>
      <ResultReport attempt={attempt} t={t} language={language} refreshing={refreshing} onRefresh={()=>void refresh()} />
    </>
  );
}
