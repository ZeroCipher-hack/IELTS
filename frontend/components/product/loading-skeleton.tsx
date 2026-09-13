export default function LoadingSkeleton({label,view='dashboard'}:{label:string;view?:string}){
 return <section aria-busy="true" aria-label={label}><p className="loading-status" role="status">{label}</p><div className={'skeleton-grid '+view} aria-hidden="true">{Array.from({length:view==='results'?4:view==='tests'?4:3},(_,i)=><div className="panel skeleton-card" key={i}><div className="skeleton-line short"/><div className="skeleton-line large"/><div className="skeleton-line"/></div>)}</div></section>
}
