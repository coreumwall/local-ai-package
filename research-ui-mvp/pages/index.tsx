import { useState } from 'react';
import Graph3D from '../components/Graph3D';

export default function Home() {
  const [tab, setTab] = useState<'graph'|'search'|'reader'|'pipelines'>('graph');

  return (
    <div style={{display:'grid', gridTemplateColumns:'240px 1fr', height:'100vh'}}>
      <aside style={{borderRight:'1px solid #333', padding:'12px'}}>
        <h3>Tools</h3>
        <button onClick={async()=>{
          await fetch('/api/n8n/crawl', {method:'POST', body: JSON.stringify({ q:'test' }), headers:{'Content-Type':'application/json'}});
          alert('Triggered crawl');
        }}>Crawl</button>
        <button onClick={()=>setTab('graph')}>Graph</button>
        <button onClick={()=>setTab('search')}>Search</button>
        <button onClick={()=>setTab('reader')}>Reader</button>
        <button onClick={()=>setTab('pipelines')}>Pipelines</button>
      </aside>
      <main style={{padding:'12px'}}>
        <header style={{display:'flex', gap:12, alignItems:'center'}}>
          <strong>Research UI MVP</strong>
          <select>
            <option>o3</option>
            <option>o1-pro</option>
            <option>o3-mini</option>
            <option>Deep Research</option>
          </select>
        </header>
        <section style={{marginTop:12, height:'calc(100% - 40px)'}}>
          {tab==='graph' && <Graph3D />}
          {tab==='search' && <SearchTab />}
          {tab==='reader' && <ReaderTab />}
          {tab==='pipelines' && <PipelinesTab />}
        </section>
      </main>
    </div>
  );
}

function SearchTab(){
  const [q,setQ]=useState('laser optics');
  const [results,setResults]=useState<any>(null);
  return (
    <div>
      <h3>Private Search (SearXNG)</h3>
      <input value={q} onChange={e=>setQ(e.target.value)} />
      <button onClick={async()=>{
        const r = await fetch(`/api/searx?q=${encodeURIComponent(q)}`);
        setResults(await r.json());
      }}>Search</button>
      <pre style={{maxHeight:400, overflow:'auto'}}>{results?JSON.stringify(results,null,2):'No results yet'}</pre>
    </div>
  );
}

function ReaderTab(){
  return <div>Reader placeholder. Wire to Supabase doc/chunk tables.</div>;
}

function PipelinesTab(){
  return <div>n8n pipelines status placeholder.</div>;
}
