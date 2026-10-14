'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Clock3, Mic, Square, ArrowRight, AudioLines } from 'lucide-react';
import { type Attempt } from './api';

/**
 * Speaking EXAM mode: an interlocutor frame, not a conversation.
 *
 * The question bank drives the session. Each question is delivered as the
 * examiner's recording when one was uploaded, and read aloud by the browser
 * when it was not; the candidate then answers against a fixed clock. Nothing
 * here reacts to WHAT the candidate said — no follow-ups, no coaching, no
 * score during the exam. That is what separates this from the practice pilot.
 */

type Phase = 'intro' | 'prep' | 'asking' | 'answering' | 'between' | 'submitting' | 'done' | 'error';
type Question = NonNullable<Attempt['questions']>[number];

/** Standard IELTS timings, derived from the part so the question bank stays simple. */
const SECONDS: Record<number, number> = { 1: 60, 2: 120, 3: 90 };
const PREP_SECONDS = 60;

const PART_NAMES: Record<number, Record<string, string>> = {
  1: { uz: 'Part 1 · Tanishuv', en: 'Part 1 · Introduction', ru: 'Part 1 · Знакомство' },
  2: { uz: 'Part 2 · Cue card', en: 'Part 2 · Long turn', ru: 'Part 2 · Монолог' },
  3: { uz: 'Part 3 · Muhokama', en: 'Part 3 · Discussion', ru: 'Part 3 · Обсуждение' },
};

