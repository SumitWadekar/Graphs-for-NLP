#!/bin/bash

# Run backend API
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Starting Backend API${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

cd backend

if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found at backend/.venv"
    exit 1
fi

source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""
echo -e "${BLUE}Starting API server...${NC}"
echo -e "${YELLOW}API: http://localhost:8000${NC}"
echo -e "${YELLOW}Docs: http://localhost:8000/docs${NC}"
echo ""

python main.py
