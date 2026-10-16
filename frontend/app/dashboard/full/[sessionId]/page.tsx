'use client';
import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowRight, AudioLines, BookOpen, Check, Clock3, Headphones, Hourglass, Mic, PenLine, Printer } from 'lucide-react';
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
/**
 * A date on a report has to read the same everywhere.
 *
 * toLocaleDateString depends on the locale data the BROWSER happens to carry:
 * a Chromium without Uzbek data rendered this as "2026 M10 16". A report
 * number and a test date are not prose, so they are formatted here.
 */
function readable(iso: string) {
  if (!iso) return '';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  const pad = (value: number) => String(value).padStart(2, '0');
  return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()}`;
}

export default function FullExamPage() {
  const router = useRouter();
  const { sessionId } = useParams<{ sessionId: string }>();
  const { t, say, load, user, displayName } = useProduct();
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
    <div className="full-exam-layout">
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

      {done && (
        <section className="panel result-form" aria-label={say('Natija varaqasi', 'Result form', 'Бланк результатов')}>
          <header className="result-form-top">
            <span className="result-form-brand">
              <AudioLines size={28} aria-hidden="true" />IELTS<span>QA</span>
            </span>
            <button className="secondary no-print" onClick={() => window.print()}>
              <Printer size={16} />{say('PDF / chop etish', 'PDF / print', 'PDF / печать')}
            </button>
          </header>

          <div className="result-form-body">
          <div className="result-form-title">
            <span className="eyebrow">{say('MASHQ NATIJASI VARAQASI', 'PRACTICE RESULT FORM', 'БЛАНК РЕЗУЛЬТАТА ПРАКТИКИ')}</span>
            <h2>IELTS Academic</h2>
            <p>{say('To‘rtta bo‘lim bir sessiyada topshirildi',
              'Four sections taken in one sitting', 'Четыре раздела за одну сессию')}</p>
          </div>

          <p className="result-form-candidate">{displayName || user?.email || '—'}</p>

          <dl className="result-form-meta">
            <div>
              <dt>{say('Imtihon sanasi', 'Test date', 'Дата теста')}</dt>
              <dd>{readable(sitting.started_at)}</dd>
            </div>
            <div>
              <dt>{say('Hisobot raqami', 'Report number', 'Номер отчёта')}</dt>
              <dd className="result-form-id">{sitting.id.slice(0, 8).toUpperCase()}</dd>
            </div>
            <div>
              <dt>{say('Bo‘limlar', 'Sections', 'Разделы')}</dt>
              <dd>{sitting.stages.length} / 4</dd>
            </div>
          </dl>

          <div className="result-form-bands">
            {sitting.stages.map((stage) => (
              <div key={stage.order} className="result-form-band">
                <span>{stage.section}</span>
                <strong>
                  {stage.band !== null ? stage.band.toFixed(1)
                    : stage.total ? `${stage.correct}/${stage.total}` : '—'}
                </strong>
              </div>
            ))}
          </div>

          <div className="result-form-overall">
            <span>{say('Umumiy band', 'Overall band', 'Общий балл')}</span>
            <strong>{sitting.overall_band !== null ? sitting.overall_band.toFixed(1) : '—'}</strong>
            <small>{say('taxminiy', 'estimate', 'оценка')}</small>
          </div>

          {sitting.overall_band === null && (
            <p className="result-form-pending" role="status">
              {sitting.awaiting_assessment.length > 0 && say(
                `Umumiy band hali chiqarilmadi — baholanmoqda: ${sitting.awaiting_assessment.join(', ')}. Baho kelgach shu sahifada ko‘rinadi.`,
                `No overall band yet — still being assessed: ${sitting.awaiting_assessment.join(', ')}. It appears here once the band arrives.`,
                `Общий балл пока не выставлен — оценивается: ${sitting.awaiting_assessment.join(', ')}.`)}
              {sitting.sections_without_band.length > 0 && ' ' + say(
                `${sitting.sections_without_band.join(', ')} uchun band jadvali yo‘q: bu testlar to‘liq 40 savoldan iborat emas, shuning uchun faqat to‘g‘ri javoblar soni ko‘rsatiladi. Umumiy band to‘rttala bo‘limda ham band bo‘lgandagina chiqadi.`,
                `${sitting.sections_without_band.join(', ')} has no band table: these papers are not the standard 40 questions, so only the raw score is shown. An overall band needs a band in all four sections.`,
                `Для ${sitting.sections_without_band.join(', ')} нет таблицы: это не стандартные 40 вопросов, показан только сырой балл.`)}
            </p>
          )}

          </div>

          <footer className="result-form-foot">
          <p className="result-form-note">
            {say('Bu — mashq natijasi. Rasmiy IELTS Test Report Form emas va rasmiy maqsadlarda ishlatilmaydi. Listening va Reading bandlari jadval bo‘yicha taxmin, Writing va Speaking bandlari AI tomonidan qo‘yilgan.',
              'This is a practice result. It is not an official IELTS Test Report Form and cannot be used for any official purpose. Listening and Reading bands are table estimates; Writing and Speaking bands are given by AI.',
              'Это результат практики, а не официальный IELTS Test Report Form. Баллы Listening и Reading — оценка по таблице; Writing и Speaking выставлены ИИ.')}
          </p>
          <p className="result-form-issuer">
            IELTSQA · {say('Mustaqil IELTS mashq platformasi', 'Independent IELTS practice platform',
              'Независимая платформа подготовки к IELTS')}
          </p>
          </footer>
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
        <button className="text-button no-print" onClick={() => void abandon()}>
          {say('Imtihonni to‘xtatish', 'Abandon this sitting', 'Прервать сессию')}
        </button>
      )}
    </div>
  );
}
