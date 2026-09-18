'use client';
import {useEffect,useRef,useState} from 'react';
import {ArrowLeft,Mic,MicOff,Square,Volume2,Clock3,RefreshCw} from 'lucide-react';
import ExaminerAvatar from './examiner-avatar';
import {api,type Language,type Attempt} from './api';
type Phase='idle'|'connecting'|'mic-test'|'part1'|'prepare'|'part2'|'part3'|'done'|'error';
type Status={configured:boolean;allowed:boolean;reason:string;cue:{title:string;points:string[]}};
type Entry={role:'AI'|'You';text:string};
export default function VoicePilot({language='uz',onBack,onSubmitted}:{language?:Language;onBack?:()=>void;onSubmitted?:(attempt:Attempt)=>void}){
 const say=(uz:string,en:string,ru:string)=>language==='uz'?uz:language==='en'?en:ru;
 const [status,setStatus]=useState<Status|null>(null),[phase,setPhase]=useState<Phase>('idle'),[error,setError]=useState(''),[seconds,setSeconds]=useState(0),[level,setLevel]=useState(0),[speaking,setSpeaking]=useState(false),[muted,setMuted]=useState(false),[transcript,setTranscript]=useState<Entry[]>([]),[part,setPart]=useState(1),[audioBlocked,setAudioBlocked]=useState(false);
 const recordings=useRef<Promise<Blob>[]>([]),submissionId=useRef(''),recordingFailed=useRef(false);
 const [saving,setSaving]=useState(false),[consent,setConsent]=useState(false);
 const faceRef=useRef<HTMLDivElement|null>(null);
 const audioRef=useRef<AudioContext|null>(null);
 const generation=useRef(0),release=useRef<()=>void>(()=>{}),deadline=useRef(0),advance=useRef<()=>void>(()=>{}),socketRef=useRef<WebSocket|null>(null),streamRef=useRef<MediaStream|null>(null),mutedRef=useRef(false),entries=useRef<Entry[]>([]),guard=useRef(false);
 const active=['connecting','mic-test','part1','prepare','part2','part3'].includes(phase);
 function message(code:string){const errors:Record<string,string>={
  AI_NOT_CONFIGURED:say('Serverda AI yoqilmagan yoki Gemini kaliti kiritilmagan.','AI is disabled or the server Gemini key is missing.','ИИ отключён или на сервере нет ключа Gemini.'),
  VOICE_PRACTICE_DISABLED:say('Talabalar uchun ovozli mashq hali ochilmagan. Administrator hisobida sinash mumkin.','Student voice practice is not enabled. Staff can test it.','Голосовая практика для учеников пока не включена. Доступен тест администратора.'),
  AI_RATE_LIMIT:say('AI limiti tugadi. Keyinroq qayta urinib ko‘ring.','AI quota reached. Please try again later.','Лимит ИИ исчерпан. Повторите позже.'),
  AI_PROVIDER_ERROR:say('AI kaliti yoki tanlangan modelga ruxsatni tekshiring.','Check the server API key and model access.','Проверьте ключ API и доступ к модели.'),
  NotAllowedError:say('Brauzerda mikrofon ruxsatini yoqing.','Allow microphone access in your browser.','Разрешите доступ к микрофону в браузере.'),
  NotFoundError:say('Mikrofon topilmadi. Uni ulang va qayta sinang.','No microphone found. Connect one and retry.','Микрофон не найден. Подключите его и повторите.'),
  NotReadableError:say('Mikrofonni boshqa dastur band qilgan bo‘lishi mumkin.','Your microphone may be in use by another application.','Микрофон может быть занят другим приложением.'),
  INSECURE:say('Mikrofon uchun localhost yoki HTTPS orqali oching.','Open this page through localhost or HTTPS to use the microphone.','Для микрофона откройте сайт через localhost или HTTPS.'),
  UPLOAD_STALLED:say('Mikrofon audiosini yuborish sekinlashdi va navbat to‘lib qoldi. Internet yuklamasini kamaytirib, qayta boshlang.','Microphone upload stalled and the audio queue filled. Reduce network traffic and restart.','Передача аудио замедлилась, очередь заполнена. Снизьте нагрузку на сеть и начните заново.'),
  TIMEOUT:say('AI ulanishi javob bermadi. Internet va modelni tekshiring.','AI connection timed out. Check your network and model.','Время подключения ИИ истекло. Проверьте сеть и модель.'),
  CLOSED:say('AI ulanishi uzildi. Mashq to‘liq yakunlanmadi; qayta boshlashingiz mumkin.','AI disconnected. Practice was interrupted; you can restart.','Связь с ИИ прервалась. Практика не завершена; можно начать заново.'),
  RECORDING:say('Audio yozib olinmadi. Boshqa brauzerda sinang.','Audio recording failed. Try another browser.','Не удалось записать аудио. Попробуйте другой браузер.'),
  NO_AUDIO:say('AI ulandi, lekin ovoz yubormadi. Model va API limitini tekshiring.','AI connected but sent no audio. Check the model and API quota.','ИИ подключён, но аудио не поступило. Проверьте модель и лимит API.'),
  AUDIO:say('AI audiosini o‘qishda xato yuz berdi.','The AI audio response could not be decoded.','Не удалось обработать аудио ИИ.')};return errors[code]||say('Ulanish xatosi. Mikrofon, internet va server sozlamalarini tekshiring.','Connection failed. Check microphone, network and server settings.','Ошибка подключения. Проверьте микрофон, сеть и сервер.');}
 async function check(){setError('');try{setStatus(await api<Status>('voice/status/'))}catch(e){setError(message((e as Error).message))}}
 // Voice statusni mountda bir marta yuklash — fetch on mount, cleanup da generatsiyani oshirish intentional
 useEffect(()=>{let alive=true;api<Status>('voice/status/').then(s=>{if(alive)setStatus(s)}).catch(()=>{if(alive)setError(say('Serverga ulanib bo‘lmadi.','Could not reach the server.','Не удалось подключиться к серверу.'))});return()=>{alive=false;generation.current++;release.current()}},[]);
 function cleanup(){generation.current++;release.current();release.current=()=>{};socketRef.current=null;streamRef.current=null;guard.current=false;setSpeaking(false);setAudioBlocked(false);audioRef.current=null;setLevel(0);setMuted(false);mutedRef.current=false}
 function stop(){cleanup();setPhase('done');setTranscript([...entries.current]);setSeconds(0)}
 function fail(code:string){cleanup();setPhase('error');setError(message(code));setTranscript([...entries.current])}
 function append(role:Entry['role'],text:string){if(!text)return;const all=entries.current;if(all.reduce((n,e)=>n+e.text.length,0)>60000)return;const last=all[all.length-1];if(last?.role===role)last.text+=text;else all.push({role,text})}
 // Phase bo'yicha keyingi bosqichga o'tish — advance ref ni phase bilan sinxronlash, connect/stop barqaror ref orqali chaqiriladi
 useEffect(()=>{advance.current=()=>{if(phase==='part1'){cleanup();setPart(2);deadline.current=Date.now()+60000;setSeconds(60);setPhase('prepare')}else if(phase==='prepare'){void connect(2)}else if(phase==='part2'){void connect(3)}else stop()}},[phase]);
 useEffect(()=>{if(!['part1','prepare','part2','part3','mic-test'].includes(phase))return;const tick=()=>{const n=Math.max(0,Math.ceil((deadline.current-Date.now())/1000));setSeconds(n);if(!n){if(phase==='mic-test'){cleanup();setPhase('idle')}else advance.current()}};tick();const timer=setInterval(tick,250);return()=>clearInterval(timer)},[phase]);
 useEffect(()=>{if(!active)return;const before=(e:BeforeUnloadEvent)=>{e.preventDefault();e.returnValue=''};window.addEventListener('beforeunload',before);return()=>window.removeEventListener('beforeunload',before)},[active]);
 async function connect(selectedPart:number,localOnly=false){
  if(guard.current)return;cleanup();guard.current=true;const id=++generation.current;setError('');setPhase('connecting');setPart(selectedPart);
  let ctx:AudioContext|undefined,stream:MediaStream|undefined,socket:WebSocket|undefined,node:AudioWorkletNode|undefined,timeout:ReturnType<typeof setTimeout>|undefined,closed=false,nextPlay=0,receivedAudio=false,congestedSince=0;
  let firstAudioTimer:ReturnType<typeof setTimeout>|undefined;
  let recorder:MediaRecorder|undefined;
  let analyser:AnalyserNode|undefined,rafId=0;
  const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
  const sources=new Set<AudioBufferSourceNode>();
  const dispose=()=>{if(closed)return;closed=true;if(recorder&&recorder.state!=='inactive')recorder.stop();cancelAnimationFrame(rafId);faceRef.current?.style.setProperty('--speech','0');analyser?.disconnect();if(firstAudioTimer)clearTimeout(firstAudioTimer);if(timeout)clearTimeout(timeout);node?.disconnect();stream?.getTracks().forEach(track=>track.stop());if(socket){socket.onclose=null;socket.onerror=null;socket.onmessage=null;socket.close()}for(const source of sources){try{source.stop()}catch{}}sources.clear();void ctx?.close().catch(()=>{})};release.current=dispose;
  try{
   if(!window.isSecureContext||!navigator.mediaDevices?.getUserMedia)throw new Error('INSECURE');
   ctx=new AudioContext({sampleRate:16000});audioRef.current=ctx;await ctx.resume();ctx.onstatechange=()=>{if(id===generation.current)setAudioBlocked(ctx!.state==='suspended')};
   if(id!==generation.current){dispose();return}
   analyser=ctx.createAnalyser();analyser.fftSize=256;analyser.connect(ctx.destination);
   const wave=new Uint8Array(analyser.fftSize);
   let lastFrame=0;
   const animate=(time:number)=>{
    if(closed||id!==generation.current)return;
    if(time-lastFrame>=33){lastFrame=time;let amplitude=0;
     if(!motion.matches&&ctx!.state==='running'&&sources.size){analyser!.getByteTimeDomainData(wave);let sum=0;for(const n of wave)sum+=((n-128)/128)**2;amplitude=Math.min(1,Math.sqrt(sum/wave.length)*6)}
     faceRef.current?.style.setProperty('--speech',amplitude.toFixed(3));
    }
    rafId=requestAnimationFrame(animate);
   };
   if(!localOnly)rafId=requestAnimationFrame(animate);
   stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true},video:false});if(id!==generation.current){stream.getTracks().forEach(t=>t.stop());dispose();return}streamRef.current=stream;
   await ctx.audioWorklet.addModule('/audio/capture.js');if(id!==generation.current){dispose();return}
   const startCapture=()=>{
    node=new AudioWorkletNode(ctx!,'ielts-capture');const input=ctx!.createMediaStreamSource(stream!);input.connect(node);const silent=ctx!.createGain();silent.gain.value=0;node.connect(silent);silent.connect(ctx!.destination);
    node.port.onmessage=e=>{if(id!==generation.current)return;const samples=e.data as Float32Array;const rms=Math.sqrt(samples.reduce((sum,n)=>sum+n*n,0)/samples.length);setLevel(mutedRef.current?0:Math.min(1,rms*6));if(localOnly||mutedRef.current||socket?.readyState!==WebSocket.OPEN)return;if(socket.bufferedAmount>65536){if(!congestedSince)congestedSince=performance.now();if(socket.bufferedAmount>524288||performance.now()-congestedSince>5000){fail('UPLOAD_STALLED');return}}else congestedSince=0;const bytes=new Uint8Array(samples.length*2),view=new DataView(bytes.buffer);samples.forEach((n,i)=>view.setInt16(i*2,Math.max(-32768,Math.min(32767,Math.round(n*32767))),true));let raw='';for(const b of bytes)raw+=String.fromCharCode(b);socket.send(JSON.stringify({realtimeInput:{audio:{mimeType:'audio/pcm;rate='+ctx!.sampleRate,data:btoa(raw)}}}))};
   };
   if(localOnly){startCapture();deadline.current=Date.now()+15000;setSeconds(15);setPhase('mic-test');guard.current=false;return}
   const credentials=await api<{token:string;model:string;expires_in:number}>('voice/token/','POST',{part:selectedPart});if(id!==generation.current){dispose();return}
   socket=new WebSocket('wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContentConstrained?access_token='+encodeURIComponent(credentials.token));socketRef.current=socket;
   timeout=setTimeout(()=>{if(id===generation.current)fail('TIMEOUT')},20000);
   socket.onopen=()=>{if(id!==generation.current)return;socket!.send(JSON.stringify({setup:{model:credentials.model,generationConfig:{responseModalities:['AUDIO']},inputAudioTranscription:{},outputAudioTranscription:{}}}))};
   let messages=Promise.resolve();
   socket.onmessage=event=>{messages=messages.then(async()=>{
    if(id!==generation.current)return;const raw=typeof event.data==='string'?event.data:await event.data.text();if(id!==generation.current)return;const data=JSON.parse(raw);
    if(data.error){fail('AI_PROVIDER_ERROR');return}
    if(data.setupComplete){
     if(typeof MediaRecorder==='undefined'){fail('RECORDING');return}
     const mime=['audio/webm;codecs=opus','audio/ogg;codecs=opus','audio/mp4'].find(m=>MediaRecorder.isTypeSupported(m));
     if(!mime){fail('RECORDING');return}
     recorder=new MediaRecorder(stream!,{mimeType:mime,audioBitsPerSecond:48000});
     const chunks:Blob[]=[];let bytes=0;
     recordings.current.push(new Promise(resolve=>{
      recorder!.ondataavailable=e=>{if(e.data.size){bytes+=e.data.size;if(bytes>4*1024*1024){recordingFailed.current=true;fail('RECORDING');return}chunks.push(e.data)}};
      recorder!.onstop=()=>resolve(new Blob(chunks,{type:mime.split(';')[0]}));
      recorder!.onerror=()=>{recordingFailed.current=true;resolve(new Blob());if(id===generation.current)fail('RECORDING')};
     }));recorder.start(1000);
     if(timeout)clearTimeout(timeout);firstAudioTimer=setTimeout(()=>{if(id===generation.current&&!receivedAudio)fail('NO_AUDIO')},30000);startCapture();deadline.current=Date.now()+(selectedPart===2?120000:240000);setSeconds(selectedPart===2?120:240);setPhase(('part'+selectedPart) as Phase);guard.current=false;socket!.send(JSON.stringify({clientContent:{turns:[{role:'user',parts:[{text:'Begin this speaking practice part now. Ask the first question in English.'}]}],turnComplete:true}}))}
    if(data.goAway){fail('CLOSED');return}
    const content=data.serverContent;if(content?.inputTranscription?.text)append('You',content.inputTranscription.text);if(content?.outputTranscription?.text)append('AI',content.outputTranscription.text);
    if(content?.interrupted){for(const source of sources){try{source.stop()}catch{}}sources.clear();nextPlay=ctx!.currentTime;setSpeaking(false)}
    for(const part of content?.modelTurn?.parts||[]){if(!part.inlineData?.data)continue;receivedAudio=true;if(firstAudioTimer)clearTimeout(firstAudioTimer);if(ctx!.state==='suspended'){await ctx!.resume();if(id!==generation.current)return;setAudioBlocked(ctx!.state==='suspended')}const binary=atob(part.inlineData.data),rate=Number(/rate=(\d+)/.exec(part.inlineData.mimeType||'')?.[1]||24000);if(binary.length%2||binary.length>2000000||!Number.isFinite(rate)||rate<8000||rate>48000)throw new Error('AUDIO');const bytes=Uint8Array.from(binary,c=>c.charCodeAt(0)),view=new DataView(bytes.buffer),buffer=ctx!.createBuffer(1,binary.length/2,rate);const channel=buffer.getChannelData(0);for(let i=0;i<channel.length;i++)channel[i]=view.getInt16(i*2,true)/32768;const source=ctx!.createBufferSource();source.buffer=buffer;source.connect(analyser!);sources.add(source);source.onended=()=>{sources.delete(source);if(id===generation.current&&sources.size===0)setSpeaking(false)};nextPlay=Math.max(nextPlay,ctx!.currentTime);source.start(nextPlay);nextPlay+=buffer.duration;setSpeaking(true)}
   }).catch(()=>{if(id===generation.current)fail('AUDIO')})};
   socket.onerror=()=>{if(id===generation.current)fail('CLOSED')};socket.onclose=event=>{if(id===generation.current)fail(event.code===1008?'AI_PROVIDER_ERROR':event.code===1013?'AI_RATE_LIMIT':'CLOSED')};
  }catch(e){dispose();if(id===generation.current)fail(e instanceof DOMException?e.name:(e as Error).message)}
 }
 async function submitFeedback(){
  if(saving)return;setSaving(true);setError('');
  try{
   const clips=await Promise.all(recordings.current);
   if(recordingFailed.current||!clips.length||clips.some(b=>!b.size))throw new Error(message('RECORDING'));
   const form=new FormData();form.set('id',submissionId.current);form.set('consent','yes');form.set('transcript',entries.current.filter(e=>e.role==='You').map(e=>e.text).join('\n'));
   clips.forEach((clip,i)=>form.append('audio',clip,'part-'+(i+1)));
   const csrf=document.cookie.split('; ').find(c=>c.startsWith('csrftoken='))?.slice(10)||'';
   const response=await fetch('/api/voice/submit/',{method:'POST',credentials:'same-origin',headers:{'X-CSRFToken':decodeURIComponent(csrf)},body:form,signal:AbortSignal.timeout(60000)});
   const data=await response.json();if(!response.ok)throw new Error(data.error||'Upload failed');
   recordings.current=[];onSubmitted?.(data);
  }catch(e){setError((e as Error).message)}finally{setSaving(false)}
 }
 function toggleMute(){const value=!mutedRef.current;mutedRef.current=value;setMuted(value);streamRef.current?.getAudioTracks().forEach(t=>t.enabled=!value);if(value&&socketRef.current?.readyState===WebSocket.OPEN)socketRef.current.send(JSON.stringify({realtimeInput:{audioStreamEnd:true}}))}
 async function testSpeaker(){try{const ctx=new AudioContext();await ctx.resume();const tone=ctx.createOscillator(),gain=ctx.createGain();gain.gain.value=.08;tone.frequency.value=440;tone.connect(gain);gain.connect(ctx.destination);tone.start();tone.stop(ctx.currentTime+.4);tone.onended=()=>void ctx.close()}catch{setError(message('AUDIO'))}}
 const title=phase==='done'?say('Suhbat tugadi','Conversation ended','Беседа завершена'):phase==='error'?say('Ulanish to‘xtadi','Connection stopped','Подключение прервано'):phase==='connecting'?say('Ulanmoqda…','Connecting…','Подключение…'):phase==='prepare'?say('Tayyorlanish','Preparation','Подготовка'):phase==='mic-test'?say('Mikrofon tekshiruvi','Microphone check','Проверка микрофона'):active?muted?say('Mikrofon o‘chirilgan','Microphone muted','Микрофон выключен'):speaking?say('AI gapirmoqda','AI is speaking','ИИ говорит'):say('Sizni tinglamoqda','Listening to you','Слушает вас'):say('Suhbatga tayyor','Ready to practise','Готов к практике');
 return <div className="speaking-studio"><div className="page-heading"><div><span className="eyebrow">IELTSQA · SPEAKING PRACTICE</span><h1>{say('AI bilan suhbat','Speak with AI','Разговор с ИИ')}</h1></div>{onBack&&<button className="secondary" onClick={()=>{if(active&&!window.confirm(say('Mashqni to‘xtatib chiqasizmi?','Stop practice and leave?','Остановить практику и выйти?')))return;cleanup();onBack()}}><ArrowLeft size={18}/>{say('Qaytish','Back','Назад')}</button>}</div><p className="product-muted">{say('Ovoz va javoblar AI baholashiga yuboriladi. Audio baholash tugagach o‘chiriladi; hisobot hisobingizda saqlanadi.','Audio and answers are sent for AI assessment. Audio is deleted after assessment; the report stays in your account.','Аудио и ответы отправляются для оценки ИИ. После оценки аудио удаляется; отчёт сохраняется в аккаунте.')}</p>{error&&<div className="product-alert" role="alert">{error}</div>}{status?.reason&&!active&&<div className="panel voice-availability"><p>{message(status.reason)}</p><button className="text-button" onClick={()=>void check()}><RefreshCw size={16}/>{say('Qayta tekshirish','Check again','Проверить снова')}</button></div>}<div className="speaking-layout"><section className="panel examiner-stage"><div className="speaking-stage-top"><span className="badge">{active?'Part '+part:say('Ovozli mashq','Voice practice','Голосовая практика')}</span><span className="timer"><Clock3 size={18}/>{Math.floor(seconds/60)}:{String(seconds%60).padStart(2,'0')}</span></div><ExaminerAvatar faceRef={faceRef} speaking={speaking&&!audioBlocked} listening={['part1','part2','part3'].includes(phase)&&!speaking&&!muted} label={say('Nova — AI imtihon oluvchi','Nova — AI examiner','Нова — ИИ-экзаменатор')}/><p className="voice-state" role="status">{title}</p><div className="voice-wave" aria-hidden="true">{Array.from({length:36},(_,i)=><span key={i} style={{height:4+level*64*(.3+.7*Math.abs(Math.sin(i*1.7)))}}/>)}</div>{audioBlocked&&<button className="primary" onClick={()=>{void audioRef.current?.resume().then(()=>setAudioBlocked(audioRef.current?.state!=='running')).catch(()=>setError(message('AUDIO')))}}><Volume2 size={18}/>{say('AI ovozini yoqish','Enable AI audio','Включить звук ИИ')}</button>}{!active&&<label className="voice-consent"><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/>{say('Audio va javoblarim AI baholashiga yuborilishiga roziman.','I agree to send my audio and answers for AI assessment.','Согласен отправить аудио и ответы для оценки ИИ.')}</label>}<div className="voice-controls">{active?<><button className="secondary" disabled={phase==='connecting'||phase==='prepare'} onClick={toggleMute}>{muted?<MicOff size={20}/>:<Mic size={20}/>} {muted?say('Mikrofonni yoqish','Unmute','Включить микрофон'):say('Mikrofonni o‘chirish','Mute','Выключить микрофон')}</button><button className="secondary" onClick={stop}><Square size={18}/>{say('Yakunlash','End practice','Завершить')}</button></>:<><button className="primary" disabled={saving||!consent||!status?.configured||!status.allowed} onClick={()=>{entries.current=[];recordings.current=[];recordingFailed.current=false;submissionId.current=crypto.randomUUID();setTranscript([]);void connect(1)}}><Mic size={20}/>{say('Suhbatni boshlash','Start conversation','Начать разговор')}</button><button className="secondary" onClick={()=>void connect(1,true)}>{say('Mikrofonni tekshirish','Test microphone','Проверить микрофон')}</button><button className="secondary" onClick={()=>void testSpeaker()}><Volume2 size={18}/>{say('Ovozni tekshirish','Test speaker','Проверить звук')}</button></>}</div></section><aside className="panel speaking-guide"><h2>{say('Suhbat bosqichlari','Conversation stages','Этапы беседы')}</h2><ol>{[['Part 1','4:00'],[say('Tayyorlanish','Preparation','Подготовка'),'1:00'],['Part 2','2:00'],['Part 3','4:00']].map(([label,time],i)=><li key={label} aria-current={phase===['part1','prepare','part2','part3'][i]?'step':undefined}><span>{label}</span><span>{time}</span></li>)}</ol>{(phase==='prepare'||phase==='part2')&&status&&<div className="speaking-cue" lang="en"><h3>{status.cue.title}</h3><ul>{status.cue.points.map(p=><li key={p}>{p}</li>)}</ul></div>}<p>{say('Inglizcha javob bering. Bosqichlar vaqt tugaganda avtomatik almashadi. Tarjima va tayyor javoblar suhbat davomida ko‘rsatilmaydi.','Answer in English. Stages advance automatically when time runs out. Translations and model answers are hidden during the conversation.','Отвечайте на английском. Этапы переключаются по таймеру. Перевод и готовые ответы во время беседы не показываются.')}</p></aside></div>{(phase==='done'||phase==='error')&&<section className="panel speaking-transcript"><button className="primary" disabled={saving||!consent||!transcript.some(e=>e.role==='You')} onClick={()=>void submitFeedback()}>{saving?say('Yuborilmoqda…','Uploading…','Отправка…'):say('Baholash va natijani saqlash','Assess and save result','Оценить и сохранить результат')}</button><h2>{say('Suhbat matni','Conversation transcript','Текст беседы')}</h2><p>{say('Natijani saqlash tugmasini bosing. Yubormasdan sahifadan chiqsangiz yozuv yo‘qoladi.','Submit for feedback before leaving, otherwise this recording will be lost.','Отправьте запись для оценки перед выходом, иначе она будет потеряна.')}</p>{transcript.length?transcript.map((e,i)=><div key={i}><strong>{e.role==='AI'?'AI Examiner':say('Siz','You','Вы')}</strong><p lang="en">{e.text}</p></div>):<p>{say('Suhbat matni olinmadi.','No transcript was received.','Текст беседы не получен.')}</p>}</section>}</div>
}
