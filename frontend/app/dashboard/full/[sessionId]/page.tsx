'use client';
import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowRight, BookOpen, Check, Clock3, Headphones, Hourglass, Mic, PenLine } from 'lucide-react';
import { api, type Sitting, type Stage } from '@/components/product/api';
import { useProduct } from '@/components/product/product-context';
import LoadingSkeleton from '@/components/product/loading-skeleton';

const ICONS: Record<string, typeof BookOpen> = {
  Listening: Headphones, Reading: BookOpen, Writing: PenLine, Speaking: Mic,
};

/**
 * The hub of a full sitting: four sections, taken in order, one report.
 *
 * Progress is never stored here. Every render reads the server's view, which
 * is derived from the attempts themselves, so a candidate who refreshes, loses
 * the tab or returns on another device sees the same place in the exam.
 */
export default function FullExamPage() {
  const router = useRouter();
  const { sessionId } = useParams<{ sessionId: string }>();
  const { t, say, load } = useProduct();
  const [sitting, setSitting] = useState<Sitting | null>(null);
  const [failed, setFailed] = useState('');

  const refresh = useCallback(async () => {
    try { setSitting(await api<Sitting>(`sessions/${sessionId}/`)); }
    catch (e) { setFailed((e as Error).message); }
  }, [sessionId]);

  useEffect(() => { void refresh(); }, [refresh]);

  // A section awaiting assessment is graded by a background worker, so the
  // page follows it instead of asking the candidate to keep reloading.
  useEffect(() => {
    if (!sitting?.awaiting_assessment.length) return;
    const id = setInterval(() => { void refresh(); }, 6000);
    return () => clearInterval(id);
  }, [sitting?.awaiting_assessment.length, refresh]);

  if (failed) {
    return (
      <section className="panel">
        <h1>{say('To‘liq imtihon ochilmadi', 'The sitting could not be opened', 'Сессия не открылась')}</h1>
        <p role="alert">{failed}</p>
        <Link className="primary" href="/dashboard/tests">{t.tests}</Link>
      </section>
    );
  }
  if (!sitting) return <LoadingSkeleton label={t.loading} />;

  const done = sitting.state !== 'in_progress';
  const stageLabel = (stage: Stage) => {
    if (stage.state === 'not_started') return say('Boshlanmagan', 'Not started', 'Не начато');
    if (stage.state === 'in_progress') return say('Davom etmoqda', 'In progress', 'Выполняется');
    if (stage.state === 'awaiting_assessment') return t.pending;
    return t.graded;
  };

  async function abandon() {
    if (!window.confirm(say('Imtihonni to‘xtatasizmi? Topshirilgan bo‘limlar saqlanib qoladi.',
      'Abandon this sitting? Sections you already submitted are kept.',
      'Прервать сессию? Отправленные разделы сохранятся.'))) return;
    await api<Sitting>(`sessions/${sessionId}/`, 'DELETE');
    await load().catch(() => {});
    router.push('/dashboard/tests');
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">{say('TO‘LIQ IMTIHON', 'FULL EXAM', 'ПОЛНЫЙ ЭКЗАМЕН')}</span>
          <h1>IELTS Academic</h1>
          <p>
            {done
              ? say('Imtihon yakunlandi.', 'The sitting is finished.', 'Сессия завершена.')
              : say('To‘rtta bo‘lim ketma-ket topshiriladi. Har bo‘lim o‘z vaqt chegarasiga ega.',
                'Four sections, taken in order. Each has its own time limit.',
                'Четыре раздела по порядку. У каждого свой лимит времени.')}
          </p>
        </div>
        <Link className="secondary" href="/dashboard/tests">{t.back}</Link>
      </div>

      {sitting.overall_band !== null && (
        <section className="panel full-exam-score">
          <span className="eyebrow">{say('Umumiy band (taxminiy)', 'Overall band (estimate)', 'Общий балл (оценка)')}</span>
          <strong className="band-figure">{sitting.overall_band.toFixed(1)}</strong>
          <p className="product-muted">{sitting.note}</p>
        </section>
      )}

      {done && sitting.overall_band === null && (
        <section className="panel">
          <h2>{say('Umumiy band chiqarilmadi', 'No overall band', 'Общий балл не выставлен')}</h2>
          {sitting.awaiting_assessment.length > 0 && (
            <p>{say('Baholanmoqda: ', 'Being assessed: ', 'Оценивается: ') + sitting.awaiting_assessment.join(', ')}</p>
          )}
          {sitting.sections_without_band.length > 0 && (
            <p className="product-muted">
              {say(
                `${sitting.sections_without_band.join(', ')} uchun band jadvali yo‘q — bu testlar to‘liq 40 savoldan iborat emas, shuning uchun faqat to‘g‘ri javoblar soni ko‘rsatiladi. To‘rttala bo‘limda band bo‘lmaguncha umumiy band chiqarilmaydi.`,
                `${sitting.sections_without_band.join(', ')} has no band table: these papers are not the standard 40 questions, so only the raw score is shown. An overall band needs a band in all four sections.`,
                `Для ${sitting.sections_without_band.join(', ')} нет таблицы: это не стандартные 40 вопросов, показан только сырой балл.`)}
            </p>
          )}
        </section>
      )}

      <ol className="full-exam-stages">
        {sitting.stages.map((stage) => {
          const Icon = ICONS[stage.section] ?? BookOpen;
          const active = !done && stage.order === sitting.current;
          const finished = stage.state === 'graded' || stage.state === 'awaiting_assessment';
          return (
            <li key={stage.order} className={'panel exam-card skill-' + stage.section.toLowerCase()}>
              <div className="exam-card-top">
                <span className="skill-icon"><Icon size={24} /></span>
                <span className="access-badge">
                  {finished ? <Check size={13} /> : stage.state === 'awaiting_assessment' ? <Hourglass size={13} /> : <Clock3 size={13} />}
                  {stageLabel(stage)}
                </span>
              </div>
              <span className="eyebrow">{stage.section}</span>
              <h2>{stage.title}</h2>
              <p>{stage.question_count} {t.questions} · {Math.round(stage.duration_seconds / 60)} {t.minutes}</p>

              {stage.band !== null && (
                <p className="stage-band">
                  <strong>{stage.band.toFixed(1)}</strong>
                  <span className="product-muted">
                    {stage.band_source === 'ai_estimate'
                      ? say('AI taxminiy bandi', 'AI estimate', 'Оценка ИИ')
                      : say('Jadval bo‘yicha taxmin', 'Table estimate', 'Оценка по таблице')}
                  </span>
                </p>
              )}
              {stage.band === null && stage.total ? (
                <p className="stage-band">
                  <strong>{stage.correct} / {stage.total}</strong>
                  <span className="product-muted">{say('Band jadvali yo‘q', 'No band table', 'Нет таблицы')}</span>
                </p>
              ) : null}

              {active && (
                <button className="primary" onClick={() => router.push(`/dashboard/tests/${stage.exam_id}?session=${sitting.id}`)}>
                  <ArrowRight size={16} />{stage.state === 'in_progress' ? t.resume : t.start}
                </button>
              )}
              {!active && !finished && !done && (
                <p className="availability-note">
                  {say('Oldingi bo‘lim tugagach ochiladi.', 'Opens when the previous section is finished.', 'Откроется после предыдущего раздела.')}
                </p>
              )}
              {finished && stage.attempt_id && (
                <Link className="text-button" href={`/dashboard/results/${stage.attempt_id}`}>
                  {t.details}<ArrowRight size={16} />
                </Link>
              )}
            </li>
          );
        })}
      </ol>

      {!done && (
        <button className="text-button" onClick={() => void abandon()}>
          {say('Imtihonni to‘xtatish', 'Abandon this sitting', 'Прервать сессию')}
        </button>
      )}
    </>
  );
}
