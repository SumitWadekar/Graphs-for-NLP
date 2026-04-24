# Contract Analysis System

A comprehensive system for analyzing legal contracts using NLP and graph-based analysis. This project provides both a FastAPI backend and a Streamlit frontend for interactive contract analysis.

## 🎯 Features

- **Graph-Based Analysis**: Build similarity graphs from contract clauses
- **Multiple Input Methods**: Upload CSV, paste text, or input clauses manually
- **Interactive Visualization**: Visualize clause relationships with Plotly
- **RESTful API**: Complete API for programmatic access
- **Legal NLP**: Uses InLegalBERT for contract-specific embeddings

## 📁 Project Structure

```
Graphs-for-NLP/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── base_graph_builder.py   # Base graph building logic
│   ├── document_graph.py       # Document-level graph analysis
│   ├── dynamic_graph_builder.py # Dynamic graph construction
│   ├── user_graph_builder.py   # User-specific graphs
│   ├── schemas/
│   │   └── contracts.py        # Pydantic models
│   ├── services/
│   │   └── model_singleton.py  # Embedding service
│   └── requirements.txt
├── frontend/
│   ├── app.py                  # Streamlit application
│   └── requirements.txt
├── data/
│   ├── base_contract_clauses.csv
│   ├── embeddings.npy
│   └── legal_graph.pkl
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda

### Backend Setup

1. **Install backend dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Run the API server**:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

**API Documentation**: Visit `http://localhost:8000/docs` for interactive Swagger UI

### Frontend Setup

1. **Install frontend dependencies** (in a new terminal):
```bash
cd frontend
pip install -r requirements.txt
```

2. **Run the Streamlit app**:
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📡 API Endpoints

### Health Check
```bash
GET /health
```
Returns API status

### Build Graph from Clauses
```bash
POST /build-graph-from-clauses
Content-Type: application/json

{
    "clauses": ["Clause 1 text", "Clause 2 text"],
    "similarity_threshold": 0.75
}
```

### Build Graph from Raw Text
```bash
POST /build-graph-from-text
Content-Type: application/json

{
    "text": "Raw contract text here..."
}
```

### Upload Contract CSV
```bash
POST /upload-contract-csv
Content-Type: multipart/form-data

file: <your_file.csv>
```

Expected CSV columns:
- `clause_text` (required) - The text of each clause
- `clause_type` (optional) - Type of clause
- `risk_level` (optional) - Risk classification

### API Information
```bash
GET /api-info
```
Returns list of all available endpoints

## 🖥️ Streamlit Frontend Features

### 📤 Upload Tab
- Upload CSV files with contract clauses
- Automatic CSV parsing and validation

### ✏️ Manual Input Tab
- Paste multiple clauses (separated by blank lines)
- Paste raw contract text (auto-split into clauses)
- Configure similarity threshold

### 📊 Visualization Tab
- Interactive graph visualization
- Contract statistics
- Similarity matrix table
- Detailed clause view

## 🔧 Configuration

### Similarity Threshold
Controls the minimum similarity score (0-1) required to create edges in the graph:
- **0.75** (default): More selective, shows only strong relationships
- **0.50**: Medium sensitivity
- **0.25**: Shows more relationships

### API Server URL
Configure the API endpoint in the Streamlit sidebar (default: `http://localhost:8000`)

## 📊 Graph Components

### Nodes
- Each clause in the contract becomes a node
- Node properties:
  - `id`: Unique clause index
  - `text`: Full clause text
  - `label`: Human-readable label

### Edges
- Created when similarity between clauses exceeds threshold
- Edge properties:
  - `source`: Source clause index
  - `target`: Target clause index
  - `similarity`: Cosine similarity score (0-1)

## 🔌 Integration Examples

### Python Client
```python
import requests

# Build graph from clauses
response = requests.post(
    "http://localhost:8000/build-graph-from-clauses",
    json={
        "clauses": ["Clause 1", "Clause 2"],
        "similarity_threshold": 0.75
    }
)

graph = response.json()
print(f"Nodes: {len(graph['nodes'])}")
print(f"Edges: {len(graph['edges'])}")
```

### JavaScript/TypeScript
```javascript
const response = await fetch(
  'http://localhost:8000/build-graph-from-clauses',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      clauses: ['Clause 1', 'Clause 2'],
      similarity_threshold: 0.75
    })
  }
);

const graph = await response.json();
```

## 📝 Data Models

### Clause
```python
{
    "index": int,          # Unique clause ID
    "label": str,          # Human-readable label
    "text": str           # Clause content
}
```

### Graph Response
```python
{
    "nodes": [
        {"id": int, "text": str}
    ],
    "edges": [
        {
            "source": int,
            "target": int,
            "risk": float,          # similarity score
            "difference": float | null,
            "base_nodes": dict | null
        }
    ]
}
```

## 🔄 Workflow

1. **Input Contract**: Upload CSV or paste contract text
2. **Build Graph**: System splits into clauses and computes embeddings
3. **Create Edges**: Clauses with similarity > threshold are connected
4. **Visualize**: Interactive graph shows relationships
5. **Analyze**: Review similarity matrix and clause details

## 🛠️ Development

### Running Both Services Together

**Terminal 1 - Backend**:
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend**:
```bash
cd frontend
streamlit run app.py
```

### Testing the API

Use the Swagger UI at `http://localhost:8000/docs` or test with curl:

```bash
curl -X POST "http://localhost:8000/build-graph-from-clauses" \
  -H "Content-Type: application/json" \
  -d '{
    "clauses": ["This is clause 1", "This is clause 2"],
    "similarity_threshold": 0.75
  }'
```

## 📦 Key Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Streamlit**: Rapid data app development
- **Sentence-Transformers**: InLegalBERT for legal embeddings
- **NetworkX**: Graph analysis and visualization
- **Plotly**: Interactive visualizations
- **Scikit-learn**: ML utilities

## 🐛 Troubleshooting

### API Connection Error
- Ensure backend is running on port 8000
- Check API URL in Streamlit sidebar
- Use "Test Connection" button

### CSV Upload Issues
- Verify CSV has `clause_text` column
- Check file encoding (UTF-8 recommended)
- Ensure clauses are not empty

### Slow Graph Building
- Reduce number of clauses
- Increase similarity threshold
- Check available system memory

## 📄 License

This project is part of the NLP Project suite.

## 🤝 Contributing

Feel free to extend with:
- Additional analysis features
- Different embedding models
- Custom graph algorithms
- Export functionality (PDF, JSON)

## 📧 Support

For issues or questions, check the logs from both frontend and backend for detailed error messages.
