import LoadingSkeleton from '@/components/product/loading-skeleton';

// Next.js bu faylni marshrut segmenti yuklanayotganda avtomatik ko'rsatadi
// (masalan sekin tarmoqda JS bo'lagi yetib kelguncha) — Context hali tayyor
// bo'lmasligi mumkin, shuning uchun statik matn ishlatiladi.
export default function DashboardLoading() {
  return <LoadingSkeleton label="Yuklanmoqda…" />;
}
