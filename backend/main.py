from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import networkx as nx
from typing import List

from schemas.contracts import (
    Clause, 
    BuildGraphResponse, 
    NodeOut, 
    EdgeOut
)
from document_graph import build_document_graph
from dynamic_graph_builder import build_dynamic_graph

app = FastAPI(
    title="Contract Analysis API",
    description="API for analyzing legal contracts with NLP and graph analysis",
    version="1.0.0"
)

# Add CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Contract Analysis API"}


@app.post("/build-graph-from-clauses")
async def build_graph_from_clauses(clauses: List[str], similarity_threshold: float = 0.75):
    """
    Build a graph from a list of clause texts
    
    Args:
        clauses: List of clause text strings
        similarity_threshold: Minimum similarity score to create an edge (0-1)
    """
    try:
        if not clauses:
            raise HTTPException(status_code=400, detail="Clauses list cannot be empty")
        
        if similarity_threshold < 0 or similarity_threshold > 1:
            raise HTTPException(status_code=400, detail="similarity_threshold must be between 0 and 1")
        
        # Create Clause objects
        clause_objects = [
            Clause(index=i, label=f"Clause {i+1}", text=text)
            for i, text in enumerate(clauses)
        ]
        
        # Build graph
        graph, edges, vectors = build_document_graph(clause_objects, similarity_threshold)
        
        # Convert to response format
        nodes = [
            NodeOut(id=node, text=clause_objects[node].text)
            for node in graph.nodes()
        ]
        
        edges_out = [
            EdgeOut(
                source=edge[0],
                target=edge[1],
                risk=graph[edge[0]][edge[1]].get('similarity', 0.0),
                difference=None,
                base_nodes=None
            )
            for edge in graph.edges()
        ]
        
        return BuildGraphResponse(nodes=nodes, edges=edges_out)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building graph: {str(e)}")


@app.post("/build-graph-from-text")
async def build_graph_from_text(text: str = Body(...)):
    """
    Build a graph from raw contract text by splitting into clauses
    
    Args:
        text: Raw contract text
    """
    try:
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Build dynamic graph from text
        G = build_dynamic_graph(text)
        
        # Convert to response format
        nodes = [
            NodeOut(id=int(node), text=G.nodes[node].get('text', str(node)))
            for node in G.nodes()
        ]
        
        edges_out = [
            EdgeOut(
                source=int(edge[0]),
                target=int(edge[1]),
                risk=G[edge[0]][edge[1]].get('weight', 0.5),
                difference=G[edge[0]][edge[1]].get('difference', None),
                base_nodes=G[edge[0]][edge[1]].get('base_nodes', None)
            )
            for edge in G.edges()
        ]
        
        return BuildGraphResponse(nodes=nodes, edges=edges_out)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building graph: {str(e)}")


@app.post("/upload-contract-csv")
async def upload_contract_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file containing contract clauses

    Supported formats:
    - CSV with a header column named `clause_text` (preferred)
    - CSV without headers where each row is a clause (single column or multiple columns joined)
    - Plain text file where each line is a clause (fallback)
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        content = await file.read()

        clauses = []
        # Try reading as CSV with header first
        try:
            df = pd.read_csv(io.BytesIO(content))
            if 'clause_text' in df.columns:
                clauses = df['clause_text'].astype(str).tolist()
            else:
                # Fallback: read without header and join all columns into a single clause string per row
                df_no_header = pd.read_csv(io.BytesIO(content), header=None)
                clauses = df_no_header.fillna('').astype(str).agg(' '.join, axis=1).tolist()
                clauses = [c.strip() for c in clauses if len(c.strip()) > 0]
        except Exception:
            # Final fallback: treat file as plain text and split by lines
            try:
                text = content.decode('utf-8', errors='ignore')
                clauses = [line.strip() for line in text.splitlines() if len(line.strip()) > 0]
            except Exception:
                clauses = []

        if not clauses:
            raise HTTPException(
                status_code=400,
                detail=("No clauses found in file. Provide a CSV with a 'clause_text' column, "
                        "a CSV where each row is a clause, or a plain text file with one clause per line.")
            )
        
        if len(clauses) > 100:
            raise HTTPException(status_code=400, detail="Too many clauses (max 100). Please split the document.")
        
        # Build graph
        clause_objects = [
            Clause(index=i, label=f"Clause {i+1}", text=text)
            for i, text in enumerate(clauses)
        ]
        
        graph, edges, vectors = build_document_graph(clause_objects)
        
        # Convert to response format
        nodes = [
            NodeOut(id=node, text=clause_objects[node].text)
            for node in graph.nodes()
        ]
        
        edges_out = [
            EdgeOut(
                source=edge[0],
                target=edge[1],
                risk=graph[edge[0]][edge[1]].get('similarity', 0.0),
                difference=None,
                base_nodes=None
            )
            for edge in graph.edges()
        ]
        
        return {
            "filename": file.filename,
            "total_clauses": len(clauses),
            "graph": BuildGraphResponse(nodes=nodes, edges=edges_out)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")


@app.get("/api-info")
def get_api_info():
    """Get information about available API endpoints"""
    return {
        "endpoints": [
            {
                "path": "/health",
                "method": "GET",
                "description": "Health check"
            },
            {
                "path": "/build-graph-from-clauses",
                "method": "POST",
                "description": "Build graph from list of clauses"
            },
            {
                "path": "/build-graph-from-text",
                "method": "POST",
                "description": "Build graph from raw contract text"
            },
            {
                "path": "/upload-contract-csv",
                "method": "POST",
                "description": "Upload CSV file with clauses"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
