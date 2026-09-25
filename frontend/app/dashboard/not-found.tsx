import Link from 'next/link';
import { Compass } from 'lucide-react';

export default function DashboardNotFound() {
  return (
    <section className="panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 16 }}>
      <Compass size={32} color="var(--muted-foreground)" />
      <h2>Sahifa topilmadi</h2>
      <p className="product-muted">Siz izlagan bo‘lim mavjud emas yoki ko‘chirilgan.</p>
      <Link className="primary" href="/dashboard">Bosh sahifaga qaytish</Link>
    </section>
  );
}
