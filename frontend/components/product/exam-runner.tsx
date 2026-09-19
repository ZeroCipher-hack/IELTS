'use client';
import {useCallback,useEffect,useRef,useState} from 'react';
import {Check,Clock3,Flag} from 'lucide-react';
import {api,type Attempt} from './api';
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
 return <div className="live-exam"><header className="exam-toolbar"><button className="text-button" disabled={busy} onClick={leave}>← {t.back}</button><strong>{attempt.section}</strong><span className="timer" aria-label={t.remaining}><Clock3 size={18}/>{Math.floor(seconds/60)}:{String(seconds%60).padStart(2,'0')}</span></header><h1>{attempt.title}</h1><p className="product-muted">{t.examEnglish}</p><section className="exam-progress"><div><span>{t.answeredCount}</span><strong>{answered} / {total}</strong></div><progress value={answered} max={total||1} aria-label={`${t.answeredCount}: ${answered} / ${total}`}/></section>{error&&<div role="alert" className="product-alert">{error}<button className="text-button" disabled={busy||seconds===0} onClick={()=>void enqueue().catch(()=>{})}>{t.retry}</button></div>}{seconds===0&&<p role="status" className="product-alert">{t.expired}</p>}<div className="live-exam-grid"><article className="panel live-passage"><span className="eyebrow">{t.passage}</span>{attempt.section==='Listening'&&attempt.audio_url&&<audio controls controlsList="nodownload" src={attempt.audio_url} onError={()=>setError(t.audioError)}/>}<div lang="en" className="passage-copy">{attempt.passage}</div>{attempt.section==='Writing'&&attempt.questions?.map(q=><section key={q.position} className="writing-prompt" lang="en"><h2>Task {q.position}</h2><p>{q.prompt}</p></section>)}</article><section className="panel live-questions"><div className="section-title"><h2>{t.answer}</h2><span className="badge" role="status">{saveState}</span></div><nav className="question-nav" aria-label={t.questions}>{attempt.questions?.map(q=><button key={q.position} className={answers[q.position]?.trim()?'answered':''} aria-label={`${q.position}: ${answers[q.position]?.trim()?t.saved:t.unanswered}${marks.includes(q.position)?', '+t.review:''}`} onClick={()=>document.getElementById('live-q-'+q.position)?.scrollIntoView({block:'center',behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})}>{q.position}{marks.includes(q.position)?<Flag size={12}/>:answers[q.position]?.trim()?<Check size={12}/>:null}</button>)}</nav>{attempt.questions?.map(q=><fieldset className="live-question" id={'live-q-'+q.position} key={q.position} disabled={busy||seconds===0}><legend lang="en">{q.position}. {q.prompt}</legend>{attempt.section==='Writing'?<><textarea aria-label={`Task ${q.position}: ${t.answer}`} className="essay" maxLength={30000} value={answers[q.position]||''} onChange={e=>change(q.position,e.target.value)} lang="en" spellCheck={false}/><p>{(answers[q.position]||'').trim().split(/\s+/).filter(Boolean).length} {t.words}</p></>:q.choices.length?<div className="live-options">{q.choices.map(choice=><label key={choice}><input type="radio" name={'live-'+q.position} value={choice} checked={answers[q.position]===choice} onChange={()=>change(q.position,choice)}/><span lang="en">{choice}</span></label>)}</div>:<input className="short-answer" aria-label={`${q.position}: ${t.answer}`} maxLength={500} value={answers[q.position]||''} onChange={e=>change(q.position,e.target.value)} lang="en"/>}<button type="button" className={'review-button '+(marks.includes(q.position)?'marked':'')} aria-pressed={marks.includes(q.position)} onClick={()=>mark(q.position)}><Flag size={15}/>{t.review}</button></fieldset>)}<button className="primary" disabled={busy} onClick={()=>void submit(seconds===0)}>{busy?t.working:t.finish}</button></section></div></div>
}
