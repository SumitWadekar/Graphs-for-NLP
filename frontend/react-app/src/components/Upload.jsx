import React, {useState, useRef} from 'react'

export default function Upload({onGraphData}){
  const [fileName, setFileName] = useState(null)
  const [previewLines, setPreviewLines] = useState([])
  const [message, setMessage] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef()

  function handleFile(file){
    setFileName(file.name)
    const reader = new FileReader()
    reader.onload = ()=>{
      const text = reader.result
      const lines = text.split(/\r?\n/).slice(0,20)
      setPreviewLines(lines)
    }
    reader.readAsText(file)
  }

  async function uploadFile(file){
    setMessage('Uploading...')
    const form = new FormData()
    form.append('file', file)
    try{
      const res = await fetch('/upload-contract-csv', {method:'POST', body: form})
      const data = await res.json()
      if(!res.ok){
        setMessage(`Error: ${data.detail || res.statusText}`)
        return
      }
      if(onGraphData){
        onGraphData(data.graph || data)
      }
      setMessage(`Processed ${data.total_clauses || (data.graph?.nodes?.length||0)} clauses`)
    }catch(e){
      setMessage('Network error')
    }
  }

  function onChange(e){
    const file = e.target.files[0]
    if(!file) return
    handleFile(file)
    uploadFile(file)
  }

  function onDrop(e){
    e.preventDefault()
    setDragActive(false)
    const file = e.dataTransfer.files[0]
    if(!file) return
    inputRef.current.files = e.dataTransfer.files
    handleFile(file)
    uploadFile(file)
  }

  return (
    <section className="card">
      <h2>Upload Contract File</h2>
      <div
        className={`uploader ${dragActive ? 'active' : ''}`}
        onDragOver={e=>e.preventDefault()}
        onDragEnter={()=>setDragActive(true)}
        onDragLeave={()=>setDragActive(false)}
        onDrop={onDrop}
      >
        <div className="upload-inner">
          <div className="cloud">Upload</div>
          <div className="hint">Drag a file here, or use the button below.</div>
          <label className="file-btn">
            Browse files
            <input ref={inputRef} type="file" accept=".csv,.txt" onChange={onChange} />
          </label>
          <div className="file-note">Accepts .csv or .txt</div>
        </div>
      </div>

      {fileName && (
        <div className="preview">
          <strong>{fileName}</strong>
          <div className="preview-list">
            {previewLines.map((l,i)=>(<div key={i} className="line">{l}</div>))}
          </div>
        </div>
      )}

      {message && <div className="msg">{message}</div>}
    </section>
  )
}
