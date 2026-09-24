'use client';
import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useProduct } from '@/components/product/product-context';
import SiteHeader from '@/components/product/site-header';
import LoadingSkeleton from '@/components/product/loading-skeleton';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { ready, available, user, t, error, notice, connect } = useProduct();
  // Imtihon topshirish sahifasida (tests/[examId]) header/footer yashiriladi — diqqat chalg'imasin.
  const isExam = /^\/dashboard\/tests\/[^/]+$/.test(pathname);

  useEffect(() => {
    if (ready && (!available || !user)) router.replace('/login');
  }, [ready, available, user, router]);

  if (!ready) return <main className="workspace loading-shell"><LoadingSkeleton label={t.loading} /></main>;
  if (!available) {
    return (
      <main className="workspace product-login">
        <section className="panel">
          <h1>IELTSQA</h1>
          <h2>{t.unavailable}</h2>
          <p>{t.unavailableNote}</p>
          <p role="alert">{error}</p>
          <button className="primary" onClick={() => void connect()}>{t.retry}</button>
        </section>
      </main>
    );
  }
  if (!user) return null;

  return (
    <div className={'workspace product-shell top-navigation ' + (isExam ? 'is-exam' : '')}>
      {!isExam && <SiteHeader />}
      <main className="product-main">
        <div className="product-body">
          {error && <div className="product-alert no-print" role="alert">{error}</div>}
          {notice && <div className="product-success" role="status">{notice}</div>}
          {children}
        </div>
      </main>
      {!isExam && <footer className="product-footer">IELTSQA · {t.brand}</footer>}
    </div>
  );
}
