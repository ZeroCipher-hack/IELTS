"use client";

import Image from 'next/image';
import { useEffect, useRef, useState, type CSSProperties } from 'react';
import { ArrowUpRight, ArrowRight, AudioLines, Headphones, BookOpen, PenLine, Mic, CalendarCheck, Target, Pause, Play } from 'lucide-react';
import { copy } from './refresh-copy';
import s from './landing.module.css';

const skills = [
  { name: 'Listening', score: 7, Icon: Headphones },
  { name: 'Reading', score: 6.5, Icon: BookOpen },
  { name: 'Writing', score: 6, Icon: PenLine },
  { name: 'Speaking', score: 6.5, Icon: Mic },
];
const languages = ['uz', 'en', 'ru'] as const;

export default function Landing() {
  const [lang, setLang] = useState<(typeof languages)[number]>('uz');
  const [paused, setPaused] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const c = copy[lang];

  useEffect(() => {
    if (!window.IntersectionObserver || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add(s.visible);
        observer.unobserve(entry.target);
      }
    }), { threshold: 0.08 });
    root.current?.querySelectorAll('[data-reveal]').forEach(element => {
      element.classList.add(s.waiting);
      observer.observe(element);
    });
    return () => observer.disconnect();
  }, []);

  return <div ref={root} lang={lang} className={`landing-page ${s.page}`}>
    <a className={s.skip} href="#content">{c.skip}</a>
    <header className={s.header}>
      <a className={s.logo} href="#top" aria-label="IELTSQA"><AudioLines aria-hidden="true"/>IELTS<span>QA</span></a>
      <nav aria-label={c.nav[0]}><a href="#skills">{c.nav[0]}</a><a href="#how-it-works">{c.nav[1]}</a><a href="/app">{c.nav[2]}</a></nav>
      <div className={s.headerActions}><div className={s.languages} role="group" aria-label="Language">{languages.map(l => <button key={l} type="button" aria-pressed={l === lang} onClick={() => setLang(l)}>{l.toUpperCase()}</button>)}</div><a className={s.login} href="/login">{c.nav[3]}</a></div>
    </header>
    <main id="content">
      <section id="top" className={s.hero}>
        <div><p className={s.eyebrow}>{c.eyebrow}</p><h1>{c.title}<span>{c.accent}</span></h1><p className={s.intro}>{c.intro}</p><div className={s.actions}><a className={s.cta} href="/app">{c.cta}<ArrowUpRight aria-hidden="true"/></a><a className={s.textLink} href="#sample-result">{c.sampleLink}</a></div><p className={s.note}>{c.note}</p></div>
        <div id="sample-result" className={s.report} tabIndex={-1}>
          <div className={s.reportHeader}><div><h2>{c.sample}</h2><p>{c.sampleNote}</p></div><AudioLines aria-hidden="true"/></div>
          <div className={s.scoreGrid}><div className={s.ring}><div><strong>6.5</strong><span>Overall band</span></div></div><ul className={s.scores}>{skills.map(({ name, score, Icon }) => <li key={name}><Icon aria-hidden="true"/><span>{name}</span><div className={s.track} aria-hidden="true"><i style={{width:`${score / 9 * 100}%`}}/></div><b>{score.toFixed(1)}</b></li>)}</ul></div>
          <div className={s.weakness}><Target aria-hidden="true"/><div><h3>{c.improve}</h3><ul>{c.weaknesses.map(w => <li key={w}>{w}</li>)}</ul></div></div>
          <div className={s.plan}><CalendarCheck aria-hidden="true"/><b>{c.plan}</b><span>{c.planText}</span></div>
        </div>
      </section>
      <section id="skills" className={s.section} data-reveal><h2>{c.modules}</h2><div className={s.skills}>{skills.map(({name, Icon}, i) => <a href="/app" key={name} className={s.skill}><Icon aria-hidden="true"/><div><h3>{name}</h3><p>{c.descriptions[i]}</p></div><ArrowRight aria-hidden="true"/></a>)}</div><p className={s.note}>{c.availability}</p></section>
      <section className={s.speaking} data-reveal>
        <div className={s.conversation} data-paused={paused}>
          <div className={s.previewHeader}><span>{c.preview}</span><span>PART 1</span></div>
          <div className={s.avatar}><Image src="/examiner-landing-v3.webp" alt="Nova — IELTSQA AI speaking examiner" fill sizes="(max-width: 760px) 90vw, 44vw"/></div>
          <div className={s.waveRow}><Mic aria-hidden="true"/><div className={s.wave} aria-hidden="true">{Array.from({length:32}, (_, i) => <i key={i} style={{'--height':`${8 + ((i * 17) % 32)}px`, '--delay':`${i * -0.13}s`} as CSSProperties}/>)}</div><button type="button" onClick={() => setPaused(p => !p)} aria-label={paused ? c.play : c.pause}>{paused ? <Play aria-hidden="true"/> : <Pause aria-hidden="true"/>}</button></div>
          <p className={s.transcript} lang="en"><b>NOVA</b>What do you enjoy about where you live?</p><p className={s.note}>{c.previewNote}</p>
        </div>
        <div><p className={s.eyebrow}>SPEAKING</p><h2>{c.speaking}</h2><p className={s.intro}>{c.speakingText}</p><a className={s.textLink} href="/app">{c.speakingCta}<ArrowRight aria-hidden="true"/></a></div>
      </section>
      <section id="how-it-works" className={s.section} data-reveal><p className={s.eyebrow}>IELTSQA / 01 — 03</p><h2>{c.how}</h2><ol className={s.steps}>{c.steps.map(([title,text], i) => <li key={title}><span>0{i+1}</span><h3>{title}</h3><p>{text}</p></li>)}</ol></section>
      <section className={s.feedback} data-reveal><div><p className={s.eyebrow}>{c.evidence}</p><h2>{c.detail}</h2><p className={s.intro}>{c.detailText}</p></div><div className={s.example}><span>{c.original}</span><blockquote lang="en">“There are many things near my house.”</blockquote><span>{c.better}</span><blockquote lang="en">“There’s a library and a small park within walking distance of my house.”</blockquote><p>{c.explanation}</p></div></section>
      <section className={s.status} data-reveal><h2>{c.status}</h2><p>{c.statusText}</p></section>
      <section className={s.finalCta} data-reveal><h2>{c.end}</h2><p>{c.endText}</p><a className={s.cta} href="/register">{c.register}<ArrowUpRight aria-hidden="true"/></a></section>
    </main>
    <footer className={s.footer}><div><a className={s.logo} href="#top"><AudioLines aria-hidden="true"/>IELTS<span>QA</span></a><p>{c.footer}</p></div><p>{c.disclaimer}</p><a className={s.textLink} href="/login">{c.nav[3]}<ArrowUpRight aria-hidden="true"/></a></footer>
  </div>;
}
