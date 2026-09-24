'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useProduct } from '@/components/product/product-context';
import { api, type Attempt } from '@/components/product/api';
import ExamRunner from '@/components/product/exam-runner';
import LoadingSkeleton from '@/components/product/loading-skeleton';

export default function ExamPage() {
  const router = useRouter();
  const params = useParams<{ examId: string }>();
  const { t, exams, history, free, load, setError } = useProduct();
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');

  useEffect(() => {
    let alive = true;
    (async () => {
      const exam = exams.find((e) => String(e.id) === params.examId);
      if (!exam) {
        // Katalog hali yuklanmagan yoki noto'g'ri ID — testlar sahifasiga qaytaramiz.
        router.replace('/dashboard/tests');
        return;
      }
      const resuming = history.find((a) => a.state === 'in_progress' && a.section === exam.section && a.title === exam.title);
      try {
        if (resuming) {
          const a = await api<Attempt>(`attempts/${resuming.id}/`);
          if (alive) { setAttempt(a); setStatus('ready'); }
          return;
        }
        if (!free && !exam.has_access) {
          router.replace(`/dashboard/payments?exam=${encodeURIComponent(exam.title)}`);
          return;
        }
        const a = await api<Attempt>('attempts/', 'POST', { exam_id: exam.id, accept_pending_assessment: exam.section === 'Writing' });
        await load();
        if (alive) { setAttempt(a); setStatus('ready'); }
      } catch (e) {
        if (alive) { setError((e as Error).message); setStatus('error'); }
      }
    })();
    return () => { alive = false; };
    // exams/history faqat boshlang'ich holatni aniqlash uchun ishlatiladi — qayta yuklanish shart emas.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.examId]);

  // Baholash kutilayotganda polling.
  useEffect(() => {
    if (!attempt || attempt.state !== 'awaiting_assessment' || attempt.assessment_status === 'failed' || attempt.assessment_status === 'disabled') return;
    let alive = true;
    let pending = false;
    const id = setInterval(() => {
      if (pending) return;
      pending = true;
      api<Attempt>(`attempts/${attempt.id}/`)
        .then((a) => { if (!alive) return; setAttempt(a); if (a.state === 'graded') void load(true).catch(() => {}); })
        .catch(() => {})
        .finally(() => { pending = false; });
    }, 5000);
    return () => { alive = false; clearInterval(id); };
  }, [attempt, load]);

  if (status === 'loading') return <LoadingSkeleton label={t.loading} />;
  if (status === 'error' || !attempt) return <LoadingSkeleton label={t.loading} />;

  if (attempt.state === 'in_progress') {
    return (
      <ExamRunner
        attempt={attempt}
        t={t}
        onClose={() => { void load().catch(() => {}); router.push('/dashboard/tests'); }}
        onComplete={(a) => router.push(`/dashboard/results/${a.id}`)}
      />
    );
  }
  // Allaqachon topshirilgan/baholangan bo'lsa — natija sahifasiga yo'naltiramiz.
  router.replace(`/dashboard/results/${attempt.id}`);
  return <LoadingSkeleton label={t.loading} />;
}
