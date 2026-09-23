'use client';
import { type RefObject } from 'react';
/** Audio-reactive voice orb, replacing a static character face. Driven by playback
 * amplitude written directly to --speech on faceRef (see voice-pilot.tsx), so this
 * component stays a pure CSS consumer — no per-frame React re-renders. */
export default function ExaminerAvatar({faceRef,speaking,listening,label}:{faceRef:RefObject<HTMLDivElement|null>;speaking:boolean;listening:boolean;label:string}){
 return <div ref={faceRef} className={'examiner-character '+(speaking?'is-speaking':listening?'is-listening':'')} role="img" aria-label={label}>
  <div className="character-orbit" aria-hidden="true"/>
  <div className="voice-orb" aria-hidden="true">
   <span className="voice-orb-ring voice-orb-ring-1"/>
   <span className="voice-orb-ring voice-orb-ring-2"/>
   <span className="voice-orb-core">
    <span className="voice-orb-bar"/><span className="voice-orb-bar"/><span className="voice-orb-bar"/><span className="voice-orb-bar"/><span className="voice-orb-bar"/>
   </span>
  </div>
  <span className="character-name">NOVA <span>AI EXAMINER</span></span>
 </div>
}
