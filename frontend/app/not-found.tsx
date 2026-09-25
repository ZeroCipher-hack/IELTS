import Link from 'next/link';

export default function NotFound() {
  return (
    <main style={{ minHeight: '100dvh', display: 'grid', placeItems: 'center', background: '#FFF8EC', color: '#1A1A2E', fontFamily: 'system-ui, sans-serif', padding: 24 }}>
      <div style={{ maxWidth: 420, textAlign: 'center' }}>
        <span style={{ fontSize: 13, fontWeight: 700, letterSpacing: 1, color: '#756E5C', textTransform: 'uppercase' }}>404</span>
        <h1 style={{ fontSize: 26, fontWeight: 800, marginTop: 8 }}>Sahifa topilmadi</h1>
        <p style={{ marginTop: 10, color: '#756E5C' }}>Siz izlagan manzil mavjud emas yoki ko‘chirilgan.</p>
        <Link
          href="/"
          style={{ display: 'inline-block', marginTop: 20, background: '#3654E0', color: '#fff', borderRadius: 999, padding: '12px 24px', fontWeight: 700, textDecoration: 'none' }}
        >
          Bosh sahifaga qaytish
        </Link>
      </div>
    </main>
  );
}