export default function SpeakingExam({
  attempt, t, say, onClose, onComplete,
}: {
  attempt: Attempt;
  t: { back: string; remaining: string; working: string; finish: string; retry: string };
  say: (uz: string, en: string, ru: string) => string;
  onClose: () => void;
  onComplete: (a: Attempt) => void;
}) {
  const questions = (attempt.questions ?? [])
    .slice()
    .sort((a, b) => (a.part ?? 0) - (b.part ?? 0) || a.position - b.position);

  const [index, setIndex] = useState(0);
  const [phase, setPhase] = useState<Phase>('intro');
  const [seconds, setSeconds] = useState(0);
  const [error, setError] = useState('');
  const [consent, setConsent] = useState(false);
  const [level, setLevel] = useState(0);

  const clips = useRef<Blob[]>([]);
  const stream = useRef<MediaStream | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const audioCtx = useRef<AudioContext | null>(null);
  const deadline = useRef(0);
  const raf = useRef(0);
  const advance = useRef<() => void>(() => {});

  const question: Question | undefined = questions[index];
  const lang = say('uz', 'en', 'ru') as 'uz' | 'en' | 'ru';
  const partName = question ? (PART_NAMES[question.part ?? 1]?.[lang] ?? `Part ${question.part}`) : 'Speaking';

  const release = useCallback(() => {
    cancelAnimationFrame(raf.current);
    try { if (recorder.current && recorder.current.state !== 'inactive') recorder.current.stop(); } catch { /* already stopped */ }
    recorder.current = null;
    stream.current?.getTracks().forEach((track) => track.stop());
    stream.current = null;
    void audioCtx.current?.close().catch(() => {});
    audioCtx.current = null;
    try { window.speechSynthesis?.cancel(); } catch { /* unsupported */ }
  }, []);

  useEffect(() => release, [release]);

  /** Moves to question `next`, inserting Part 2's preparation minute before it. */
  const goTo = useCallback((next: number) => {
    if (next >= questions.length) { setPhase('between'); return; }
    setIndex(next);
    if (questions[next].part === 2) {
      // Part 2 opens with its preparation minute; arm the clock as we enter it.
      deadline.current = Date.now() + PREP_SECONDS * 1000;
      setSeconds(PREP_SECONDS);
      setPhase('prep');
    } else setPhase('asking');
  }, [questions]);

  const finishAnswer = useCallback(() => {
    cancelAnimationFrame(raf.current);
    setLevel(0);
    try { if (recorder.current && recorder.current.state !== 'inactive') recorder.current.stop(); } catch { /* already stopped */ }
    recorder.current = null;
    goTo(index + 1);
  }, [goTo, index]);

  // Whichever phase is timed owns what happens when the clock reaches zero.
  useEffect(() => {
    if (phase === 'prep') advance.current = () => setPhase('asking');
    else if (phase === 'answering') advance.current = finishAnswer;
    else advance.current = () => {};
  }, [phase, finishAnswer]);

  useEffect(() => {
    if (phase !== 'answering' && phase !== 'prep') return;
    const tick = () => {
      const left = Math.max(0, Math.ceil((deadline.current - Date.now()) / 1000));
      setSeconds(left);
      if (!left) advance.current();
    };
    tick();
    const id = setInterval(tick, 250);
    return () => clearInterval(id);
  }, [phase]);

  const openMic = useCallback(async () => {
    if (stream.current) return stream.current;
    const media = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.current = media;
    return media;
  }, []);

  /** Delivers the question, then opens the microphone for a fixed time. */
  const ask = useCallback(async (q: Question) => {
    setError('');
    let media: MediaStream;
    try {
      media = await openMic();
    } catch {
      setError(say('Mikrofonga ruxsat berilmadi. Brauzer sozlamalaridan ruxsat bering va qaytadan urining.',
        'Microphone permission was refused. Allow it in your browser settings and retry.',
        'Доступ к микрофону запрещён. Разрешите его в настройках браузера и повторите.'));
      setPhase('error');
      return;
    }

    // Deliver the prompt. Every path resolves: a device with no English voice,
    // a missing file or a blocked autoplay must not stall the exam.
    await new Promise<void>((resolve) => {
      const done = () => resolve();
      if (q.audio_url) {
        const el = new Audio(q.audio_url);
        el.onended = done;
        el.onerror = done;
        void el.play().catch(done);
        setTimeout(done, 60000);
        return;
      }
      try {
        const synth = window.speechSynthesis;
        // No speech engine, or no English voice on this device: the prompt is on
        // screen, so open the microphone at once rather than sitting in silence.
        const voice = synth?.getVoices().find((v) => v.lang.toLowerCase().startsWith('en'));
        if (!synth || !voice) return done();
        const utterance = new SpeechSynthesisUtterance(q.prompt);
        utterance.voice = voice;
        utterance.lang = voice.lang;
        utterance.rate = 0.95;
        utterance.onend = done;
        utterance.onerror = done;
        synth.cancel();
        synth.speak(utterance);
        // Roughly 12 words a second of slack, so a long prompt is never cut off
        // and a silent failure never stalls the exam.
        setTimeout(done, Math.min(20000, 3000 + q.prompt.split(/\s+/).length * 450));
      } catch { done(); }
    });

    try {
      const mime = ['audio/webm', 'audio/ogg', 'audio/mp4'].find((m) => MediaRecorder.isTypeSupported(m)) ?? '';
      const rec = new MediaRecorder(media, mime ? { mimeType: mime, audioBitsPerSecond: 48000 } : undefined);
      const chunks: Blob[] = [];
      rec.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
      rec.onstop = () => clips.current.push(new Blob(chunks, { type: (mime || 'audio/webm').split(';')[0] }));
      rec.start(1000);
      recorder.current = rec;
    } catch {
      setError(say('Audio yozib olinmadi. Boshqa brauzerda sinab ko‘ring.',
        'Audio recording failed. Try another browser.',
        'Не удалось записать аудио. Попробуйте другой браузер.'));
      setPhase('error');
      return;
    }

    // A level meter, so the candidate can see the microphone is live.
    try {
      const ctx = new AudioContext();
      audioCtx.current = ctx;
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      ctx.createMediaStreamSource(media).connect(analyser);
      const data = new Uint8Array(analyser.frequencyBinCount);
      const loop = () => {
        analyser.getByteTimeDomainData(data);
        let peak = 0;
        for (const v of data) peak = Math.max(peak, Math.abs(v - 128) / 128);
        setLevel(peak);
        raf.current = requestAnimationFrame(loop);
      };
      loop();
    } catch { /* the meter is decoration; the exam continues without it */ }

    deadline.current = Date.now() + (SECONDS[q.part ?? 1] ?? 60) * 1000;
    setSeconds(SECONDS[q.part ?? 1] ?? 60);
    setPhase('answering');
  }, [openMic, say]);

  useEffect(() => {
    if (phase !== 'asking' || !question) return;
    void ask(question);
    // `index` drives re-delivery; `ask` is stable enough and re-running it on
    // identity changes alone would replay the prompt mid-answer.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, index]);

  async function submit() {
    setPhase('submitting');
    setError('');
    release();
    await new Promise((r) => setTimeout(r, 400)); // let the last onstop land
    try {
      const form = new FormData();
      form.append('id', attempt.id);
      form.append('consent', 'yes');
      form.append('transcript', '');
      const usable = clips.current.filter((c) => c.size > 100).slice(0, 12);
      if (!usable.length) throw new Error(say('Hech qanday yozuv olinmadi.', 'No recording was captured.', 'Запись не получена.'));
      usable.forEach((clip, i) => form.append('audio', clip, `answer-${i + 1}.webm`));
      const response = await fetch('/api/voice/submit/', {
        method: 'POST',
        body: form,
        headers: { 'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? '' },
        credentials: 'same-origin',
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? 'SUBMIT_FAILED');
      setPhase('done');
      onComplete(data as Attempt);
    } catch (e) {
      setError((e as Error).message);
      setPhase('error');
    }
  }

  const clock = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
  const cue = question?.choices ?? [];

  return (
    <div className="live-exam section-speaking speaking-exam">
      <header className="exam-toolbar">
        <button className="text-button" onClick={() => { release(); onClose(); }}>← {t.back}</button>
        <strong>{partName}</strong>
        {(phase === 'answering' || phase === 'prep') && (
          <span className="timer" aria-label={t.remaining}><Clock3 size={18} />{clock}</span>
        )}
      </header>

      <h1>{attempt.title}</h1>
      {error && <div role="alert" className="product-alert">{error}</div>}

      {phase === 'intro' && (
        <section className="panel speaking-stage">
          <p>{attempt.passage}</p>
          <ol className="speaking-steps">
            <li>{say('Part 1 — tanishuv savollari, har biriga 60 soniya.',
              'Part 1 — introduction questions, 60 seconds each.',
              'Part 1 — вводные вопросы, по 60 секунд.')}</li>
            <li>{say('Part 2 — cue card. Avval 1 daqiqa tayyorgarlik, keyin 2 daqiqa gapirasiz.',
              'Part 2 — cue card. One minute to prepare, then two minutes to speak.',
              'Part 2 — карточка. Минута на подготовку, затем две минуты речи.')}</li>
            <li>{say('Part 3 — mavhum savollar, har biriga 90 soniya.',
              'Part 3 — abstract questions, 90 seconds each.',
              'Part 3 — абстрактные вопросы, по 90 секунд.')}</li>
          </ol>
          <p className="product-muted">
            {say('Imtihon davomida maslahat ham, baho ham berilmaydi. Javoblaringiz yozib olinadi va keyin baholanadi.',
              'No coaching and no score during the exam. Your answers are recorded and assessed afterwards.',
              'Во время экзамена нет подсказок и оценок. Ответы записываются и оцениваются позже.')}
          </p>
          <label className="voice-consent">
            <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
            <span>{say('Ovozim yozib olinishiga va baholash uchun ishlatilishiga roziman.',
              'I agree to my voice being recorded and used for assessment.',
              'Я согласен на запись голоса и его использование для оценки.')}</span>
          </label>
          <button className="primary" disabled={!consent} onClick={() => goTo(0)}>
            <Mic size={18} />{say('Imtihonni boshlash', 'Start the exam', 'Начать экзамен')}
          </button>
        </section>
      )}

      {phase === 'prep' && question && (
        <section className="panel speaking-stage">
          <span className="eyebrow">{say('Tayyorgarlik', 'Preparation', 'Подготовка')}</span>
          <h2 lang="en">{question.prompt}</h2>
          <ul className="speaking-cue-points" lang="en">{cue.map((point) => <li key={point}>{point}</li>)}</ul>
          <p className="product-muted">
            {say('Yozib oling yoki o‘ylab oling. Vaqt tugagach savol o‘qiladi.',
              'Make notes or think it through. The question is read when the time ends.',
              'Сделайте заметки. Вопрос прозвучит по истечении времени.')}
          </p>
        </section>
      )}

      {(phase === 'asking' || phase === 'answering') && question && (
        <section className="panel speaking-stage">
          <span className="eyebrow">{say('Savol', 'Question', 'Вопрос')} {index + 1} / {questions.length}</span>
          <h2 lang="en">{question.prompt}</h2>
          {question.part === 2 && cue.length > 0 && (
            <ul className="speaking-cue-points" lang="en">{cue.map((p) => <li key={p}>{p}</li>)}</ul>
          )}
          {phase === 'asking' ? (
            <p className="voice-state" role="status">
              <AudioLines size={18} />{say('Savol o‘qilmoqda…', 'The question is being read…', 'Вопрос зачитывается…')}
            </p>
          ) : (
            <>
              <div className="speaking-meter" aria-hidden="true">
                <span style={{ transform: `scaleX(${Math.min(1, level * 2.2)})` }} />
              </div>
              <p className="voice-state" role="status">
                <Mic size={18} />{say('Yozilmoqda — javob bering', 'Recording — answer now', 'Идёт запись — отвечайте')}
              </p>
              <button className="secondary" onClick={finishAnswer}>
                <Square size={16} />{say('Javobni yakunlash', 'Finish this answer', 'Завершить ответ')}
              </button>
            </>
          )}
        </section>
      )}

      {phase === 'between' && (
        <section className="panel speaking-stage">
          <h2>{say('Barcha savollarga javob berdingiz', 'You have answered every question', 'Вы ответили на все вопросы')}</h2>
          <p className="product-muted">
            {say('Yozuvlaringizni yuboring. Baho AI baholash ulanganda chiqadi.',
              'Submit your recordings. The band appears once AI assessment is connected.',
              'Отправьте записи. Балл появится после подключения AI-оценки.')}
          </p>
          <button className="primary" onClick={() => void submit()}>{t.finish}<ArrowRight size={18} /></button>
        </section>
      )}

      {phase === 'submitting' && (
        <section className="panel speaking-stage"><p role="status">{t.working}</p></section>
      )}

      {phase === 'error' && (
        <section className="panel speaking-stage">
          <button className="primary" onClick={() => setPhase(index < questions.length ? 'asking' : 'between')}>{t.retry}</button>
        </section>
      )}
    </div>
  );
}
