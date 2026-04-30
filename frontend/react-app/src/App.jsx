import React, {useState} from 'react'
import Upload from './components/Upload'
import GraphView from './components/GraphView'

export default function App(){
  const [tab, setTab] = useState('upload')
  const [graph, setGraph] = useState(null)

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">Contract Lens</div>
        <nav className="nav-links">
          <a href="#features">Features</a>
          <a href="#workflow">Workflow</a>
          <a href="#workspace">Workspace</a>
        </nav>
        <a className="btn small primary" href="#workspace">Open Workspace</a>
      </header>

      <main className="container">
        <div className="content">
          <section className="hero">
            <div className="hero-copy">
              <p className="kicker">Contract intelligence</p>
              <h1>Make clauses legible and connected</h1>
              <p className="sub">Upload a contract or paste text to build a clear clause graph with risk and similarity in seconds.</p>
              <div className="actions">
                <a className="btn primary" href="#workspace">Start analysis</a>
                <a className="btn ghost" href="#features">Explore features</a>
              </div>
              <div className="stat-row">
                <div>
                  <div className="stat-num">4000+</div>
                  <div className="stat-label">Clauses handled</div>
                </div>
                <div>
                  <div className="stat-num">0.9</div>
                  <div className="stat-label">Avg similarity</div>
                </div>
                <div>
                  <div className="stat-num">3x</div>
                  <div className="stat-label">Faster review</div>
                </div>
              </div>
            </div>
            <div className="hero-card">
              <div className="hero-card-header">Live contract snapshot</div>
              <div className="hero-card-body">
                <div className="chip">Definitions</div>
                <div className="line">Confidential information, non public data, and trade secrets.</div>
                <div className="chip">Termination</div>
                <div className="line">Either party may terminate after thirty days notice.</div>
                <div className="meter">
                  <span>Risk</span>
                  <div className="bar"><div style={{width:'64%'}} /></div>
                  <span>Medium</span>
                </div>
              </div>
            </div>
          </section>

          <section className="logos">
            <span>Trusted by legal teams and product counsel</span>
            <div className="logo-row">
              <div className="logo-pill">Northwind</div>
              <div className="logo-pill">Aperture</div>
              <div className="logo-pill">Bluegate</div>
              <div className="logo-pill">Silverline</div>
            </div>
          </section>

          <section id="features" className="section">
            <div className="section-head">
              <h2>Focused features for contract clarity</h2>
              <p>Everything you need to cut through noise and see what matters most.</p>
            </div>
            <div className="grid-3">
              <div className="card">
                <h3>Clause detection</h3>
                <p>Merge headings with bodies and keep clause boundaries consistent across formats.</p>
              </div>
              <div className="card">
                <h3>Similarity graph</h3>
                <p>Reveal relationships between clauses and spot duplication or conflicts fast.</p>
              </div>
              <div className="card">
                <h3>Risk signals</h3>
                <p>Edge scores surface higher risk links and prioritize review paths.</p>
              </div>
            </div>
          </section>

          <section id="workflow" className="section alt">
            <div className="section-head">
              <h2>A clean workflow from raw text to graph</h2>
              <p>Simple steps that keep your team moving.</p>
            </div>
            <div className="grid-3">
              <div className="step">
                <div className="step-num">01</div>
                <h3>Upload or paste</h3>
                <p>CSV, text, or pasted contracts are processed without friction.</p>
              </div>
              <div className="step">
                <div className="step-num">02</div>
                <h3>Build the graph</h3>
                <p>We split clauses, score similarity, and prepare edge risks.</p>
              </div>
              <div className="step">
                <div className="step-num">03</div>
                <h3>Review and act</h3>
                <p>Explore connections and focus on the clauses that matter.</p>
              </div>
            </div>
          </section>

          <section id="workspace" className="section workspace">
            <div className="section-head">
              <h2>Workspace</h2>
              <p>Upload a contract or paste text and see the graph.</p>
            </div>

            <div className="tab-row">
              <button className={tab==='upload' ? 'active' : ''} onClick={()=>setTab('upload')}>Upload</button>
              <button className={tab==='manual' ? 'active' : ''} onClick={()=>setTab('manual')}>Manual</button>
              <button className={tab==='visual' ? 'active' : ''} onClick={()=>setTab('visual')}>Visualize</button>
            </div>

            <section className={`panel ${tab === 'upload' ? 'active' : ''}`}>
              <Upload onGraphData={setGraph} />
            </section>

            <section className={`panel ${tab === 'manual' ? 'active' : ''}`}>
              <section className="card">
                <h2>Manual Input</h2>
                <p>Paste contract text below and click <strong>Build Graph</strong>.</p>
                <ManualInput onGraphData={setGraph} />
              </section>
            </section>

            <section className={`panel ${tab === 'visual' ? 'active' : ''}`}>
              <section className="card">
                <h2>Visualization</h2>
                <GraphView graph={graph} />
              </section>
            </section>
          </section>
        </div>
      </main>

      <footer className="footer">Contract Lens. Built for calm review.</footer>
    </div>
  )
}

function ManualInput({onGraphData}){
  const [text, setText] = useState('')
  const [status, setStatus] = useState(null)

  async function send(){
    setStatus('Building...')
    try{
      const res = await fetch('/build-graph-from-text', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({text})
      })
      if(!res.ok){
        const err = await res.json()
        setStatus(`Error: ${err.detail || res.statusText}`)
        return
      }
      const data = await res.json()
      if(onGraphData){
        onGraphData(data)
      }
      setStatus(`Graph built: ${data.nodes?.length || 0} nodes`)
    }catch(e){
      setStatus('Network error')
    }
  }

  return (
    <div>
      <textarea value={text} onChange={e=>setText(e.target.value)} placeholder="Paste full contract text here" rows={12} />
      <div style={{display:'flex',gap:8,marginTop:8}}>
        <button onClick={send} className="btn primary">Build Graph</button>
        <div style={{alignSelf:'center'}}>{status}</div>
      </div>
    </div>
  )
}
