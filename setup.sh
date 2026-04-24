#!/bin/bash

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Contract Analysis System - Backend${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Activate virtual environment and run backend
cd backend
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found at backend/.venv"
    exit 1
fi

source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""
echo -e "${BLUE}Starting API server...${NC}"
echo -e "${YELLOW}API will be available at http://localhost:8000${NC}"
echo -e "${YELLOW}API Docs at http://localhost:8000/docs${NC}"
echo ""

python main.py
