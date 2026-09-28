'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowRight, BookOpen, Headphones, LockKeyhole, Mic, PenLine, Sparkles, Clock3, CircleHelp } from 'lucide-react';
import { useProduct } from '@/components/product/product-context';
import LoadingSkeleton from '@/components/product/loading-skeleton';

const sections = [
  { name: 'Listening', Icon: Headphones, detail: ['Audio topshiriqlar', 'Audio practice', 'Аудио задания'], summary: ['Audio yozuvni tinglang va javoblarni toping.', 'Listen to the recording and answer each question.', 'Прослушайте запись и ответьте на вопросы.'] },
  { name: 'Reading', Icon: BookOpen, detail: ['Matnni tushunish', 'Read and understand', 'Чтение и понимание'], summary: ['Matndan dalil topib, savollarga javob bering.', 'Read the passage and find evidence for each answer.', 'Читайте текст и находите подтверждения ответам.'] },
  { name: 'Writing', Icon: PenLine, detail: ['Task 1 va Task 2', 'Task 1 and Task 2', 'Задания Task 1 и Task 2'], summary: ['Rejalashtiring, yozing va topshiriqlar bo‘yicha so‘zlarni kuzating.', 'Plan and write your responses with a word count for each task.', 'Планируйте и пишите ответы с подсчётом слов для каждого задания.'] },
  { name: 'Speaking', Icon: Mic, detail: ['AI bilan gapirish', 'Speak with AI', 'Разговор с ИИ'], summary: ['IELTS Speaking qismlarini ovozli suhbat orqali mashq qiling.', 'Practise IELTS Speaking parts in a live voice conversation.', 'Тренируйте части IELTS Speaking в голосовом диалоге.'] },
] as const;

