#!/bin/bash

# Run frontend
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Starting Streamlit Frontend${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

cd frontend

if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found at frontend/.venv"
    exit 1
fi

source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""
echo -e "${BLUE}Starting Streamlit app...${NC}"
echo -e "${YELLOW}App: http://localhost:8501${NC}"
echo ""

streamlit run app.py
