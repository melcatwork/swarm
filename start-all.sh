#!/bin/bash
# Start all services for Swarm TM: Ollama, Backend, Frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log directory
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# PID file to track running services
PID_FILE="$LOG_DIR/services.pid"

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping all services...${NC}"

    if [ -f "$PID_FILE" ]; then
        while read -r line; do
            SERVICE=$(echo "$line" | cut -d: -f1)
            PID=$(echo "$line" | cut -d: -f2)

            if ps -p "$PID" > /dev/null 2>&1; then
                echo -e "${YELLOW}Stopping $SERVICE (PID: $PID)${NC}"
                kill "$PID" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi

    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true

    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Set up trap to cleanup on exit
trap cleanup EXIT INT TERM

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}   Swarm TM - Quick Start${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "  Please create .env file with LLM configuration"
    echo "  See README.md or .env.example for details"
    exit 1
fi

# Show configured model
OLLAMA_MODEL=$(grep "^OLLAMA_MODEL=" .env | cut -d'=' -f2)
if [ -n "$OLLAMA_MODEL" ]; then
    echo -e "${BLUE}Configured Model:${NC} ${GREEN}$OLLAMA_MODEL${NC}"
    echo ""
fi

# =============================================================================
# 1. Check Ollama
# =============================================================================

echo -e "${BLUE}[1/3] Checking Ollama...${NC}"

if ! command -v ollama &> /dev/null; then
    echo -e "${RED}✗ Ollama not installed${NC}"
    echo "  Install from: https://ollama.ai"
    exit 1
fi

# Check if Ollama is already running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama is already running${NC}"
    OLLAMA_ALREADY_RUNNING=true
else
    echo -e "${YELLOW}Starting Ollama server...${NC}"
    OLLAMA_ALREADY_RUNNING=false

    # Start Ollama in background
    ollama serve > "$LOG_DIR/ollama.log" 2>&1 &
    OLLAMA_PID=$!
    echo "ollama:$OLLAMA_PID" >> "$PID_FILE"

    # Wait for Ollama to be ready
    echo -n "  Waiting for Ollama to start"
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}✓ Ollama started (PID: $OLLAMA_PID)${NC}"
            break
        fi
        echo -n "."
        sleep 1

        if [ $i -eq 30 ]; then
            echo ""
            echo -e "${RED}✗ Ollama failed to start${NC}"
            echo "  Check logs: $LOG_DIR/ollama.log"
            exit 1
        fi
    done
fi

# Check if model is available (using qwen3:14b for better JSON generation)
echo -n "  Checking for qwen3:14b model... "
if ollama list | grep -q "qwen3:14b"; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${YELLOW}Not found${NC}"
    echo -e "${YELLOW}  Pulling qwen3:14b (this may take a few minutes, ~9.3GB)...${NC}"
    ollama pull qwen3:14b
    echo -e "${GREEN}✓ Model downloaded${NC}"
fi

echo ""

# =============================================================================
# 2. Start Backend
# =============================================================================

echo -e "${BLUE}[2/3] Starting Backend (FastAPI)...${NC}"

cd backend

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo "  Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "  Installing dependencies..."
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install -r requirements.txt
fi

# Kill any existing backend process
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 1

# Start backend
echo -e "${YELLOW}Starting uvicorn server...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "../$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "backend:$BACKEND_PID" >> "../$PID_FILE"

# Wait for backend to be ready
echo -n "  Waiting for backend to start"
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
        echo -e "  ${GREEN}http://localhost:8000${NC}"
        break
    fi
    echo -n "."
    sleep 1

    if [ $i -eq 30 ]; then
        echo ""
        echo -e "${RED}✗ Backend failed to start${NC}"
        echo "  Check logs: $LOG_DIR/backend.log"
        tail -20 "../$LOG_DIR/backend.log"
        exit 1
    fi
done

cd ..
echo ""

# =============================================================================
# 3. Start Frontend
# =============================================================================

