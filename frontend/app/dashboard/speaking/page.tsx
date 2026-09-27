'use client';
import { useSearchParams, useRouter } from 'next/navigation';
import { useProduct } from '@/components/product/product-context';
import VoicePilot from '@/components/product/voice-pilot';

export default function SpeakingPage() {
  const router = useRouter();
  const params = useSearchParams();
  const fullExam = params.get('full') === '1';
  const { language } = useProduct();
  function finishSpeaking(attemptId?: string) {
    if (fullExam) {
      try {
        const flow = JSON.parse(localStorage.getItem('ieltsqa-full-exam') || '{}') as { attempts?: string[] };
        if (attemptId) flow.attempts = [...(flow.attempts || []), attemptId];
        localStorage.setItem('ieltsqa-full-exam', JSON.stringify(flow));
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
      {fullExam && <button className="secondary" onClick={() => finishSpeaking()}>
        {language === 'uz' ? 'Speakingni o‘tkazib yuborish' : language === 'ru' ? 'Пропустить Speaking' : 'Skip Speaking'}
      </button>}
    </>
  );
}
