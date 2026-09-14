'use client';
import {useId,type RefObject} from 'react';
/** A vector character, animated from playback amplitude rather than phonemes. */
export default function ExaminerAvatar({faceRef,speaking,listening,label}:{faceRef:RefObject<HTMLDivElement|null>;speaking:boolean;listening:boolean;label:string}){
 const id=useId().replace(/:/g,'');
 return <div ref={faceRef} className={'examiner-character '+(speaking?'is-speaking':listening?'is-listening':'')}>
  <div className="character-orbit" aria-hidden="true"/>
  <svg viewBox="0 0 480 460" role="img" aria-label={label}>
   <defs>
    <linearGradient id={id+'hair'} x2="1" y2="1"><stop stopColor="#344664"/><stop offset="1" stopColor="#111d32"/></linearGradient>
    <linearGradient id={id+'skin'} x2="1" y2="1"><stop stopColor="#fff3e9"/><stop offset="1" stopColor="#dfb6a4"/></linearGradient>
    <linearGradient id={id+'coat'} x2="1" y2="1"><stop stopColor="#53798b"/><stop offset="1" stopColor="#223d59"/></linearGradient>
   </defs>
   <ellipse cx="240" cy="438" rx="151" ry="15" fill="#091522" opacity=".25"/>
   <path d="M137 265V153C137 32 338 30 341 156L350 298 309 329 149 310Z" fill={'url(#'+id+'hair)'}/>
   <path d="M201 268H279V339H201Z" fill={'url(#'+id+'skin)'}/>
   <path d="M87 446 104 359Q115 324 196 308L240 337 284 308Q365 324 376 359L393 446Z" fill={'url(#'+id+'coat)'}/>
   <path d="M201 312 240 336 279 312 269 446H210Z" fill="#f1f7f6"/>
   <path d="M188 313 220 343 199 365 221 389 210 446 158 333Z" fill="#7193a0"/>
   <path d="M292 313 260 343 281 365 259 389 270 446 322 333Z" fill="#7193a0"/>
   <rect x="304" y="370" width="37" height="20" rx="5" fill="#102e43"/><circle cx="314" cy="380" r="3" fill="#6ff0d4"/><path d="M322 377h11m-11 6h8" stroke="#b4d6db" strokeWidth="2"/>
   <ellipse cx="153" cy="201" rx="13" ry="24" fill="#dfb6a4"/><ellipse cx="327" cy="201" rx="13" ry="24" fill="#dfb6a4"/>
   <path d="M153 147Q152 103 240 100Q327 103 327 147V223Q324 285 240 310Q156 285 153 223Z" fill={'url(#'+id+'skin)'}/>
   <path d="M142 177Q135 64 239 68Q337 65 337 164L325 199 308 139Q231 157 207 110Q188 157 153 172L151 214Z" fill={'url(#'+id+'hair)'}/>
   <path d="M170 108Q210 76 258 89" fill="none" stroke="#65718b" strokeWidth="5" strokeLinecap="round" opacity=".5"/>
   <path d="M177 185Q195 173 215 183M265 183Q285 173 303 185" fill="none" stroke="#4c3b3c" strokeWidth="5" strokeLinecap="round"/>
   <g className="character-eyes"><ellipse cx="198" cy="204" rx="17" ry="10" fill="#fffaf5"/><ellipse cx="282" cy="204" rx="17" ry="10" fill="#fffaf5"/><circle cx="200" cy="204" r="8" fill="#32767c"/><circle cx="280" cy="204" r="8" fill="#32767c"/><circle cx="200" cy="205" r="4" fill="#1c2836"/><circle cx="280" cy="205" r="4" fill="#1c2836"/><circle cx="203" cy="201" r="2" fill="white"/><circle cx="283" cy="201" r="2" fill="white"/></g>
   <path d="M239 209 233 234Q240 240 248 234" fill="none" stroke="#bd9283" strokeWidth="3" strokeLinecap="round"/>
   <ellipse cx="180" cy="234" rx="17" ry="7" fill="#d99492" opacity=".3"/><ellipse cx="300" cy="234" rx="17" ry="7" fill="#d99492" opacity=".3"/>
   <g className="character-mouth"><ellipse cx="240" cy="263" rx="20" ry="3" fill="#763d49"/><path d="M224 261Q240 257 256 261" fill="none" stroke="#c77a83" strokeWidth="3" strokeLinecap="round"/></g>
   <path d="M331 184v43q0 23-42 23" fill="none" stroke="#6bcac7" strokeWidth="5" strokeLinecap="round"/><rect x="277" y="245" width="18" height="10" rx="5" fill="#1d5263"/>
   <rect x="323" y="188" width="15" height="29" rx="7" fill="#b7e8df"/><circle cx="330" cy="198" r="3" fill="#188a92"/>
  </svg>
  <span className="character-name">NOVA <span>AI EXAMINER</span></span>
 </div>
}
