'use client';
import {useEffect,useRef,useState} from 'react';
import {api} from './api';
export default function VoicePilot(){
 const [status,setStatus]=useState('Tayyor'),[running,setRunning]=useState(false);
 const release=useRef<()=>void>(()=>{}),generation=useRef(0);
 function stop(){generation.current++;release.current();setRunning(false);setStatus('To‘xtatildi')}
 useEffect(()=>()=>{generation.current++;release.current()},[]);
 async function start(){
  const id=++generation.current;setRunning(true);setStatus('Mikrofon ochilmoqda…');
  let stream:MediaStream|undefined,ctx:AudioContext|undefined,socket:WebSocket|undefined,node:AudioWorkletNode|undefined,timeout:ReturnType<typeof setTimeout>|undefined;
  const sources=new Set<AudioBufferSourceNode>();let nextPlay=0;
  const cleanup=()=>{if(timeout)clearTimeout(timeout);node?.disconnect();stream?.getTracks().forEach(t=>t.stop());socket?.close();for(const source of sources){try{source.stop()}catch{}}sources.clear();void ctx?.close().catch(()=>{})};release.current=cleanup;
  try{
   stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true},video:false});if(id!==generation.current){cleanup();return}
   ctx=new AudioContext({sampleRate:16000});await ctx.resume();await ctx.audioWorklet.addModule('/audio/capture.js');
   const credentials=await api<{token:string;model:string;expires_in:number}>('voice/token/','POST',{});if(id!==generation.current){cleanup();return}
   socket=new WebSocket('wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?access_token='+encodeURIComponent(credentials.token));
   socket.onopen=()=>{socket!.send(JSON.stringify({setup:{model:credentials.model,generationConfig:{responseModalities:['AUDIO']}}}));setStatus('AI ulanmoqda…')};
   socket.onmessage=async event=>{
    if(id!==generation.current)return;
    try{
     const message=JSON.parse(typeof event.data==='string'?event.data:await event.data.text());
     if(message.setupComplete){
      setStatus('Suhbat boshlandi — inglizcha gapiring');
      node=new AudioWorkletNode(ctx!,'ielts-capture');const source=ctx!.createMediaStreamSource(stream!);source.connect(node);const mute=ctx!.createGain();mute.gain.value=0;node.connect(mute);mute.connect(ctx!.destination);
      node.port.onmessage=e=>{if(socket?.readyState!==WebSocket.OPEN||socket.bufferedAmount>65536)return;const input=e.data as Float32Array;const bytes=new Uint8Array(input.length*2);const view=new DataView(bytes.buffer);input.forEach((n,i)=>view.setInt16(i*2,Math.max(-32768,Math.min(32767,Math.round(n*32767))),true));let binary='';for(const b of bytes)binary+=String.fromCharCode(b);socket.send(JSON.stringify({realtimeInput:{audio:{mimeType:'audio/pcm;rate='+ctx!.sampleRate,data:btoa(binary)}}}))};
      socket!.send(JSON.stringify({clientContent:{turns:[{role:'user',parts:[{text:'Start the speaking practice. Ask me your first question.'}]}],turnComplete:true}}));
     }
     const content=message.serverContent;
     if(content?.interrupted){for(const source of sources){try{source.stop()}catch{}}sources.clear();nextPlay=ctx!.currentTime}
     for(const part of content?.modelTurn?.parts||[]){if(!part.inlineData?.data)continue;const binary=atob(part.inlineData.data);const raw=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)raw[i]=binary.charCodeAt(i);const view=new DataView(raw.buffer);const rate=Number(/rate=(\d+)/.exec(part.inlineData.mimeType||'')?.[1]||24000);const buffer=ctx!.createBuffer(1,Math.floor(raw.length/2),rate);const channel=buffer.getChannelData(0);for(let i=0;i<channel.length;i++)channel[i]=view.getInt16(i*2,true)/32768;const source=ctx!.createBufferSource();source.buffer=buffer;source.connect(ctx!.destination);sources.add(source);source.onended=()=>sources.delete(source);nextPlay=Math.max(nextPlay,ctx!.currentTime);source.start(nextPlay);nextPlay+=buffer.duration;}
    }catch{setStatus('Audio javobini qayta ishlashda xato');cleanup();setRunning(false)}
   };
   socket.onerror=()=>{if(id===generation.current)setStatus('AI ulanishida xato. Kalit va model ruxsatini tekshiring.')};
   socket.onclose=()=>{if(id===generation.current){cleanup();setRunning(false);setStatus('Ulanish yopildi. Yangi sinov boshlashingiz mumkin.')}};
   timeout=setTimeout(()=>{if(id===generation.current)stop()},credentials.expires_in*1000);
  }catch{cleanup();if(id===generation.current){setRunning(false);setStatus('Ulanmadi: mikrofon ruxsati, server kaliti yoki bepul limitni tekshiring.')}}
 }
 return <section className="panel" style={{marginTop:24}}><h2>Speaking · administrator sinovi</h2><p style={{margin:'16px 0'}}>5 daqiqalik Gemini ovozli suhbat. Ovoz bevosita Google’ga yuboriladi. Bu sinov yozuvni saqlamaydi va IELTS bandini chiqarmaydi.</p><p role="status" style={{marginBottom:16}}>{status}</p><button className="primary" onClick={()=>running?stop():void start()}>{running?'Suhbatni to‘xtatish':'Ovozli AI’ni sinash'}</button></section>
}
