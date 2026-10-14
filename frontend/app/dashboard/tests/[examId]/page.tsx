'use client';
import { useEffect, useRef, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useProduct } from '@/components/product/product-context';
import { api, type Attempt } from '@/components/product/api';
import ExamRunner from '@/components/product/exam-runner';
import SpeakingExam from '@/components/product/speaking-exam';
import LoadingSkeleton from '@/components/product/loading-skeleton';

export default function ExamPage() {
  const router = useRouter();
  const params = useParams<{ examId: string }>();
  const { t, say, exams, history, free, load, setError } = useProduct();
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');

  // One start per exam id. React runs effects twice in development, and a double
  // POST raced itself into a locked row; a second tab or a double click would do
  // the same in production. Both runs await the SAME request, so whichever
  // effect survives is the one that sets the state.
  const pending = useRef<{ id: string; promise: Promise<Attempt | null> } | null>(null);

  useEffect(() => {
    let alive = true;
    const examId = params.examId;

    if (!pending.current || pending.current.id !== examId) {
      pending.current = {
        id: examId,
        promise: (async () => {
          const exam = exams.find((e) => String(e.id) === examId);
          if (!exam) {
            // Katalog hali yuklanmagan yoki noto'g'ri ID — testlar sahifasiga qaytaramiz.
            router.replace('/dashboard/tests');
            return null;
          }
          const resuming = history.find((a) => a.state === 'in_progress' && a.section === exam.section && a.title === exam.title);
          if (resuming) return api<Attempt>(`attempts/${resuming.id}/`);
          if (!free && !exam.has_access) {
            router.replace(`/dashboard/payments?exam=${encodeURIComponent(exam.title)}`);
            return null;
          }
          const a = await api<Attempt>('attempts/', 'POST', { exam_id: exam.id, accept_pending_assessment: exam.section === 'Writing' });
          await load();
          return a;
        })(),
      };
    }

    pending.current.promise.then(
      (a) => { if (alive && a) { setAttempt(a); setStatus('ready'); } },
      (e: Error) => { pending.current = null; if (alive) { setError(e.message); setStatus('error'); } },
    );

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
    // Speaking runs a scripted interview, not the written-answer runner.
    if (attempt.section === 'Speaking') {
      return (
        <SpeakingExam
          attempt={attempt}
          t={t}
          say={say}
          onClose={() => { void load().catch(() => {}); router.push('/dashboard/tests'); }}
          onComplete={(a) => router.push(`/dashboard/results/${a.id}`)}
        />
      );
    }
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
