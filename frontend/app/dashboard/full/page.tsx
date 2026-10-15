'use client';
import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, type Sitting } from '@/components/product/api';
import { useProduct } from '@/components/product/product-context';
import LoadingSkeleton from '@/components/product/loading-skeleton';

/**
 * Opens a full sitting, or re-opens the one already running.
 *
 * The POST is idempotent on the server: an unfinished sitting is returned
 * rather than a second one created, so a refresh here never splits a
 * candidate's exam in two.
 */
export default function StartFullExamPage() {
  const router = useRouter();
  const { t, say, setError } = useProduct();
  const [failed, setFailed] = useState('');
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    api<Sitting>('sessions/', 'POST', {})
      .then((s) => router.replace(`/dashboard/full/${s.id}`))
      .catch((e: Error) => { setFailed(e.message); setError(e.message); });
  }, [router, setError]);

  if (!failed) return <LoadingSkeleton label={t.loading} />;
  return (
    <section className="panel">
      <h1>{say('To‘liq imtihon boshlanmadi', 'The full exam could not start', 'Полный экзамен не начался')}</h1>
      <p role="alert">{failed}</p>
      <button className="primary" onClick={() => router.push('/dashboard/tests')}>{t.tests}</button>
    </section>
  );
}
