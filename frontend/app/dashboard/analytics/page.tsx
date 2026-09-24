'use client';
import { useRouter } from 'next/navigation';
import { useProduct } from '@/components/product/product-context';
import AnalyticsDashboard from '@/components/product/analytics-dashboard';

export default function AnalyticsPage() {
  const router = useRouter();
  const { language, busy } = useProduct();
  return <AnalyticsDashboard language={language} busy={busy} onOpen={(id) => router.push(`/dashboard/results/${id}`)} />;
}
