'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowRight, Clock3, Headphones, BookOpen, PenLine, Mic, Check, CircleHelp, Sparkles, Trophy, ShieldCheck } from 'lucide-react';
import { useProduct } from '@/components/product/product-context';
import { api, type Attempt } from '@/components/product/api';
import {fullExamKey, nextFullExamPath, parseFullExamFlow, type FullExamFlow} from '@/components/product/full-exam-flow';
import LoadingSkeleton from '@/components/product/loading-skeleton';

const order = ['Listening', 'Reading', 'Writing'] as const;
const icons = { Listening: Headphones, Reading: BookOpen, Writing: PenLine, Speaking: Mic } as const;
export default function FullExamPage() {
  const router = useRouter();
  const params = useSearchParams();
  const { exams, openAccess, say, t, catalogLoading } = useProduct();
  const [results, setResults] = useState<Attempt[] | null>(null);
  const [chosen, setChosen] = useState<Record<string, number>>({});
  const [flow, setFlow] = useState<FullExamFlow | null>(null);
  const [flowReady, setFlowReady] = useState(false);
  const [resultError, setResultError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const isResults = params.get('results') === '1';
  useEffect(() => {
    const saved = parseFullExamFlow(localStorage.getItem(fullExamKey));
    setFlow(saved);
    if (saved) setChosen(Object.fromEntries(order.map((section,index) => [section,saved.ids[index]])));
    setFlowReady(true);
  }, []);
  useEffect(() => {
    if (!isResults || !flow) return;
    let alive = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    async function refresh() {
      const outcomes = await Promise.allSettled(flow!.attempts.map(id => api<Attempt>(`attempts/${id}/`)));
      if (!alive) return;
      const items = outcomes.flatMap(outcome => outcome.status === 'fulfilled' ? [outcome.value] : []);
      setResults(items);
      setResultError(outcomes.some(outcome => outcome.status === 'rejected') ? t.unavailable : '');
      if (items.some(item => (item.state === 'awaiting_assessment' && !['failed','disabled'].includes(item.assessment_status || '')) || ['pending','running'].includes(item.tutoring_status || ''))) timer = setTimeout(() => { void refresh(); }, 5000);
    }
    void refresh();
    return () => { alive = false; if (timer) clearTimeout(timer); };
  }, [isResults, flow, refreshKey, t.unavailable]);

  const selected = order.map(section => { const options=exams.filter(e => e.section === section && e.ready !== false).sort((a,b) => a.id-b.id); return options.find(e => e.id === chosen[section]) || options[0]; }).filter((exam): exam is NonNullable<typeof exam> => Boolean(exam));
  const canResume = Boolean(flow && (flow.step < 3 || flow.speaking === 'pending'));
  const totalMinutes = selected.reduce((sum, exam) => sum + Math.round(exam.duration_seconds / 60), 0);
  const hasAccess = openAccess || selected.every(e => e.has_access);
  function start() {
    if (canResume && flow) { router.push(nextFullExamPath(flow)); return; }
    if (selected.length !== order.length) return;
    if (!hasAccess) { router.push('/dashboard/payments'); return; }
    if (selected.some(e => e.section === 'Writing') && !window.confirm(t.writingNotice)) return;
    const value: FullExamFlow = { ids: selected.map(e => e.id), step: 0, attempts: [], speaking: 'pending', startedAt: new Date().toISOString() };
    localStorage.setItem(fullExamKey, JSON.stringify(value));
    router.push(`/dashboard/tests/${value.ids[0]}?full=1`);
  }

  if (!flowReady || (catalogLoading && !isResults)) return <LoadingSkeleton label={t.loading} />;

  if (isResults) {
    if (!flow) return <section className="panel"><h1>{say('Saqlangan imtihon topilmadi','No saved exam found','Сохранённый экзамен не найден')}</h1><Link className="primary" href="/dashboard/full-exam">{t.start}</Link></section>;
    if (!results) return <LoadingSkeleton label={t.loading} />;
    const completed = results.filter(item => item.state === 'graded').length;
    return <div className="full-exam-page full-exam-results">
      <div className="full-exam-results-hero">
        <span className="full-exam-kicker"><Trophy size={16}/>{say('SINOV HISOBOTI','PRACTICE REPORT','ОТЧЁТ О ТРЕНИРОВКЕ')}</span>
        <h1>{canResume?say('Imtihon davom etmoqda','Exam in progress','Экзамен продолжается'):say('Imtihon yakunlandi','Exam complete','Экзамен завершён')}</h1>
        <p>{say('Bo‘limlar bo‘yicha javoblaringiz saqlandi. Quyida mavjud natijalar va baholash holati berilgan.','Your answers were saved by section. Review the available scores and assessment status below.','Ответы по разделам сохранены. Ниже доступны результаты и статус оценки.')}</p>
        <div className="full-exam-report-score"><strong>{completed} / 4</strong><span>{say('natijasi tayyor bo‘limlar','sections with results ready','разделов с готовым результатом')}</span></div>
      </div>
      <div className="full-exam-report-note"><ShieldCheck size={18}/><p>{say('Bu sinov hisoboti. Umumiy IELTS band hisoblanmaydi. Writing va Speaking baholari AI taxmini. Listening va Reading xom ballari bandga aylantirilmagan.','Practice report only. No overall IELTS band is calculated. Writing and Speaking bands are AI estimates. Listening and Reading raw scores are not converted to bands.','Это тренировочный отчёт. Общий IELTS band не рассчитывается. Баллы Writing и Speaking — оценки ИИ. Сырые баллы Listening и Reading не переведены в band.')}</p></div>
      {resultError&&<div className="product-alert" role="alert">{resultError}<button className="secondary" onClick={()=>setRefreshKey(key=>key+1)}>{t.retry}</button></div>}
      <div className="full-exam-report-grid">{[...order,'Speaking'].map(section=>{
        const a=results.find(item=>item.section===section);
        const failed=a?.assessment_status==='failed',disabled=a?.assessment_status==='disabled';
        const label=a?.state==='graded'&&a.result?(a.result.band==null?`${a.result.correct} / ${a.result.total}`:`AI band ${a.result.band}`):failed?t.assessmentFailed:disabled?t.pendingNote:a?.state==='awaiting_assessment'?t.pending:section==='Speaking'&&flow.speaking==='skipped'?say('O‘tkazib yuborilgan','Skipped','Пропущено'):say('Natija olinmadi','No result loaded','Результат не получен');
        return <article className={'full-exam-result-card skill-'+section.toLowerCase()} key={section}><span className="eyebrow">{section}</span><h2>{a?.title||section}</h2><div className="full-exam-result-value">{label}</div>{a&&<><p>{a.result?.band==null&&a.state==='graded'?say('To‘g‘ri javoblar','Correct answers','Правильные ответы'):say('Javoblar saqlandi','Answers saved','Ответы сохранены')}</p><Link className="text-button" href={`/dashboard/results/${a.id}`}>{say('Batafsil tahlil','View result','Подробный результат')}<ArrowRight size={16}/></Link></>}</article>;
      })}</div>
      <div className="full-exam-bottom-actions">{canResume&&<Link className="primary" href={nextFullExamPath(flow)}>{say('Davom ettirish','Resume exam','Продолжить')}</Link>}<Link className="secondary" href="/dashboard/tests">{say('Testlar ro‘yxatiga qaytish','Back to tests','К тестам')}<ArrowRight size={16}/></Link><button className="text-button" onClick={()=>{localStorage.removeItem(fullExamKey);router.push('/dashboard')}}>{say('Bosh sahifa','Dashboard','На главную')}</button></div>
    </div>;
  }

  return <div className="full-exam-page">
    <section className="full-exam-hero">
      <div className="full-exam-hero-copy">
        <span className="full-exam-kicker"><Sparkles size={16}/>{say('IELTSQA · SINOV REJIMI','IELTSQA · PRACTICE MODE','IELTSQA · РЕЖИМ ТРЕНИРОВКИ')}</span>
        <h1>{say('To‘liq IELTS imtihoni','Full IELTS practice exam','Полный пробный IELTS')}</h1>
        <p>{say('To‘rtta ko‘nikmani ketma-ket mashq qiling. Har bir bo‘lim tugagach javoblar saqlanadi va keyingisiga o‘tasiz.','Practise all four skills in sequence. Your answers are saved between sections as you move through the exam.','Практикуйте все четыре навыка по порядку. Ответы сохраняются при переходе между разделами.')}</p>
        <div className="full-exam-facts">
          <span><Clock3 size={16}/>{totalMinutes? `~${totalMinutes} ${t.minutes}`:say('Vaqt testga bog‘liq','Timed by each test','Время зависит от теста')}</span>
          <span><CircleHelp size={16}/>{selected.reduce((sum,e)=>sum+e.question_count,0)} {t.questions}</span>
          <span><ShieldCheck size={16}/>{say('Natijalar saqlanadi','Progress is saved','Результаты сохраняются')}</span>
        </div>
        {canResume&&<div className="full-exam-resume-note"><Check size={17}/>{say('Davom etayotgan urinish topildi. Boshlashni bossangiz, oxirgi bo‘limingiz ochiladi.','An unfinished attempt was found. Starting will resume that section.','Найдена незавершённая попытка. При старте откроется текущий раздел.')}</div>}
        {selected.length!==order.length&&<div className="product-alert">{say('Boshlash uchun Listening, Reading va Writing bo‘limlarida tayyor test bo‘lishi kerak.','Ready Listening, Reading and Writing tests are required to begin.','Для старта нужны готовые тесты Listening, Reading и Writing.')}</div>}
        {!hasAccess&&selected.length===order.length&&<div className="full-exam-resume-note">{say('Bu imtihonga kirish huquqi kerak.','Access is required for this exam.','Для экзамена требуется доступ.')}</div>}
        <button className="primary full-exam-start" disabled={!canResume&&selected.length!==order.length} onClick={start}><PlayIcon/>{canResume?say('Imtihonni davom ettirish','Resume exam','Продолжить экзамен'):!hasAccess?say('Kirish huquqini olish','Get access','Получить доступ'):say('Imtihonni boshlash','Start full exam','Начать экзамен')}<ArrowRight size={18}/></button>
        {canResume&&<button className="text-button" onClick={()=>{if(!window.confirm(say('Joriy oqim o‘rniga yangi imtihon boshlaysizmi? Saqlangan javoblar tarixda qoladi.','Start a new flow? Saved attempts remain in history.','Начать новый экзамен? Сохранённые ответы останутся в истории.')))return;localStorage.removeItem(fullExamKey);setFlow(null);setChosen({});}}>{say('Yangi imtihon tanlash','Choose a new exam','Выбрать новый экзамен')}</button>}
      </div>
      <aside className="full-exam-hero-aside">
        <span className="full-exam-aside-label">{say('IMTIHON OQIMI','EXAM FLOW','ПОРЯДОК ЭКЗАМЕНА')}</span>
        <div className="full-exam-flow-line" aria-hidden="true"/>
        <div className="full-exam-aside-brand"><Trophy size={25}/><strong>IELTS<br/>Academic</strong></div>
        <p>{say('Urinishingiz vaqtida saqlanadi. Keyinroq davom ettirishingiz mumkin.','Your attempt is saved as you go. You can resume it later.','Попытка сохраняется по ходу. Вы сможете продолжить позже.')}</p>
      </aside>
    </section>

    <section className="full-exam-steps-section">
      <div className="full-exam-section-heading"><div><span className="eyebrow">{say('TO‘RT KO‘NIKMA','FOUR SKILLS','ЧЕТЫРЕ НАВЫКА')}</span><h2>{say('Imtihon qanday o‘tadi','How the exam works','Как проходит экзамен')}</h2></div><span className="full-exam-access-badge">{openAccess? say('Sinov uchun ochiq','Open for testing','Открыто для тестирования'):hasAccess?say('Kirish mavjud','Access granted','Доступ открыт'):say('To‘liq imtihon pullik','Full exam requires access','Полный экзамен платный')}</span></div>
      <div className="full-exam-steps-grid">
        {order.map((section,index)=>{const exam=selected.find(e=>e.section===section);const Icon=icons[section];return <article className={'full-exam-step skill-'+section.toLowerCase()} key={section}>
          <div className="full-exam-step-top"><span className="full-exam-step-number">0{index+1}</span><span className="skill-icon"><Icon size={21}/></span></div>
          <h3>{section}</h3>{exam?<label className="full-exam-test-select">{say('Testni tanlang','Choose a test','Выберите тест')}<select disabled={canResume} value={exam.id} onChange={event=>setChosen(current=>({...current,[section]:Number(event.target.value)}))}>{exams.filter(item=>item.section===section&&item.ready!==false).map(item=><option key={item.id} value={item.id}>{item.title}</option>)}</select></label>:<p>{say('Tayyor test topilmadi','No ready test found','Готовый тест не найден')}</p>}
          <div className="full-exam-step-meta">{exam?<><span>{exam.question_count} {t.questions}</span><span>{Math.round(exam.duration_seconds/60)} {t.minutes}</span></>:<span>{say('Mavjud emas','Unavailable','Недоступно')}</span>}</div>
        </article>})}
        <article className="full-exam-step skill-speaking">
          <div className="full-exam-step-top"><span className="full-exam-step-number">04</span><span className="skill-icon"><Mic size={21}/></span></div>
          <h3>Speaking</h3><p>{say('AI bilan uch qismli ovozli mashq. Imtihon oqimida o‘tkazib yuborish mumkin.','Three-part AI voice practice. You can skip it in the full exam flow.','Трёхчастная голосовая практика с ИИ. В полном экзамене её можно пропустить.')}</p>
          <div className="full-exam-step-meta"><span>11 min</span><span>{say('AI mashqi','AI practice','Практика с ИИ')}</span></div>
        </article>
      </div>
    </section>
    <p className="full-exam-disclaimer">{say('Sinov savollari rasmiy IELTS testi emas. Reading va Listening natijalari xom ball sifatida ko‘rsatiladi; tasdiqlangan band jadvali mavjud emas.', 'Practice questions are not an official IELTS test. Reading and Listening scores are raw scores; no validated band conversion is provided.', 'Тренировочные вопросы не являются официальным IELTS. Результаты Reading и Listening показываются как сырые баллы без утверждённой конвертации в band.')}</p>
  </div>;
}

function PlayIcon(){return <span className="full-exam-play-mark" aria-hidden="true">▶</span>}
