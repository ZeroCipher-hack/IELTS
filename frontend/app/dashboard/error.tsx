'use client';
import { useEffect } from 'react';
import Link from 'next/link';
import { RefreshCw, TriangleAlert } from 'lucide-react';

export default function DashboardError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error(error);
  }, [error]);

  return (
    <section className="panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 16 }}>
      <TriangleAlert size={32} color="var(--destructive)" />
      <h2>Nimadir noto‘g‘ri ketdi</h2>
      <p className="product-muted">
        Sahifani ko‘rsatishda kutilmagan xatolik yuz berdi. Qayta urinib ko‘ring — agar takrorlansa, boshqa
        bo‘limga o‘tib qayta kirishga harakat qiling.
      </p>
      <div style={{ display: 'flex', gap: 12 }}>
        <button className="primary" onClick={reset}><RefreshCw size={16} />Qayta urinish</button>
        <Link className="secondary" href="/dashboard">Bosh sahifaga qaytish</Link>
      </div>
    </section>
  );
}
