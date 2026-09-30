'use client';
import { useEffect, useRef, useState } from 'react';
import { Play, Pause, Square, Volume2 } from 'lucide-react';
import { audioTime, chooseEnglishVoice, chooseListeningSource } from './listening-audio';

export default function ListeningPlayer({ audioUrl, transcript }: { audioUrl?: string; transcript?: string }) {
  const source = audioUrl?.startsWith('https://') || audioUrl?.startsWith('/media/exam_audio/') ? audioUrl : '';
  const script = transcript?.trim() || '';
  const audio = useRef<HTMLAudioElement>(null);
  const utterance = useRef<SpeechSynthesisUtterance | null>(null);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[] | null>(null);
  const [fileError, setFileError] = useState('');
  const [speechError, setSpeechError] = useState('');
  const speechTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [duration, setDuration] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [volume, setVolume] = useState(1);
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
      if (speechTimer.current) clearTimeout(speechTimer.current);
      utterance.current = null;
      synth.cancel();
      audio.current?.pause();
    };
  }, []);

  async function playFile() {
    if (!audio.current) return;
    if (filePlaying) { audio.current.pause(); setFilePlaying(false); return; }
    try {
      if (speechTimer.current) clearTimeout(speechTimer.current);
      utterance.current = null;
      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
      setSpeechPlaying(false);
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
    const voice = chooseEnglishVoice(voices || []);
    if (!voice || !script || !('speechSynthesis' in window)) return;
    audio.current?.pause();
    setFilePlaying(false);
    if (speechTimer.current) clearTimeout(speechTimer.current);
    const synth = window.speechSynthesis;
    if (synth.speaking || synth.pending) { utterance.current = null; synth.cancel(); setSpeechPlaying(false); return; }
    const spoken = new SpeechSynthesisUtterance(script);
    utterance.current = spoken;
    spoken.lang = 'en-GB';
    spoken.rate = 0.88;
    spoken.voice = voice;
    let started = false;
    const timer = setTimeout(() => {
      if (!started) { synth.cancel(); setSpeechPlaying(false); setSpeechError('Browser speech is unavailable. Read the sample transcript below.'); }
    }, 3500);
    speechTimer.current = timer;
    spoken.onstart = () => { if (utterance.current !== spoken) return; started = true; clearTimeout(timer); setSpeechPlaying(true); };
    spoken.onend = () => { clearTimeout(timer); if (utterance.current !== spoken) return; setSpeechPlaying(false); utterance.current = null; };
    spoken.onerror = () => { clearTimeout(timer); if (utterance.current !== spoken) return; setSpeechPlaying(false); setSpeechError('Browser speech failed. Read the sample transcript below.'); utterance.current = null; };
    try { setSpeechError(''); synth.speak(spoken); }
    catch { clearTimeout(timer); setSpeechError('Browser speech failed. Read the sample transcript below.'); }
  }

  const fallback = chooseListeningSource(source || '', script, Boolean(fileError), voices === null ? null : chooseEnglishVoice(voices) ? 1 : 0);
  return <>
    {source && <div className="audio-player-card">
      <div className="audio-player-icon"><Volume2 size={20}/></div>
      <div className="audio-player-copy"><strong>Listening recording</strong><span>Press Play to start the recording.</span></div>
      <audio ref={audio} preload="none" src={source} onLoadedMetadata={event => setDuration(event.currentTarget.duration)} onTimeUpdate={event => setElapsed(event.currentTarget.currentTime)} onPlay={() => setFilePlaying(true)} onPause={() => setFilePlaying(false)} onEnded={() => setFilePlaying(false)} onError={() => { setFilePlaying(false); setFileError('Recording could not be loaded. Retry or use the fallback below.'); }} />
      <button type="button" className="primary" onClick={() => void playFile()}>{filePlaying ? <Pause size={17}/> : <Play size={17}/>} {filePlaying ? 'Pause' : fileError ? 'Retry recording' : 'Play recording'}</button>
      <div className="listening-playback-status"><span>{audioTime(elapsed)} / {duration > 0 && Number.isFinite(duration) ? audioTime(duration) : '—:—'}</span><span>{filePlaying ? 'Playing' : 'Ready'}</span></div>
      <progress className="listening-audio-progress" value={elapsed} max={Number.isFinite(duration) && duration > 0 ? duration : 1} aria-label="Audio progress"/>
      <label className="listening-volume"><Volume2 size={16}/><span>Volume</span><input type="range" min="0" max="1" step="0.05" value={volume} aria-label="Audio volume" onChange={event => {const value = Number(event.target.value); setVolume(value); if (audio.current) audio.current.volume = value;}}/></label>
    </div>}
    {fileError && <p className="product-alert" role="alert">{fileError}</p>}
    {fallback === 'waiting' && <p role="status" className="product-muted">Checking available browser voices…</p>}
    {fallback === 'speech' && !speechError && <div className="audio-player-card">
      <div className="audio-player-icon"><Volume2 size={20}/></div>
      <div className="audio-player-copy"><strong>Browser voice sample</strong><span>Synthetic practice voice. Upload a recording for a real listening test.</span></div>
      <button type="button" className="primary" onClick={playSpeech}>{speechPlaying ? <Square size={17}/> : <Play size={17}/>} {speechPlaying ? 'Stop sample' : 'Play sample'}</button>
    </div>}
    {fallback === 'speech' && !speechError && <details className="listening-demo-transcript"><summary>Sample transcript · practice only</summary><p lang="en">{script}</p></details>}
    {(fallback === 'transcript' || fallback === 'missing' || (fallback !== 'file' && Boolean(speechError))) && <div className="product-muted listening-fallback" role="status">
      <p>{speechError || (fallback === 'missing' ? 'No recording or transcript is available. Upload audio in the admin panel.' : 'No English browser voice is available. This transcript helps check demo questions; it does not test listening skill.')}</p>
      {speechError && chooseEnglishVoice(voices || []) && <button type="button" className="secondary" onClick={playSpeech}>Retry sample voice</button>}
      {script && <details open><summary>Sample transcript</summary><p lang="en">{script}</p></details>}
    </div>}
  </>;
}
