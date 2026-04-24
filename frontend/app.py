import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import io
from typing import List, Dict, Any

# Page configuration
st.set_page_config(
    page_title="Contract Analysis System",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if 'graph_data' not in st.session_state:
    st.session_state.graph_data = None
if 'clauses' not in st.session_state:
    st.session_state.clauses = []

# Header
st.title("⚖️ Contract Analysis System")
st.markdown("Analyze legal contracts with NLP and graph-based insights")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_url = st.text_input(
        "API Server URL",
        value=st.session_state.api_url,
        help="URL of the backend API server"
    )
    st.session_state.api_url = api_url
    
    # Test connection
    if st.button("🔗 Test Connection", use_container_width=True):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Connected to API")
            else:
                st.error(f"❌ API returned status {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")
    
    st.divider()
    
    # Similarity threshold
    similarity_threshold = st.slider(
        "Similarity Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
        step=0.05,
        help="Minimum similarity to create graph edges"
    )
    
    st.divider()
    
    # API Info
    with st.expander("📡 API Endpoints", expanded=False):
        try:
            response = requests.get(f"{api_url}/api-info", timeout=5)
            if response.status_code == 200:
                api_info = response.json()
                for endpoint in api_info.get('endpoints', []):
                    st.write(f"**{endpoint['path']}** ({endpoint['method']})")
                    st.write(f"_{endpoint['description']}_")
                    st.write("---")
        except Exception as e:
            st.warning(f"Could not fetch API info: {str(e)}")


# Main content tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload", "✏️ Manual Input", "📊 Visualization"])

with tab1:
    st.header("Upload Contract File")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload CSV File")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="CSV should contain a 'clause_text' column"
        )
        
        if uploaded_file is not None:
            with st.spinner("Processing CSV..."):
                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getbuffer(), 'text/csv')}
                    response = requests.post(
                        f"{st.session_state.api_url}/upload-contract-csv",
                        files=files,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.graph_data = result['graph']
                        
                        # Extract clauses for display
                        st.session_state.clauses = [node['text'] for node in result['graph']['nodes']]
                        
                        st.success(f"✅ Processed {result['total_clauses']} clauses")
                        st.info(f"Graph: {len(result['graph']['nodes'])} nodes, {len(result['graph']['edges'])} edges")
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Failed to process file: {str(e)}")
    
    with col2:
        st.subheader("Preview")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.dataframe(df.head(), use_container_width=True)
            except Exception as e:
                st.error(f"Could not preview: {str(e)}")


with tab2:
    st.header("Manual Clause Input")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        input_method = st.radio(
            "Input Method",
            ["Paste Multiple Clauses", "Paste Raw Text"],
            horizontal=True
        )
    
    if input_method == "Paste Multiple Clauses":
        st.write("Enter each clause separated by a blank line:")
        
        clauses_text = st.text_area(
            "Clauses (one per line/paragraph)",
            height=300,
            placeholder="Clause 1\n\nClause 2\n\nClause 3..."
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Build Graph", use_container_width=True):
                if clauses_text.strip():
                    with st.spinner("Building graph..."):
                        try:
                            # Split by blank lines
                            clauses = [c.strip() for c in clauses_text.split('\n\n') if c.strip()]
                            
                            response = requests.post(
                                f"{st.session_state.api_url}/build-graph-from-clauses",
                                json={
                                    "clauses": clauses,
                                    "similarity_threshold": similarity_threshold
                                },
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                st.session_state.graph_data = response.json()
                                st.session_state.clauses = clauses
                                st.success(f"✅ Graph built with {len(clauses)} clauses")
                            else:
                                st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                                
                        except Exception as e:
                            st.error(f"❌ Failed: {str(e)}")
                else:
                    st.warning("Please enter some clauses")
    
    else:  # Raw text input
        st.write("Paste raw contract text (will be split into clauses automatically):")
        
        raw_text = st.text_area(
            "Raw Text",
            height=300,
            placeholder="Paste contract text here..."
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Build Graph", use_container_width=True):
                if raw_text.strip():
                    with st.spinner("Building graph..."):
                        try:
                            response = requests.post(
                                f"{st.session_state.api_url}/build-graph-from-text",
                                json={"text": raw_text},
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                st.session_state.graph_data = response.json()
                                st.session_state.clauses = [node['text'] for node in response.json()['nodes']]
                                st.success(f"✅ Graph built")
                            else:
                                st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                                
                        except Exception as e:
                            st.error(f"❌ Failed: {str(e)}")
                else:
                    st.warning("Please enter some text")


with tab3:
    st.header("Graph Visualization")
    
    if st.session_state.graph_data is None:
        st.info("📌 Upload a file or create clauses manually to visualize the graph")
    else:
        graph_data = st.session_state.graph_data
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Clauses", len(nodes))
        col2.metric("Similarities Found", len(edges))
        col3.metric("Avg Similarity", f"{sum(e['risk'] for e in edges) / len(edges):.3f}" if edges else "N/A")
        col4.metric("Graph Density", f"{2 * len(edges) / (len(nodes) * (len(nodes) - 1)):.3f}" if len(nodes) > 1 else "0")
        
        st.divider()
        
        # Interactive graph
        st.subheader("Contract Graph")
        
        try:
            # Create Plotly graph
            fig = go.Figure()
            
            # Add edges
            edge_x = []
            edge_y = []
            edge_text = []
            
            for edge in edges:
                source_idx = edge['source']
                target_idx = edge['target']
                
                # You would need node positions - for now using node indices as positions
                if source_idx < len(nodes) and target_idx < len(nodes):
                    edge_x.extend([source_idx, target_idx, None])
                    edge_y.extend([target_idx, source_idx, None])
                    edge_text.append(f"Similarity: {edge['risk']:.3f}")
            
            # Simplified graph visualization (circular layout)
            import math
            n = len(nodes)
            node_x = [math.cos(2 * math.pi * i / n) for i in range(n)]
            node_y = [math.sin(2 * math.pi * i / n) for i in range(n)]
            
            # Add edges
            edge_x = []
            edge_y = []
            
            for edge in edges:
                source = edge['source']
                target = edge['target']
                edge_x += [node_x[source], node_x[target], None]
                edge_y += [node_y[source], node_y[target], None]
            
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                showlegend=False
            ))
            
            # Add nodes
            node_colors = [edge['risk'] for i in range(len(nodes)) for edge in edges if edge['source'] == i]
            node_sizes = [15 for _ in nodes]
            
            node_text = [f"Clause {i}: {nodes[i]['text'][:100]}..." if len(nodes[i]['text']) > 100 else f"Clause {i}: {nodes[i]['text']}" 
                        for i in range(len(nodes))]
            
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=[f"{i}" for i in range(len(nodes))],
                textposition="top center",
                hovertext=node_text,
                hoverinfo="text",
                marker=dict(
                    size=node_sizes,
                    color='#1f77b4',
                    line=dict(width=2)
                ),
                showlegend=False
            ))
            
            fig.update_layout(
                title="Contract Clause Similarity Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=0, l=0, r=0, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error rendering graph: {str(e)}")
        
        st.divider()
        
        # Detailed edges table
        st.subheader("Similarity Matrix")
        
        if edges:
            edges_df = pd.DataFrame([
                {
                    "Source Clause": f"Clause {e['source']}",
                    "Target Clause": f"Clause {e['target']}",
                    "Similarity Score": f"{e['risk']:.4f}"
                }
                for e in sorted(edges, key=lambda x: x['risk'], reverse=True)
            ])
            
            st.dataframe(edges_df, use_container_width=True, hide_index=True)
        else:
            st.info("No similarities found with current threshold")
        
        st.divider()
        
        # Clauses detail
        st.subheader("Clauses Detail")
        
        for i, clause in enumerate(st.session_state.clauses):
            with st.expander(f"Clause {i} - {clause[:50]}..."):
                st.write(clause)


# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #888; font-size: 12px;'>
        <p>Contract Analysis System v1.0 | Powered by NLP & Graph Analysis</p>
    </div>
""", unsafe_allow_html=True)