export default function TestsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { t, say, exams, free, openAccess, history, catalogLoading, busy } = useProduct();
  const [sectionFilter, setSectionFilter] = useState(searchParams.get('section') || 'All');
  if (catalogLoading) return <LoadingSkeleton label={t.loading} view="tests" />;

  const selected = sections.find((s) => s.name === sectionFilter);
  const selectedExams = selected ? exams.filter((exam) => exam.section === selected.name) : [];

  async function start(exam: (typeof exams)[number]) {
    if (exam.ready === false && !history.some((a) => a.state === 'in_progress' && a.section === exam.section && a.title === exam.title)) return;
    if (!openAccess && !free && !exam.has_access && !history.some((a) => a.state === 'in_progress' && a.section === exam.section && a.title === exam.title)) {
      router.push(`/dashboard/payments?exam=${encodeURIComponent(exam.title)}`);
      return;
    }
    if (exam.section === 'Writing' && !window.confirm(t.writingNotice)) return;
    router.push(`/dashboard/tests/${exam.id}`);
  }

  return (
    <div className={`tests-workspace ${selected ? 'is-skill-view skill-' + selected.name.toLowerCase() : 'is-catalog-view'}`}>
      {selected ? (
        <section className="section-studio-hero">
          <div className="section-studio-main">
            <div className="section-studio-heading">
              <span className="section-studio-icon"><selected.Icon size={28} /></span>
              <span className="section-studio-kicker">{say('IELTS KO‘NIKMASI', 'IELTS SKILL', 'НАВЫК IELTS')} · {selected.name.toUpperCase()}</span>
            </div>
            <h1>{selected.name === 'Speaking' ? say('Gapirishni mashq qiling', 'Build speaking confidence', 'Практикуйте разговорную речь') : selected.name === 'Writing' ? say('Fikrlaringizni yozma ifodalang', 'Make your ideas count', 'Выражайте мысли письменно') : selected.name === 'Reading' ? say('Matnni tahlil qiling', 'Read with confidence', 'Читайте уверенно') : say('Diqqat bilan tinglang', 'Train your listening', 'Тренируйте аудирование')}</h1>
            <p>{say(...selected.summary)}</p>
            <div className="section-studio-facts">
              <span><CircleHelp size={15} />{selected.name === 'Speaking' ? say('3 ta speaking qismi', '3 speaking parts', '3 части Speaking') : `${selectedExams.reduce((n,e)=>n+e.question_count,0)} ${t.questions}`}</span>
              <span><Clock3 size={15} />{selected.name === 'Speaking' ? '10 min' : selectedExams.length ? `${Math.round(selectedExams.reduce((n,e)=>n+e.duration_seconds,0)/60)} ${t.minutes}` : say('Testlar tez orada', 'Tests coming soon', 'Тесты скоро появятся')}</span>
              <span>{say('Natijalar profilingizda saqlanadi', 'Results are saved to your profile', 'Результаты сохраняются в профиле')}</span>
            </div>
            <div className="section-studio-actions">
              {selected.name === 'Speaking' ? <Link className="primary" href="/dashboard/speaking"><Mic size={17}/>{say('Speaking mashqini boshlash', 'Start speaking practice', 'Начать Speaking')}<ArrowRight size={17}/></Link> : <a className="primary" href="#test-catalog">{say('Testlarni ko‘rish', 'Browse tests', 'Посмотреть тесты')}<ArrowRight size={17}/></a>}
              <Link className="text-button" href="/dashboard/tests">{say('Barcha ko‘nikmalar', 'All skills', 'Все навыки')}<ArrowRight size={16}/></Link>
            </div>
          </div>
          <div className="section-studio-side">
            <span className="section-studio-side-label">{selected.name === 'Speaking' ? 'PART 1 · PART 2 · PART 3' : say('MASHQ HOLATI', 'PRACTICE OVERVIEW', 'ОБЗОР ТРЕНИРОВКИ')}</span>
            <strong>{selected.name === 'Speaking' ? '4 + 1 + 2 + 4' : selectedExams.length}</strong>
            <span>{selected.name === 'Speaking' ? say('daqiqalik suhbat bosqichlari', 'minutes across timed parts', 'минуты на этапы беседы') : say('nashr qilingan test', 'published tests', 'опубликованных теста')}</span>
            <div className="section-studio-track" aria-hidden="true"><i/><i/><i/><i/></div>
            <p>{selected.name === 'Speaking' ? say('Avval mikrofon va audio sozlamalarini tekshiring. Suhbat yakunida yozuv AI baholashiga yuboriladi.', 'Check your microphone and audio first. Your recording is submitted for AI assessment after the conversation.', 'Сначала проверьте микрофон и звук. После разговора запись отправляется на оценку ИИ.') : selected.name === 'Writing' ? say('Har bir topshiriq alohida saqlanadi va so‘zlar sonini ko‘rsatadi.', 'Each response is saved separately and shows its word count.', 'Каждый ответ сохраняется отдельно и показывает количество слов.') : say('Savollarni xotirjam bajaring. Jarayon davomida javoblaringiz saqlanib boradi.', 'Work through the questions at your pace. Your answers are saved as you go.', 'Отвечайте в удобном темпе. Ответы сохраняются по ходу работы.')}</p>
          </div>
        </section>
      ) : (
        <div className="page-heading tests-heading">
          <div>
            <span className="eyebrow">{say('KEYINGI QADAM', 'YOUR NEXT STEP', 'СЛЕДУЮЩИЙ ШАГ')}</span>
            <h1>{t.tests}</h1>
            <p>{openAccess ? say('Sinov rejimi: nashr qilingan testlar ochiq.', 'Test mode: published exams are open.', 'Режим тестирования: опубликованные тесты открыты.') : free ? t.free : t.used}</p>
          </div>
          <Link className="secondary" href="/dashboard/results">{t.results}<ArrowRight size={17} /></Link>
        </div>
      )}

      <nav className="skill-switcher" aria-label={say('Ko‘nikma tanlash', 'Choose a skill', 'Выбор навыка')}>
        {[{name:'All',Icon:Sparkles},...sections].map(({name,Icon}) => (
          <button key={name} className={sectionFilter===name?'active':''} aria-pressed={sectionFilter===name} onClick={()=>setSectionFilter(name)}>
            <Icon size={16}/>{name==='All'?say('Barchasi','All skills','Все навыки'):name}
          </button>
        ))}
      </nav>

      {!selected && (openAccess ? (
        <section className="full-test premium-exam dashboard-full-test-banner">
          <div>
            <span className="badge"><Sparkles size={14} /> {say('SINOV REJIMI', 'TEST MODE', 'РЕЖИМ ТЕСТИРОВАНИЯ')}</span>
            <h2>{t.fullExam}</h2><p>Listening · Reading · Writing · Speaking</p>
            <p className="availability-note">{say('Nashr qilingan Listening, Reading va Writing testlarini ketma-ket topshiring, so‘ng Speaking mashqini bajaring.', 'Take the published Listening, Reading and Writing tests in sequence, then try the Speaking practice.', 'Пройдите опубликованные тесты Listening, Reading и Writing по порядку, затем выполните Speaking.')}</p>
          </div>
          <Link className="primary" href="/dashboard/full-exam">{say('To‘liq imtihonni boshlash', 'Start full exam', 'Начать полный экзамен')} <ArrowRight size={17} /></Link>
        </section>
      ) : (
        <section className="full-test premium-exam dashboard-full-test-banner">
          <div>
            <span className="badge"><Sparkles size={14} /> IELTS ACADEMIC</span>
            <h2>{t.fullExam}</h2><p>Listening · Reading · Writing · Speaking</p><p className="availability-note">{t.fullNote}</p><span className="premium-price">≈ 200 000 UZS</span>
          </div>
          <Link className="secondary" href="/dashboard/payments?exam=IELTS%20Academic"><LockKeyhole size={18}/>{say('Mavjudlik holati','Availability details','Статус доступа')}<ArrowRight size={18}/></Link>
        </section>
      ))}

      <div className="test-catalog-heading" id="test-catalog">
        <div><span className="eyebrow">{selected ? selected.name.toUpperCase() : say('NASHR QILINGAN TESTLAR', 'PUBLISHED TESTS', 'ОПУБЛИКОВАННЫЕ ТЕСТЫ')}</span><h2>{selected ? say(selected.name+' testlari',selected.name+' practice tests','Практика '+selected.name) : say('Mashq uchun testlar','Practice tests','Тесты для практики')}</h2></div>
        <span className="test-count-pill">{selected ? selectedExams.length : exams.length} {say('ta test','tests','тестов')}</span>
      </div>

      <div className="product-test-grid section-test-grid">
        {sections.filter((s)=>sectionFilter==='All'||s.name===sectionFilter).flatMap(({name,Icon,detail})=>{
          const entries=exams.filter((e)=>e.section===name);
          if(entries.length)return entries.map((exam)=>{
            const unavailable=exam.ready===false && !history.some(a=>a.state==='in_progress' && a.section===exam.section && a.title===exam.title);
            const locked=(!openAccess&&!free&&!exam.has_access)||name==='Speaking';
            return <section className={'panel exam-card skill-'+name.toLowerCase()} key={exam.id}>
              <div className="exam-card-top"><span className="skill-icon"><Icon size={24}/></span><span className="access-badge">{unavailable?say('Test tayyor emas','Test unavailable','Тест не готов'):openAccess&&name!=='Speaking'?say('Sinov uchun ochiq','Open for testing','Открыто для тестирования'):locked?<><LockKeyhole size={13}/>{name==='Speaking'?say('Ovozli mashq','Voice practice','Голосовая практика'):say('Pullik','Paid','Платно')}</>:free?t.free:say('Kirish mavjud','Access granted','Доступ открыт')}</span></div>
              <div className="test-card-title"><span className="eyebrow">{name}</span><h3>{exam.title}</h3></div>
              <div className="test-card-stats"><span><CircleHelp size={15}/>{exam.question_count} {t.questions}</span><span><Clock3 size={15}/>{Math.round(exam.duration_seconds/60)} {t.minutes}</span></div>
              <p className="test-card-description">{selected?.summary ? say(...selected.summary) : detail}</p>
              <button className={locked?'secondary':'primary'} disabled={busy||unavailable} onClick={()=>name==='Speaking'?router.push('/dashboard/speaking'):void start(exam)}>{name==='Speaking'?<Mic size={16}/>:locked?<LockKeyhole size={16}/>:<ArrowRight size={16}/>} {unavailable?say('Test ma’lumotlari to‘liq emas','Test content incomplete','Данные теста неполные'):name==='Speaking'?say('Ovozli mashq','Voice practice','Голосовая практика'):locked?say('Mavjudlik holati','Access details','Статус доступа'):t.start}</button>
            </section>;
          });
          return [<section className={'panel exam-card skill-'+name.toLowerCase()} key={name}>
            <div className="exam-card-top"><span className="skill-icon"><Icon size={24}/></span><span className="access-badge"><LockKeyhole size={13}/>{name==='Speaking'?say('AI mashqi','AI practice','Практика с ИИ'):t.soon}</span></div>
            <div className="test-card-title"><span className="eyebrow">{name}</span><h3>{detail}</h3></div>
            <p className="test-card-description">{name==='Speaking'?say('AI bilan jonli ovozli suhbat va uch qismli mashq.', 'Live AI voice conversation across three speaking parts.', 'Живой голосовой диалог с ИИ и практика из трёх частей.'):say('Bu bo‘lim uchun testlar nashr qilinganda shu yerda ko‘rinadi.', 'Published tests for this section will appear here.', 'Опубликованные тесты этого раздела появятся здесь.')}</p>
            <Link className={name==='Speaking'?'primary':'secondary'} href={name==='Speaking'?'/dashboard/speaking':`/dashboard/tests?section=${name}`}>{name==='Speaking'?<Mic size={16}/>:<LockKeyhole size={16}/>} {name==='Speaking'?say('Speakingni boshlash','Start Speaking','Начать Speaking'):t.soon}<ArrowRight size={16}/></Link>
          </section>];
        })}
      </div>
    </div>
  );
}
