'use client';
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowRight, Clock3, Headphones, BookOpen, PenLine, Mic } from 'lucide-react';
import { useProduct } from '@/components/product/product-context';
import { api, type Attempt } from '@/components/product/api';
import LoadingSkeleton from '@/components/product/loading-skeleton';

const order = ['Listening', 'Reading', 'Writing'];
const icons = { Listening: Headphones, Reading: BookOpen, Writing: PenLine, Speaking: Mic } as const;
type Flow = { ids: number[]; step: number; attempts: string[]; startedAt: string };
export default function FullExamPage() {
  const router = useRouter();
  const params = useSearchParams();
  const { exams, openAccess, free, history, say, t } = useProduct();
  const [results, setResults] = useState<Attempt[] | null>(null);
  const [flow, setFlow] = useState<Flow | null>(null);
  const isResults = params.get('results') === '1';
  useEffect(() => {
    try { const saved = localStorage.getItem('ieltsqa-full-exam'); if (saved) setFlow(JSON.parse(saved) as Flow); } catch {}
  }, []);
  useEffect(() => {
    if (!isResults || !flow) return;
    let alive = true;
    Promise.all((flow.attempts || []).map(id => api<Attempt>(`attempts/${id}/`)))
      .then(items => { if (alive) setResults(items); })
      .catch(() => { if (alive) setResults([]); });
    return () => { alive = false; };
  }, [isResults, flow]);
  if (isResults) {
    if (!flow || !results) return <LoadingSkeleton label={t.loading} />;
    const graded = results.filter(a => a.result?.band != null);
    const avg = graded.length ? (graded.reduce((sum, a) => sum + Number(a.result?.band), 0) / graded.length).toFixed(1) : null;
    return <section className="panel">
      <span className="eyebrow">IELTSQA · TEST MODE</span><h1>{say('Imtihon yakunlandi', 'Exam complete', 'Экзамен завершён')}</h1>
      <p>{say('Bu sinov hisoboti. Umumiy ko‘rsatkich faqat baholangan bo‘limlar bo‘yicha hisoblangan; rasmiy IELTS bandi emas.', 'This is a practice report. The average uses graded sections only and is not an official IELTS band.', 'Это тренировочный отчёт. Среднее рассчитано только по оценённым разделам и не является официальным баллом IELTS.')}</p>
      {avg && <h2>{say('Baholangan bo‘limlar o‘rtachasi', 'Average of graded sections', 'Среднее по оценённым разделам')}: {avg}</h2>}
      <div className="product-test-grid">{results.map(a => <article className="panel" key={a.id}><span className="eyebrow">{a.section}</span><h2>{a.title}</h2><p>{a.state === 'graded' && a.result ? (a.result.band == null ? `${a.result.correct} / ${a.result.total}` : `Band ${a.result.band}`) : a.state === 'awaiting_assessment' ? say('Baholash kutilmoqda', 'Assessment pending', 'Ожидает оценки') : say('Natija mavjud emas', 'No score available', 'Оценка недоступна')}</p></article>)}</div>
      <button className="primary" onClick={() => { localStorage.removeItem('ieltsqa-full-exam'); router.push('/dashboard/tests'); }}>{say('Testlar ro‘yxatiga qaytish', 'Back to tests', 'К списку тестов')}</button>
    </section>;
  }
  const selected = order.map(section => exams.filter(e => e.section === section).sort((a,b) => a.id-b.id)[0]).filter(Boolean);
  const alreadyRunning = history.find(a => a.state === 'in_progress' && selected.some(e => e.id === exams.find(x => x.title === a.title)?.id));
  function start() {
    if (selected.length !== order.length) return;
    if (selected.some(e => !openAccess && !free && !e.has_access)) { router.push('/dashboard/payments'); return; }
    if (selected.some(e => e.section === 'Writing') && !window.confirm(t.writingNotice)) return;
    const value: Flow = { ids: selected.map(e => e.id), step: 0, attempts: [], startedAt: new Date().toISOString() };
    localStorage.setItem('ieltsqa-full-exam', JSON.stringify(value));
    router.push(`/dashboard/tests/${value.ids[0]}?full=1`);
  }
  return <section className="panel">
    <span className="eyebrow">{say('KETMA-KET SINOV', 'SEQUENTIAL PRACTICE', 'ПОСЛЕДОВАТЕЛЬНЫЙ ТЕСТ')}</span>
    <h1>{say('To‘liq imtihon', 'Full exam', 'Полный экзамен')}</h1>
    <p>{say('Har bir bo‘lim nashr qilingan test savollaridan foydalanadi. Bo‘limlar orasida javoblar saqlanadi. Speaking oxirida AI ovozli mashq sifatida taklif etiladi; sozlanmagan bo‘lsa, o‘tkazib yuborish mumkin.', 'Uses published section tests and saves answers between sections. Speaking is offered as an AI voice practice at the end and can be skipped if unavailable.', 'Используются опубликованные тесты, ответы сохраняются между разделами. В конце предлагается Speaking с ИИ, его можно пропустить, если он недоступен.')}</p>
    <div className="product-test-grid">{order.map(section => { const exam = exams.filter(e=>e.section===section).sort((a,b)=>a.id-b.id)[0]; const Icon=icons[section as keyof typeof icons]; return <article className="panel" key={section}><Icon size={22}/><h2>{section}</h2><p>{exam ? `${exam.title} · ${exam.question_count} ${t.questions} · ${Math.round(exam.duration_seconds/60)} ${t.minutes}` : say('Nashr qilingan test topilmadi', 'No published test found', 'Опубликованный тест не найден')}</p></article>; })}<article className="panel"><Mic size={22}/><h2>Speaking</h2><p>{say('AI ovozli mashq. Yakuniy o‘rtacha bandga kiritilmaydi.', 'AI voice practice. It is excluded from the average band.', 'Голосовая практика с ИИ. Не включается в средний балл.')}</p></article></div>
    {selected.length !== order.length && <p role="alert" className="product-alert">{say('To‘liq oqimni boshlash uchun Listening, Reading va Writing bo‘limlarida nashr qilingan test bo‘lishi kerak.', 'A published Listening, Reading and Writing test is required to start.', 'Для начала нужны опубликованные тесты Listening, Reading и Writing.')}</p>}
    {alreadyRunning && <p>{say('Oldingi urinish davom etmoqda; testlar sahifasidan davom ettirishingiz mumkin.', 'An attempt is already in progress. Resume it from the tests page.', 'У вас уже есть незавершённая попытка. Продолжите её со страницы тестов.')}</p>}
    <button className="primary" disabled={selected.length !== order.length} onClick={start}><Clock3 size={17}/> {say('Imtihonni boshlash', 'Start exam', 'Начать экзамен')} <ArrowRight size={17}/></button>
  </section>;
}
