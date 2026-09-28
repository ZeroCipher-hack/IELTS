'use client';
import { useEffect, useRef, useState } from 'react';
import { Play, Square, Volume2 } from 'lucide-react';
import { chooseListeningSource } from './listening-audio';

export default function ListeningPlayer({ audioUrl, transcript }: { audioUrl?: string; transcript?: string }) {
  const source = audioUrl?.startsWith('https://') || audioUrl?.startsWith('/media/exam_audio/') ? audioUrl : '';
  const script = transcript?.trim() || '';
  const audio = useRef<HTMLAudioElement>(null);
  const utterance = useRef<SpeechSynthesisUtterance | null>(null);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[] | null>(null);
  const [fileError, setFileError] = useState('');
  const [speechError, setSpeechError] = useState('');
  const [filePlaying, setFilePlaying] = useState(false);
  const [speechPlaying, setSpeechPlaying] = useState(false);

  useEffect(() => {
    if (!('speechSynthesis' in window)) { setVoices([]); return; }
    const synth = window.speechSynthesis;
    const update = () => {
      const available = synth.getVoices();
      if (available.length) setVoices(available);
    };
    synth.addEventListener('voiceschanged', update);
    update();
    const timer = setTimeout(() => setVoices(current => current ?? synth.getVoices()), 2500);
    return () => {
      clearTimeout(timer);
      synth.removeEventListener('voiceschanged', update);
      synth.cancel();
    };
  }, []);

  async function playFile() {
    if (!audio.current) return;
    if (filePlaying) { audio.current.pause(); setFilePlaying(false); return; }
    try {
      if (fileError) audio.current.load();
      await audio.current.play(); // Always called from the Play / Retry click.
      setFileError('');
      setFilePlaying(true);
    } catch {
      setFilePlaying(false);
      setFileError('Recording could not be played. Retry or use the sample transcript below.');
    }
  }

  function playSpeech() {
    if (!voices?.length || !script || !('speechSynthesis' in window)) return;
    const synth = window.speechSynthesis;
    if (synth.speaking || synth.pending) { synth.cancel(); setSpeechPlaying(false); return; }
    const spoken = new SpeechSynthesisUtterance(script);
    utterance.current = spoken;
    spoken.lang = 'en-GB';
    spoken.rate = 0.88;
    spoken.voice = voices.find(voice => /^en[-_]/i.test(voice.lang)) || voices[0];
    let started = false;
    const timer = setTimeout(() => {
      if (!started) { synth.cancel(); setSpeechPlaying(false); setSpeechError('Browser speech is unavailable. Read the sample transcript below.'); }
    }, 3500);
    spoken.onstart = () => { started = true; clearTimeout(timer); setSpeechPlaying(true); };
    spoken.onend = () => { clearTimeout(timer); setSpeechPlaying(false); utterance.current = null; };
    spoken.onerror = () => { clearTimeout(timer); setSpeechPlaying(false); setSpeechError('Browser speech failed. Read the sample transcript below.'); utterance.current = null; };
    try { setSpeechError(''); synth.speak(spoken); }
    catch { clearTimeout(timer); setSpeechError('Browser speech failed. Read the sample transcript below.'); }
  }

  const fallback = chooseListeningSource(source || '', script, Boolean(fileError), voices?.length ?? null);
  return <>
    {source && <div className="audio-player-card">
      <div className="audio-player-icon"><Volume2 size={20}/></div>
      <div className="audio-player-copy"><strong>Listening recording</strong><span>Press Play to start the recording.</span></div>
      <audio ref={audio} preload="none" src={source} onEnded={() => setFilePlaying(false)} onError={() => { setFilePlaying(false); setFileError('Recording could not be loaded. Retry or use the fallback below.'); }} />
      <button type="button" className="primary" onClick={() => void playFile()}>{filePlaying ? <Square size={17}/> : <Play size={17}/>} {filePlaying ? 'Pause' : fileError ? 'Retry recording' : 'Play recording'}</button>
    </div>}
    {fileError && <p className="product-alert" role="alert">{fileError}</p>}
    {fallback === 'waiting' && <p role="status" className="product-muted">Checking available browser voices…</p>}
    {fallback === 'speech' && !speechError && <div className="audio-player-card">
      <div className="audio-player-icon"><Volume2 size={20}/></div>
      <div className="audio-player-copy"><strong>Browser voice sample</strong><span>Press Play to hear the practice transcript.</span></div>
      <button type="button" className="primary" onClick={playSpeech}>{speechPlaying ? <Square size={17}/> : <Play size={17}/>} {speechPlaying ? 'Stop sample' : 'Play sample'}</button>
    </div>}
    {(fallback === 'transcript' || fallback === 'missing' || (fallback !== 'file' && Boolean(speechError))) && <div className="product-muted listening-fallback" role="status">
      <p>{speechError || 'No browser voice is available. This transcript helps check demo questions; it does not test listening skill.'}</p>
      {script && <details open><summary>Sample transcript</summary><p lang="en">{script}</p></details>}
    </div>}
  </>;
}
