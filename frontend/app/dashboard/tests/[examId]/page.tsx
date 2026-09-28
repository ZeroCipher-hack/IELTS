'use client';
import { useEffect, useRef, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { useProduct } from '@/components/product/product-context';
import { api, type Attempt } from '@/components/product/api';
import ExamRunner from '@/components/product/exam-runner';
import LoadingSkeleton from '@/components/product/loading-skeleton';

export default function ExamPage() {
  const router = useRouter();
  const params = useParams<{ examId: string }>();
  const searchParams = useSearchParams();
  const { t, exams, history, free, load, setError } = useProduct();
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const startRequest = useRef<{ examId: string; promise: Promise<Attempt> } | null>(null);

  useEffect(() => {
    let alive = true;
    const examId = params.examId;
    let request = startRequest.current?.examId === examId ? startRequest.current.promise : null;

    if (!request) {
      request = (async () => {
        const exam = exams.find((e) => String(e.id) === examId);
        if (!exam) {
          router.replace('/dashboard/tests');
          throw new Error('Test topilmadi.');
        }
        const resuming = history.find((a) => a.state === 'in_progress' && a.section === exam.section && a.title === exam.title);
        if (resuming) return api<Attempt>(`attempts/${resuming.id}/`);
        if (!free && !exam.has_access) {
          router.replace(`/dashboard/payments?exam=${encodeURIComponent(exam.title)}`);
          throw new Error('Bu testga kirish huquqi yo‘q.');
        }
        const attempt = await api<Attempt>('attempts/', 'POST', {
          exam_id: exam.id,
          accept_pending_assessment: exam.section === 'Writing',
        });
        await load();
        return attempt;
      })();
      startRequest.current = { examId, promise: request };
    }

    // React Strict Mode development rejimida effect’ni qayta chaqirishi mumkin.
    // Bir examId uchun bitta POST va shu Promise natijasini ulashamiz.
    request
      .then((value) => {
        if (alive) {
          setAttempt(value);
          setStatus('ready');
        }
      })
      .catch((error: unknown) => {
        if (alive) {
          setError((error as Error).message);
          setStatus('error');
        }
        if (startRequest.current?.examId === examId) startRequest.current = null;
      });

    return () => { alive = false; };
    // exams/history faqat boshlang‘ich holatni aniqlash uchun ishlatiladi.
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
        onComplete={(a) => {
          if (searchParams.get('full') !== '1') { router.push(`/dashboard/results/${a.id}`); return; }
          try {
            const flow = JSON.parse(localStorage.getItem('ieltsqa-full-exam') || '{}') as { ids?: number[]; step?: number; attempts?: string[] };
            flow.attempts = [...(flow.attempts || []), a.id];
            flow.step = (flow.step || 0) + 1;
            localStorage.setItem('ieltsqa-full-exam', JSON.stringify(flow));
            if (flow.ids && flow.step < flow.ids.length) router.push(`/dashboard/tests/${flow.ids[flow.step]}?full=1`);
            else router.push('/dashboard/speaking?full=1');
          } catch { router.push(`/dashboard/results/${a.id}`); }
        }}
      />
    );
  }
  // Allaqachon topshirilgan/baholangan bo'lsa — natija sahifasiga yo'naltiramiz.
  router.replace(`/dashboard/results/${attempt.id}`);
  return <LoadingSkeleton label={t.loading} />;
}
