import React, {useMemo, useState, useRef, useEffect} from 'react'
import ForceGraph2D from 'react-force-graph-2d'

export default function GraphView({graph}){
  const [hoverNode, setHoverNode] = useState(null)
  const [hoverLink, setHoverLink] = useState(null)
  const [showList, setShowList] = useState(false)
  const graphRef = useRef(null)

  const data = useMemo(()=>{
    if(!graph || !graph.nodes || !graph.edges){
      return {nodes: [], links: []}
    }
    const nodes = graph.nodes.map(n => ({
      id: n.id,
      name: n.text
    }))
    const links = graph.edges.map(e => ({
      source: e.source,
      target: e.target,
      value: e.risk ?? 1
    }))
    console.log('Graph data:', {nodes, links}) // Debug log
    return {nodes, links}
  }, [graph])

  useEffect(()=>{
    if(graphRef.current && data.nodes.length){
      graphRef.current.zoomToFit(600, 40)
    }
  }, [data])

  if(!graph || !graph.nodes || graph.nodes.length === 0){
    return (
      <div className="graph-empty">
        <h3>No graph yet</h3>
        <p>Upload a file or build from text to see the graph here.</p>
      </div>
    )
  }

  return (
    <div className="graph-wrap">
      <div className="graph-panel">
        <div className="graph-header">
          <div>
            <div className="graph-title">Clause Graph</div>
            <div className="graph-sub">Hover nodes or edges to see clause text and similarity.</div>
          </div>
          <div className="graph-stats">
            <span>Nodes: {data.nodes.length}</span>
            <span>Edges: {data.links.length}</span>
          </div>
        </div>

        <ForceGraph2D
          key={`${data.nodes.length}-${data.links.length}`}
          ref={graphRef}
          graphData={data}
          nodeId="id"
          linkWidth={link => {
            const value = Number(link.value || 0)
            if(value >= 1.5) return 3.8
            if(value >= 0.7) return 2.4
            return 1.1
          }}
          linkColor={link => {
            const value = Number(link.value || 0)
            if(value >= 1.5) return 'rgba(192,132,252,0.95)'
            if(value >= 0.7) return 'rgba(168,85,247,0.85)'
            return 'rgba(139,92,246,0.45)'
          }}
          nodeColor={() => 'rgba(251,191,36,0.9)'}
          nodeRelSize={6}
          onNodeHover={node => setHoverNode(node)}
          onLinkHover={link => setHoverLink(link)}
          onEngineStop={() => graphRef.current && graphRef.current.zoomToFit(600, 40)}
          nodeCanvasObject={(node, ctx, globalScale) => {
            if(hoverNode && node.id === hoverNode.id){
              const label = `Clause ${node.id}`
              const fontSize = 12 / globalScale
              ctx.font = `${fontSize}px Manrope`
              ctx.fillStyle = 'rgba(230,237,247,0.9)'
              ctx.fillText(label, node.x + 6, node.y + 6)
            }
          }}
          nodeLabel={node => node.name}
          width={920}
          height={520}
          backgroundColor="#0a1020"
          d3Force="charge"
          d3ForceStrength={-200}
        />

        <div className="graph-info">
          {hoverNode ? (
            <div>
              <div className="info-title">Clause {hoverNode.id}</div>
              <div className="info-text">{hoverNode.name}</div>
            </div>
          ) : (
            <div className="info-muted">Hover a node to see the clause text.</div>
          )}

          {hoverLink ? (
            <div>
              <div className="info-title">Similarity</div>
              <div className="info-text">{Number(hoverLink.value || 0).toFixed(3)}</div>
            </div>
          ) : (
            <div className="info-muted">Hover an edge to see similarity.</div>
          )}
        </div>
      </div>
      <div className="graph-legend">
        <span className="dot node" /> Clause
        <span className="dot link" /> Similarity edge
      </div>
      <button onClick={() => setShowList(!showList)} className="toggle-list-btn">
        {showList ? 'Hide' : 'Show'} List
      </button>
      {showList && (
        <div className="graph-list">
          <h3>Nodes</h3>
          <ul>
            {graph.nodes.map(node => (
              <li key={node.id}>
                <strong>Clause {node.id}:</strong> {node.text}
              </li>
            ))}
          </ul>
          <h3>Edges</h3>
          <ul>
            {graph.edges.map((edge, idx) => (
              <li key={idx}>
                Clause {edge.source} → Clause {edge.target}: Similarity {(edge.risk || 0).toFixed(2)} {(edge.risk || 0) <= 0.1 ? '(sequential)' : ''}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
