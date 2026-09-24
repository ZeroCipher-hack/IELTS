'use client';
import { useSearchParams, useRouter } from 'next/navigation';
import { ArrowRight, CreditCard, LockKeyhole } from 'lucide-react';
import { useProduct } from '@/components/product/product-context';

export default function PaymentsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { t, say, free } = useProduct();
  const purchase = searchParams.get('exam') || 'IELTS Academic';

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">IELTSQA · {t.tests}</span>
          <h1>{say('Imtihonga kirish', 'Exam access', 'Доступ к экзамену')}</h1>
          <p>{say('Tanlangan imtihon', 'Selected exam', 'Выбранный экзамен')}: {purchase}</p>
        </div>
        <button className="secondary" onClick={() => router.push('/dashboard/tests')}>← {t.tests}</button>
      </div>
      <div className="checkout-layout">
        <section className="panel checkout-summary">
          <CreditCard size={32} />
          <h2>{purchase}</h2>
          <p>{say('Natijalar tahlili, xatolar izohi va rivojlanish tavsiyalari.', 'Result analysis, mistake explanations and improvement advice.', 'Анализ результатов, объяснение ошибок и рекомендации.')}</p>
          <strong className="checkout-price">{purchase === 'IELTS Academic' ? '≈ 200 000 UZS' : say('Sotuvda emas', 'Not on sale', 'Не продаётся')}</strong>
          <p>{say('Yakuniy narx to‘lov ishga tushganda ko‘rsatiladi.', 'Final pricing will be shown when payments launch.', 'Итоговая цена появится после запуска оплаты.')}</p>
          <p>{say('Rejalashtirilgan to‘lov usullari', 'Planned payment methods', 'Планируемые способы оплаты')}</p>
          <div className="payment-methods"><span>Uzcard</span><span>Humo</span></div>
        </section>
        <section className="panel checkout-status">
          <LockKeyhole size={28} />
          <h2>{say('To‘lov tez orada ochiladi', 'Payments coming soon', 'Оплата скоро появится')}</h2>
          <p>{say('Hozir to‘lov qabul qilinmaydi. To‘liq imtihon va yangi bo‘limlar tayyor bo‘lgach, shu yerdan kirish sotib olasiz.', 'Payments are not available yet. Purchase access here once the exam and payment service are ready.', 'Оплата пока недоступна. Приобрести доступ можно будет после подготовки экзамена и подключения оплаты.')}</p>
          <button className="secondary" onClick={() => router.push('/dashboard/tests')}>{free ? say('Bepul testni tanlash', 'Choose a free test', 'Выбрать бесплатный тест') : t.tests}<ArrowRight size={16} /></button>
          <button className="text-button" onClick={() => router.push('/dashboard/results')}>{t.results}<ArrowRight size={16} /></button>
        </section>
      </div>
    </>
  );
}
