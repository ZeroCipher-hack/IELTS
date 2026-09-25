'use client';
import { useEffect } from 'react';

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error(error);
  }, [error]);

  return (
    <html lang="uz">
      <body style={{ fontFamily: 'system-ui, sans-serif', background: '#FFF8EC', color: '#1A1A2E', minHeight: '100dvh', display: 'grid', placeItems: 'center', padding: 24 }}>
        <div style={{ maxWidth: 420, textAlign: 'center' }}>
          <h1 style={{ fontSize: 24, fontWeight: 800 }}>Nimadir noto‘g‘ri ketdi</h1>
          <p style={{ marginTop: 12, color: '#756E5C' }}>
            Sahifa yuklanmadi. Iltimos, qayta urinib ko‘ring.
          </p>
          <button
            onClick={reset}
            style={{ marginTop: 20, background: '#3654E0', color: '#fff', border: 'none', borderRadius: 999, padding: '12px 24px', fontWeight: 700, cursor: 'pointer' }}
          >
            Qayta urinish
          </button>
        </div>
      </body>
    </html>
  );
}
