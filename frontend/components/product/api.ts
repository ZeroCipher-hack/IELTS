export type Language='uz'|'en'|'ru';
export type User={phone:string;city:string;institution:string;learner_type:string;avatar:string;id:number;name:string;email:string;is_staff:boolean;target_band:number;language:Language};
export type Exam={has_access?:boolean;id:number;title:string;section:string;version:number;question_count:number;duration_seconds:number};
export type Row={position:number;prompt:string;answer:string;correct:boolean;accepted_answers:string[];evidence:string;explanation:string;skill_tag:string};
export type Plan={day:number;tag:string;wrong:number;total:number;question_positions:number[];minutes:number;action:string};
export type Assessment={kind:'ai_writing';estimated:boolean;band:number;tasks:{position:number;criteria:Record<string,number>;feedback:string;evidence:string;improvement:string;band:number}[];model:string;note:string};
export type Result={assessment?:Assessment;correct:number;total:number;band:number|null;rows:Row[];skills:Record<string,{correct:number;total:number}>;weekly_plan?:Plan[]};
export type Attempt={assessment_status?:string;id:string;title:string;section:string;state:string;deadline:string;server_time:string;started_at:string;answers:Record<string,string>;review_positions:number[];passage?:string;audio_url?:string;questions?:{position:number;prompt:string;choices:string[];skill_tag:string}[];result:Result|null};
export async function api<T>(path:string,method='GET',data?:unknown):Promise<T>{
 const csrf=document.cookie.split('; ').find(c=>c.startsWith('csrftoken='))?.slice(10)||'';
 const response=await fetch('/api/'+path,{method,credentials:'same-origin',cache:'no-store',signal:AbortSignal.timeout(20000),headers:{'Content-Type':'application/json','X-CSRFToken':decodeURIComponent(csrf)},body:data===undefined?undefined:JSON.stringify(data)});
 const body=await response.json().catch(()=>({error:'Server response unavailable.'}));
 if(!response.ok)throw new Error(body.error||`HTTP ${response.status}`);
 return body as T;
}
