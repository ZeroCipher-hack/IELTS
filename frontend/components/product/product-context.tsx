'use client';
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { api, type Attempt, type Exam, type Language, type User } from './api';
import { copy } from './i18n';

type Ctx = {
  user: User | null;
  language: Language;
  ready: boolean;
  available: boolean;
  busy: boolean;
  error: string;
  notice: string;
  exams: Exam[];
  history: Attempt[];
  free: boolean;
  catalogLoading: boolean;
  historyLoading: boolean;
  t: (typeof copy)['uz'];
  say: (uz: string, en: string, ru: string) => string;
  displayName: string;
  setLanguage: (l: Language) => void;
  setError: (e: string) => void;
  setNotice: (n: string) => void;
  setUser: (u: User) => void;
  connect: () => Promise<void>;
  load: (silent?: boolean) => Promise<void>;
  run: (fn: () => Promise<void>) => Promise<void>;
  logout: () => Promise<void>;
  uploadAvatar: (file: File) => Promise<void>;
  authenticate: (mode: 'login' | 'register', data: Record<string, FormDataEntryValue>) => Promise<void>;
};

const ProductContext = createContext<Ctx | null>(null);

export function useProduct() {
  const ctx = useContext(ProductContext);
  if (!ctx) throw new Error('useProduct must be used inside <ProductProvider>');
  return ctx;
}

export function ProductProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [language, setLanguage] = useState<Language>('uz');
  const [ready, setReady] = useState(false);
  const [available, setAvailable] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [exams, setExams] = useState<Exam[]>([]);
  const [history, setHistory] = useState<Attempt[]>([]);
  const [free, setFree] = useState(false);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(true);

  const t = copy[language];
  const say = (uz: string, en: string, ru: string) => (language === 'uz' ? uz : language === 'en' ? en : ru);
  const displayName = user?.name && !user.name.includes('@') ? user.name : '';

  const load = useCallback(async (silent = false) => {
    if (!silent) {
      setCatalogLoading(true);
      setHistoryLoading(true);
    }
    const outcomes = await Promise.allSettled([
      api<{ exams: Exam[]; free_attempt_available: boolean }>('catalog/')
        .then((cat) => {
          setExams(cat.exams);
          setFree(cat.free_attempt_available);
        })
        .finally(() => setCatalogLoading(false)),
      api<{ attempts: Attempt[] }>('attempts/')
        .then((list) => setHistory(list.attempts))
        .finally(() => setHistoryLoading(false)),
    ]);
    const failure = outcomes.find((r) => r.status === 'rejected');
    if (failure?.status === 'rejected') throw failure.reason;
  }, []);

  const connect = useCallback(async () => {
    setReady(false);
    setError('');
    try {
      const s = await api<{ user: User | null }>('session/');
      setAvailable(true);
      setUser(s.user);
      if (s.user) {
        setLanguage(s.user.language);
        void load().catch((e) => setError((e as Error).message));
      }
    } catch (e) {
      setAvailable(false);
      setError((e as Error).message);
    } finally {
      setReady(true);
    }
  }, [load]);

  useEffect(() => {
    void connect();
  }, [connect]);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  async function run(fn: () => Promise<void>) {
    setBusy(true);
    setError('');
    setNotice('');
    try {
      await fn();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    await run(async () => {
      await api('logout/', 'POST');
      setUser(null);
      setHistory([]);
    });
  }

  async function uploadAvatar(file: File) {
    await run(async () => {
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) {
        throw new Error(say('JPG, PNG yoki WebP tanlang. Eng katta hajm: 5 MB.', 'Choose JPG, PNG or WebP, up to 5 MB.', 'Выберите JPG, PNG или WebP до 5 МБ.'));
      }
      const bitmap = await createImageBitmap(file);
      let avatar: string;
      try {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        if (!ctx) throw new Error('Image processing unavailable');
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, 256, 256);
        const edge = Math.min(bitmap.width, bitmap.height);
        ctx.drawImage(bitmap, (bitmap.width - edge) / 2, (bitmap.height - edge) / 2, edge, edge, 0, 0, 256, 256);
        avatar = canvas.toDataURL('image/jpeg', 0.85);
      } finally {
        bitmap.close();
      }
      const result = await api<{ user: User }>('profile/', 'PATCH', { avatar });
      setUser(result.user);
      setNotice(t.profileSaved);
    });
  }

  async function authenticate(mode: 'login' | 'register', data: Record<string, FormDataEntryValue>) {
    await run(async () => {
      const s = await api<{ user: User }>(mode === 'register' ? 'register/' : 'login/', 'POST', data);
      setUser(s.user);
      const p = await api<{ user: User }>('profile/', 'PATCH', { language });
      setUser(p.user);
      await load();
    });
  }

  const value: Ctx = {
    user, language, ready, available, busy, error, notice,
    exams, history, free, catalogLoading, historyLoading,
    t, say, displayName,
    setLanguage, setError, setNotice, setUser,
    connect, load, run, logout, uploadAvatar, authenticate,
  };

  return <ProductContext.Provider value={value}>{children}</ProductContext.Provider>;
}
