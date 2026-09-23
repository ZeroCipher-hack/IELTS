'use client';
import {useEffect,useState} from 'react';
import {Moon,Sun} from 'lucide-react';
import type {Language} from './api';
export default function ThemeToggle({language}:{language:Language}){
 const [dark,setDark]=useState(false);
 // Mountda tashqi tema (document + OS) bilan sinxronlash — intentional
 useEffect(()=>{
  setDark(document.documentElement.dataset.theme==='dark');

 },[]);
 const label=dark?{uz:'Yorug‘ rejim',en:'Light mode',ru:'Светлая тема'}[language]:{uz:'Tungi rejim',en:'Dark mode',ru:'Тёмная тема'}[language];
 return <button type="button" className="theme-toggle" aria-label={label} title={label} onClick={()=>{const next=!dark;setDark(next);document.documentElement.dataset.theme=next?'dark':'light';try{localStorage.setItem('ieltsqa-theme-v2',next?'dark':'light')}catch{}}}>{dark?<Sun size={20}/>:<Moon size={20}/>}</button>
}
