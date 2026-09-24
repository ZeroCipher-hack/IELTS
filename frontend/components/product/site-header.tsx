'use client';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { AudioLines, BarChart3, BookOpen, CalendarDays, CreditCard, Home, LogOut, UserRound, ArrowRight } from 'lucide-react';
import { useProduct } from './product-context';
import ThemeToggle from './theme-toggle';
import type { Language } from './api';

export default function SiteHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const { t, say, language, setLanguage, user, displayName, busy, logout } = useProduct();
  if (!user) return null;

  const nav = [
    ['/dashboard', t.dashboard, Home],
    ['/dashboard/tests', t.tests, BookOpen],
    ['/dashboard/results', t.results, BarChart3],
    ['/dashboard/analytics', say('Analitika', 'Analytics', 'Аналитика'), BarChart3],
    ['/dashboard/plan', t.plan, CalendarDays],
    ['/dashboard/payments', say('To‘lovlar', 'Payments', 'Оплата'), CreditCard],
  ] as const;

  const languages = (
    <select aria-label={t.language} value={language} onChange={(e) => setLanguage(e.target.value as Language)}>
      <option value="uz">UZ</option>
      <option value="en">EN</option>
      <option value="ru">RU</option>
    </select>
  );

  return (
    <header className="site-header no-print">
      <div className="header-content">
        <div className="header-account-row">
          <Link className="product-logo" aria-label={t.dashboard} href="/dashboard">
            <AudioLines />IELTS<span>QA</span>
          </Link>
          <div className="header-account-actions">
            {languages}
            <ThemeToggle language={language} />
            <Link className="header-profile" aria-label={t.profile} aria-current={pathname === '/dashboard/profile' ? 'page' : undefined} href="/dashboard/profile">
              <span className="avatar">{user.avatar ? <img src={user.avatar} alt="" /> : displayName.slice(0, 1).toUpperCase() || <UserRound size={18} />}</span>
              <span className="header-profile-copy"><strong>{displayName || t.profile}</strong><small>{t.profile}</small></span>
              <ArrowRight size={16} />
            </Link>
            <button className="header-logout" aria-label={t.logout} title={t.logout} disabled={busy} onClick={() => void logout().then(() => router.push('/login'))}>
              <LogOut size={18} />
            </button>
          </div>
        </div>
        <nav className="header-navigation" aria-label={say('Asosiy menyu', 'Main navigation', 'Основное меню')}>
          {nav.map(([href, label, Icon]) => (
            <Link key={href} href={href} aria-current={pathname === href ? 'page' : undefined}>
              <Icon size={18} /><span>{label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
