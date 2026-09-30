'use client';
import { useSearchParams, useRouter } from 'next/navigation';
import { useProduct } from '@/components/product/product-context';
import {finishFullExamSpeaking, fullExamKey, parseFullExamFlow} from '@/components/product/full-exam-flow';
import VoicePilot from '@/components/product/voice-pilot';

export default function SpeakingPage() {
  const router = useRouter();
  const params = useSearchParams();
  const fullExam = params.get('full') === '1';
  const { language } = useProduct();
  function finishSpeaking(attemptId?: string) {
    if (fullExam) {
      try {
        const saved = parseFullExamFlow(localStorage.getItem(fullExamKey));
        if (!saved) throw new Error('Missing full exam flow.');
        localStorage.setItem(fullExamKey, JSON.stringify(finishFullExamSpeaking(saved, attemptId)));
      } catch {}
      router.push('/dashboard/full-exam?results=1');
    } else if (attemptId) router.push(`/dashboard/results/${attemptId}`);
    else router.push('/dashboard/tests');
  }
  return (
    <>
      <VoicePilot
        language={language}
        onBack={() => fullExam ? finishSpeaking() : router.push('/dashboard/tests')}
        onSubmitted={(attempt) => finishSpeaking(attempt.id)}
      />
      {fullExam && <button className="secondary" onClick={() => { if (window.confirm(language === 'uz' ? 'Speakingni o‘tkazib yuborasizmi? Yuborilmagan yozuv saqlanmaydi.' : language === 'ru' ? 'Пропустить Speaking? Неотправленная запись не сохранится.' : 'Skip Speaking? Unsubmitted recording will not be saved.')) finishSpeaking(); }}>
        {language === 'uz' ? 'Speakingni o‘tkazib yuborish' : language === 'ru' ? 'Пропустить Speaking' : 'Skip Speaking'}
      </button>}
    </>
  );
}
