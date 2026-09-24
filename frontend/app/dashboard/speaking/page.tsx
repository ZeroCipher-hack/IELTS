'use client';
import { useRouter } from 'next/navigation';
import { useProduct } from '@/components/product/product-context';
import VoicePilot from '@/components/product/voice-pilot';

export default function SpeakingPage() {
  const router = useRouter();
  const { language } = useProduct();
  return (
    <VoicePilot
      language={language}
      onBack={() => router.push('/dashboard/tests')}
      onSubmitted={(attempt) => router.push(`/dashboard/results/${attempt.id}`)}
    />
  );
}
