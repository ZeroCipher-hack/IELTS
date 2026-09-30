'use client';
import {useCallback,useEffect,useRef,useState} from 'react';
import {Check,Clock3,Flag} from 'lucide-react';
import {api,type Attempt} from './api';
import ListeningPlayer from './listening-player';
import type {Copy} from './i18n';
export default function ExamRunner({attempt,t,onClose,onComplete}:{attempt:Attempt;t:Copy;onClose:()=>void;onComplete:(a:Attempt)=>void}){
 const [answers,setAnswers]=useState(attempt.answers),[marks,setMarks]=useState(attempt.review_positions||[]),[saveState,setSaveState]=useState(t.saved),[error,setError]=useState(''),[busy,setBusy]=useState(false),[seconds,setSeconds]=useState(1);
 const revision=useRef(0);
 const values=useRef(attempt.answers),marked=useRef(attempt.review_positions||[]),timer=useRef<ReturnType<typeof setTimeout>|null>(null),queue=useRef<Promise<unknown>>(Promise.resolve()),dirty=useRef(false),submitting=useRef(false),alive=useRef(true),expired=useRef(false);
 const clockOffset=useRef(0);
 // Server va client soati orasidagi farqni hisoblash — Date.now faqat effect ichida
 useEffect(()=>{clockOffset.current=Date.parse(attempt.server_time)-Date.now()},[attempt.server_time]);
 const enqueue=useCallback(()=>{
  if(timer.current)clearTimeout(timer.current);
  if(!dirty.current)return queue.current;
  const savedRevision=revision.current;
  const data={answers:{...values.current},review_positions:[...marked.current]};dirty.current=false;
  setSaveState(t.saving);
  const job=queue.current.catch(()=>{}).then(()=>api<Attempt>(`attempts/${attempt.id}/`,'PATCH',data));
  queue.current=job;
  job.then(()=>{if(alive.current&&savedRevision===revision.current)setSaveState(t.saved)}).catch((e:Error)=>{dirty.current=true;if(alive.current){setSaveState(t.saveError);setError(e.message)}});
  return job;
 },[attempt.id,t]);
 const submit=useCallback(async(auto=false)=>{
  if(submitting.current)return;
  if(!auto&&!window.confirm(t.confirmFinish))return;
  submitting.current=true;setBusy(true);setError('');
  try{
   if(timer.current)clearTimeout(timer.current);
   if(!auto)await enqueue();else await queue.current.catch(()=>{});
   const result=await api<Attempt>(`attempts/${attempt.id}/submit/`,'POST',auto?{}:{answers:values.current});
   onComplete(result);
  }catch(e){setError((e as Error).message)}finally{submitting.current=false;setBusy(false)}
 },[attempt.id,enqueue,onComplete,t]);
 useEffect(()=>{alive.current=true;return()=>{alive.current=false;if(timer.current)clearTimeout(timer.current)}},[]);
 useEffect(()=>{
  const tick=()=>{const n=Math.max(0,Math.ceil((Date.parse(attempt.deadline)-Date.now()-clockOffset.current)/1000));setSeconds(n);if(n===0&&!expired.current){expired.current=true;void submit(true)}};
  tick();const interval=setInterval(tick,1000);return()=>clearInterval(interval);
 },[attempt.deadline,submit]);
 useEffect(()=>{const guard=(e:BeforeUnloadEvent)=>{e.preventDefault();e.returnValue=''};window.addEventListener('beforeunload',guard);return()=>window.removeEventListener('beforeunload',guard)},[]);
 function schedule(){revision.current+=1;dirty.current=true;setSaveState(t.saving);if(timer.current)clearTimeout(timer.current);timer.current=setTimeout(()=>{void enqueue().catch(()=>{})},500)}
 function change(position:number,value:string){values.current={...values.current,[position]:value};setAnswers(values.current);schedule()}
 function mark(position:number){marked.current=marked.current.includes(position)?marked.current.filter(p=>p!==position):[...marked.current,position];setMarks(marked.current);schedule()}
 async function leave(){setBusy(true);try{await enqueue();onClose()}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 const total=attempt.questions?.length||0,answered=attempt.questions?.filter(q=>answers[q.position]?.trim()).length||0;

 const words=(value:string)=>(value||'').trim().split(/\s+/).filter(Boolean).length;
 const writingWords=attempt.questions?.reduce((sum,q)=>sum+words(answers[q.position]||''),0)||0;
 const isListening=attempt.section==='Listening',isReading=attempt.section==='Reading',isWriting=attempt.section==='Writing';
 return <div className={'live-exam section-'+attempt.section.toLowerCase()}>
  <header className="exam-toolbar"><button className="text-button" disabled={busy} onClick={leave}>← {t.back}</button><strong>{attempt.section}</strong><span className="timer" aria-label={t.remaining}><Clock3 size={18}/>{Math.floor(seconds/60)}:{String(seconds%60).padStart(2,'0')}</span></header>
  <div className="exam-title-row"><div><span className="eyebrow">{isListening?'IELTS · LISTENING PRACTICE':isReading?'IELTS · ACADEMIC READING':isWriting?'IELTS · WRITING STUDIO':'IELTS · PRACTICE'}</span><h1>{attempt.title}</h1><p className="product-muted">{t.examEnglish}</p></div></div>
  <section className="exam-progress"><div><span>{t.answeredCount}</span><strong>{answered} / {total}</strong></div><progress value={answered} max={total||1} aria-label={`${t.answeredCount}: ${answered} / ${total}`}/></section>
  {error&&<div role="alert" className="product-alert">{error}<button className="text-button" disabled={busy||seconds===0} onClick={()=>void enqueue().catch(()=>{})}>{t.retry}</button></div>}
  {seconds===0&&<p role="status" className="product-alert">{t.expired}</p>}
  <div className={`live-exam-grid ${isWriting?'writing-exam-grid':''}`}>
   <article className={`panel live-passage ${isListening?'listening-passage':isReading?'reading-passage':isWriting?'writing-overview':''}`}>
    {isListening?<><div className="passage-heading"><span className="eyebrow">LISTENING · AUDIO</span><h2>Listen and answer</h2><p>Play the recording and complete the questions in order.</p></div><ListeningPlayer audioUrl={attempt.audio_url} transcript={attempt.passage}/></>
    :isReading?<><div className="passage-heading"><span className="eyebrow">READING · PASSAGE</span><h2>Read the passage</h2><p>Use the passage to find evidence for each answer.</p></div><div lang="en" className="passage-copy reading-copy">{attempt.passage?.split(/\n\s*\n/).filter(Boolean).map((paragraph,index)=><p key={index}>{paragraph}</p>)}</div></>
    :isWriting?<><div className="passage-heading"><span className="eyebrow">WRITING STUDIO</span><h2>Your tasks</h2><p>Plan your response, then write it in the answer panels.</p></div><div className="writing-task-list">{attempt.questions?.map(q=><a className="writing-task-link" key={q.position} href={`#live-q-${q.position}`}><span>Task {q.position}</span><strong>{q.prompt.slice(0,78)}{q.prompt.length>78?'…':''}</strong><small>{words(answers[q.position]||'')} / {q.position===1?150:250} {t.words} · {q.position===1?20:40} min</small></a>)}</div><div className="writing-brief"><strong>Task 1 · 150+ words · ~20 min</strong><strong>Task 2 · 250+ words · ~40 min</strong><p>Task 2 carries twice the weight. The timer covers the whole exam.</p></div>{attempt.passage&&<div className="writing-source-material"><h3>{t.passage}</h3><div lang="en" className="passage-copy">{attempt.passage}</div></div>}<div className="writing-word-summary"><strong>{writingWords}</strong><span>{t.words} total</span></div></>
    :<><span className="eyebrow">{t.passage}</span><div lang="en" className="passage-copy">{attempt.passage}</div></>}
   </article>
   <section className="panel live-questions">
    <div className="section-title"><div><span className="eyebrow">{isWriting?'YOUR RESPONSE':isListening?'LISTENING QUESTIONS':isReading?'READING QUESTIONS':''}</span><h2>{t.answer}</h2></div><span className="badge" role="status">{saveState}</span></div>
    <nav className="question-nav" aria-label={t.questions}>{attempt.questions?.map(q=><button key={q.position} className={answers[q.position]?.trim()?'answered':''} aria-label={`${q.position}: ${answers[q.position]?.trim()?t.saved:t.unanswered}${marks.includes(q.position)?', '+t.review:''}`} onClick={()=>document.getElementById('live-q-'+q.position)?.scrollIntoView({block:'center',behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})}>{q.position}{marks.includes(q.position)?<Flag size={12}/>:answers[q.position]?.trim()?<Check size={12}/>:null}</button>)}</nav>
    {attempt.questions?.map(q=><fieldset className={`live-question ${isWriting?'writing-response':''}`} id={'live-q-'+q.position} key={q.position} disabled={busy||seconds===0}>
     <legend lang="en">{isWriting?<span className="writing-task-number">Task {q.position}</span>:<>{q.position}. {q.prompt}</>}</legend>
     {isWriting&&<><p className="writing-question-prompt" lang="en">{q.prompt}</p><div className="writing-editor-label"><span>Your response</span><span>{words(answers[q.position]||'')} / {q.position===1?150:250} {t.words}</span></div><progress className="writing-word-progress" value={Math.min(words(answers[q.position]||''),q.position===1?150:250)} max={q.position===1?150:250} aria-label={`Task ${q.position}: ${words(answers[q.position]||'')} ${t.words}`}/><textarea aria-label={`Task ${q.position}: ${t.answer}`} className="essay" maxLength={30000} value={answers[q.position]||''} onChange={e=>change(q.position,e.target.value)} lang="en" spellCheck={false}/></>}
     {!isWriting&&q.choices.length>0&&<div className="live-options">{q.choices.map(choice=><label key={choice}><input type="radio" name={'live-'+q.position} value={choice} checked={answers[q.position]===choice} onChange={()=>change(q.position,choice)}/><span lang="en">{choice}</span></label>)}</div>}
     {!isWriting&&!q.choices.length&&<input className="short-answer" aria-label={`${q.position}: ${t.answer}`} maxLength={500} value={answers[q.position]||''} onChange={e=>change(q.position,e.target.value)} lang="en"/>}
     <button type="button" className={'review-button '+(marks.includes(q.position)?'marked':'')} aria-pressed={marks.includes(q.position)} onClick={()=>mark(q.position)}><Flag size={15}/>{t.review}</button>
    </fieldset>)}
    <button className="primary" disabled={busy} onClick={()=>void submit(seconds===0)}>{busy?t.working:t.finish}</button>
   </section>
  </div>
 </div>
}
