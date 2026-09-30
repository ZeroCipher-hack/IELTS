'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { useProduct } from '@/components/product/product-context';
import { api, type Attempt } from '@/components/product/api';
import {completeFullExamSection, fullExamKey, nextFullExamPath, parseFullExamFlow} from '@/components/product/full-exam-flow';
import ExamRunner from '@/components/product/exam-runner';
import LoadingSkeleton from '@/components/product/loading-skeleton';

export default function ExamPage() {
  const router = useRouter();
  const params = useParams<{ examId: string }>();
  const searchParams = useSearchParams();
  const { t, exams, history, free, openAccess, catalogLoading, load, setError } = useProduct();
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [activeExamId, setActiveExamId] = useState('');
  const [startError, setStartError] = useState('');
  const [retryKey, setRetryKey] = useState(0);
  const startRequest = useRef<{ examId: string; promise: Promise<Attempt> } | null>(null);

  useEffect(() => {
    if (catalogLoading) return;
    let alive = true;
    const examId = params.examId;
    if (searchParams.get('full') === '1') {
      const flow = parseFullExamFlow(localStorage.getItem(fullExamKey));
      if (!flow) { router.replace('/dashboard/full-exam'); return; }
      if (flow.ids[flow.step] !== Number(examId)) { router.replace(nextFullExamPath(flow)); return; }
    }
    let request = startRequest.current?.examId === examId ? startRequest.current.promise : null;

    if (!request) {
      request = (async () => {
        const exam = exams.find((e) => String(e.id) === examId);
        if (!exam) throw new Error('Test topilmadi.');
        const resuming = history.find((a) => a.state === 'in_progress' && a.section === exam.section && a.title === exam.title);
        if (resuming) return api<Attempt>(`attempts/${resuming.id}/`);
        if (!openAccess && !free && !exam.has_access) {
          router.replace(`/dashboard/payments?exam=${encodeURIComponent(exam.title)}`);
          throw new Error('Bu testga kirish huquqi yo‘q.');
        }
        const created = await api<Attempt>('attempts/', 'POST', {
          exam_id: exam.id,
          accept_pending_assessment: exam.section === 'Writing',
        });
        // The attempt exists even if a background catalog refresh fails.
        void load(true).catch(() => {});
        return created;
      })();
      startRequest.current = { examId, promise: request };
    }

    // Reuse the same request when React Strict Mode repeats this effect.
    request
      .then((value) => {
        if (alive) {
          setAttempt(value);
          setActiveExamId(examId);
          setStatus('ready');
        }
      })
      .catch((error: unknown) => {
        if (alive) {
          const message = (error as Error).message;
          setStartError(message);
          setError(message);
          setStatus('error');
        }
        if (startRequest.current?.examId === examId) startRequest.current = null;
      });

    return () => { alive = false; };
    // Catalog/history values are read when this exam first opens.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.examId, catalogLoading, retryKey]);

  const showCompleted = useCallback((a: Attempt) => {
          if (searchParams.get('full') !== '1') { router.push(`/dashboard/results/${a.id}`); return; }
          try {
            const saved = parseFullExamFlow(localStorage.getItem(fullExamKey));
            if (!saved) throw new Error('Missing full exam flow.');
            const flow = completeFullExamSection(saved, Number(params.examId), a.id);
            localStorage.setItem(fullExamKey, JSON.stringify(flow));
            router.push(nextFullExamPath(flow));
          } catch { router.push(`/dashboard/results/${a.id}`); }
  }, [params.examId, router, searchParams]);
  useEffect(() => {
    if (status === 'ready' && attempt && attempt.state !== 'in_progress') showCompleted(attempt);
  }, [status, attempt, showCompleted]);

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

  if (status === 'error') return (
    <section className="panel exam-start-error" role="alert">
      <h1>{t.tests}</h1>
      <p>{startError || 'Testni boshlashda xatolik yuz berdi.'}</p>
      <div>
        <button className="primary" onClick={() => { setStatus('loading'); setStartError(''); setRetryKey((key) => key + 1); }}>{t.retry}</button>
        <button className="secondary" onClick={() => router.push(searchParams.get('full') === '1' ? '/dashboard/full-exam' : '/dashboard/tests')}>{t.back}</button>
      </div>
    </section>
  );
  if (catalogLoading || status === 'loading' || !attempt || activeExamId !== params.examId) return <LoadingSkeleton label={t.loading} />;

  if (attempt.state === 'in_progress') {
    return (
      <ExamRunner
        attempt={attempt}
        t={t}
        onClose={() => { void load().catch(() => {}); router.push(searchParams.get('full') === '1' ? '/dashboard/full-exam' : '/dashboard/tests'); }}
        onComplete={showCompleted}
      />
    );
  }
  // Allaqachon topshirilgan/baholangan bo'lsa — natija sahifasiga yo'naltiramiz.
  return <LoadingSkeleton label={t.loading} />;
}