echo -e "${BLUE}[3/3] Starting Frontend...${NC}"

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}✗ Frontend directory not found${NC}"
    echo "  Looking for frontend in current directory..."

    # Check common frontend directory names
    for dir in client ui web app; do
        if [ -d "$dir" ]; then
            echo -e "${YELLOW}Found frontend in: $dir${NC}"
            FRONTEND_DIR="$dir"
            break
        fi
    done

    if [ -z "$FRONTEND_DIR" ]; then
        echo -e "${YELLOW}⚠ Frontend not found, skipping...${NC}"
        FRONTEND_DIR=""
    fi
else
    FRONTEND_DIR="frontend"
fi

if [ -n "$FRONTEND_DIR" ]; then
    cd "$FRONTEND_DIR"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        npm install
    fi

    # Kill any existing frontend process
    pkill -f "vite" 2>/dev/null || true
    sleep 1

    # Start frontend
    echo -e "${YELLOW}Starting Vite dev server...${NC}"
    npm run dev > "../$LOG_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo "frontend:$FRONTEND_PID" >> "../$PID_FILE"

    # Wait for frontend to be ready
    echo -n "  Waiting for frontend to start"
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
            echo -e "  ${GREEN}http://localhost:5173${NC}"
            break
        fi
        echo -n "."
        sleep 1

        if [ $i -eq 30 ]; then
            echo ""
            echo -e "${YELLOW}⚠ Frontend may still be starting...${NC}"
            echo "  Check logs: $LOG_DIR/frontend.log"
        fi
    done

    cd ..
fi

echo ""

# =============================================================================
# Status Summary
# =============================================================================

echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}✓ All services started!${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "${YELLOW}Service URLs:${NC}"
echo -e "  ${GREEN}Frontend:${NC}  http://localhost:5173"
echo -e "  ${GREEN}Backend:${NC}   http://localhost:8000"
echo -e "  ${GREEN}API Docs:${NC}  http://localhost:8000/docs"
echo -e "  ${GREEN}Ollama:${NC}    http://localhost:11434"
echo ""
echo -e "${YELLOW}Log Files:${NC}"
echo -e "  Ollama:   $LOG_DIR/ollama.log"
echo -e "  Backend:  $LOG_DIR/backend.log"
echo -e "  Frontend: $LOG_DIR/frontend.log"
echo ""
echo -e "${YELLOW}Quick Test Commands:${NC}"
echo -e "  ${BLUE}# Test backend health${NC}"
echo -e "  curl http://localhost:8000/api/health"
echo ""
echo -e "  ${BLUE}# Submit analysis (background mode)${NC}"
echo -e "  curl -X POST http://localhost:8000/api/swarm/run/quick/background \\"
echo -e "    -F \"file=@samples/file-transfer-system.tf\""
echo ""
echo -e "  ${BLUE}# Run automated test${NC}"
echo -e "  cd backend && ./test_background_api.sh ../samples/file-transfer-system.tf"
echo ""
echo -e "${YELLOW}Recommended Agents for Single Agent Testing:${NC}"
echo -e "  ${GREEN}apt29_cozy_bear${NC}      ${BLUE}# Best for cloud infrastructure (nation-state sophistication)${NC}"
echo -e "  ${GREEN}scattered_spider${NC}    ${BLUE}# Best for identity/SSO/MFA testing${NC}"
echo -e "  ${BLUE}Use in frontend: Select agent → Run Single Agent Test${NC}"
echo ""
echo -e "${YELLOW}View Real-Time Logs:${NC}"
echo -e "  tail -f $LOG_DIR/backend.log   ${BLUE}# Backend logs${NC}"
echo -e "  tail -f $LOG_DIR/ollama.log    ${BLUE}# Ollama logs${NC}"
echo -e "  tail -f $LOG_DIR/frontend.log  ${BLUE}# Frontend logs${NC}"
echo ""
echo -e "${RED}Press Ctrl+C to stop all services${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Keep script running and show combined logs
echo -e "${BLUE}Showing combined logs (Ctrl+C to exit):${NC}"
echo ""

# Tail all logs
tail -f "$LOG_DIR/backend.log" 2>/dev/null &
TAIL_PID=$!

# Wait for Ctrl+C
wait $TAIL_PID 2>/dev/null || true
