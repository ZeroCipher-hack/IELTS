'use client';
import { useRouter } from 'next/navigation';
import { AudioLines, ArrowRight } from 'lucide-react';
import { useState } from 'react';
import { useProduct } from './product-context';
import ThemeToggle from './theme-toggle';
import LoadingSkeleton from './loading-skeleton';
import type { Language } from './api';

export default function AuthScreen({ mode }: { mode: 'login' | 'register' }) {
  const router = useRouter();
  const { t, say, language, setLanguage, ready, available, error, setError, busy, connect, authenticate, user } = useProduct();
  const [localMode, setLocalMode] = useState(mode);
  const isRegister = localMode === 'register';

  if (user) {
    router.replace('/dashboard');
    return null;
  }
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

  const languages = (
    <select aria-label={t.language} value={language} onChange={(e) => setLanguage(e.target.value as Language)}>
      <option value="uz">UZ</option>
      <option value="en">EN</option>
      <option value="ru">RU</option>
    </select>
  );

  return (
    <main className="workspace product-login">
      <div className="login-brand">
        <span className="product-logo"><AudioLines />IELTS<span>QA</span></span>
        <div className="login-controls">{languages}<ThemeToggle language={language} /></div>
        <h1>{t.subtitle}</h1>
        <p>{t.brand}</p>
        <p className="login-skills">Listening · Reading · Writing · Speaking</p>
      </div>
      <form
        className="panel product-auth"
        onSubmit={(e) => {
          e.preventDefault();
          const data = Object.fromEntries(new FormData(e.currentTarget));
          void authenticate(isRegister ? 'register' : 'login', data).then(() => router.push('/dashboard'));
        }}
      >
        <h2>{isRegister ? t.register : t.login}</h2>
        {error && <p className="product-alert" role="alert">{error}</p>}
        {isRegister && (
          <label>{t.name}<input name="name" required maxLength={80} autoComplete="name" /></label>
        )}
        <label>{t.email}<input type="email" name="email" required maxLength={150} autoComplete="email" /></label>
        <label>
          {t.password}
          <input type="password" name="password" required minLength={isRegister ? 10 : 1} autoComplete={isRegister ? 'new-password' : 'current-password'} />
        </label>
        <button className="primary" disabled={busy}>{busy ? t.working : isRegister ? t.register : t.login}<ArrowRight size={18} /></button>
        <button
          className="text-button"
          type="button"
          onClick={() => {
            const next = isRegister ? 'login' : 'register';
            setLocalMode(next);
            setError('');
            router.replace(`/${next}`);
          }}
        >
          {isRegister ? t.haveAccount : t.newAccount}
        </button>
      </form>
    </main>
  );
}
