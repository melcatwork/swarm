#!/bin/bash
# Start all services for Swarm TM: Ollama, Backend, Frontend
# Updated: 2026-04-25 - Added Living Intelligence System support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

# Show configured LLM provider and model
LLM_PROVIDER=$(grep "^LLM_PROVIDER=" .env | cut -d'=' -f2 | tr -d ' "' | tr -d "'")
if [ -n "$LLM_PROVIDER" ]; then
    echo -e "${BLUE}LLM Provider:${NC} ${GREEN}$LLM_PROVIDER${NC}"

    case "$LLM_PROVIDER" in
        "ollama")
            OLLAMA_MODEL=$(grep "^OLLAMA_MODEL=" .env | cut -d'=' -f2 | tr -d ' "' | tr -d "'")
            echo -e "${BLUE}Ollama Model:${NC} ${GREEN}${OLLAMA_MODEL:-qwen3:14b}${NC}"
            ;;
        "bedrock")
            BEDROCK_MODEL=$(grep "^BEDROCK_MODEL=" .env | cut -d'=' -f2 | tr -d ' "' | tr -d "'")
            echo -e "${BLUE}Bedrock Model:${NC} ${GREEN}${BEDROCK_MODEL:-anthropic.claude-3-sonnet-20240229-v1:0}${NC}"
            ;;
        "anthropic")
            ANTHROPIC_MODEL=$(grep "^ANTHROPIC_MODEL=" .env | cut -d'=' -f2 | tr -d ' "' | tr -d "'")
            echo -e "${BLUE}Anthropic Model:${NC} ${GREEN}${ANTHROPIC_MODEL:-claude-sonnet-4-6}${NC}"
            ;;
    esac
    echo ""
fi

# Check for Living Intelligence System configuration
echo -e "${PURPLE}Living Intelligence Status:${NC}"
if grep -q "^AWS_BEARER_TOKEN_BEDROCK=" .env 2>/dev/null; then
    echo -e "  ${GREEN}✓ AWS Bedrock configured for persona patch generation${NC}"
elif grep -q "^ANTHROPIC_API_KEY=" .env 2>/dev/null; then
    echo -e "  ${GREEN}✓ Anthropic API configured for persona patch generation${NC}"
else
    echo -e "  ${YELLOW}⚠ No LLM credentials for persona patch generation${NC}"
    echo -e "    Set AWS_BEARER_TOKEN_BEDROCK or ANTHROPIC_API_KEY to enable"
fi
echo ""

# =============================================================================
# 1. Check LLM Provider
# =============================================================================

echo -e "${BLUE}[1/3] Checking LLM Provider...${NC}"

case "$LLM_PROVIDER" in
    "ollama")
        echo -e "${YELLOW}Provider: Ollama (local)${NC}"

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

        # Check if configured model is available
        OLLAMA_MODEL=$(grep "^OLLAMA_MODEL=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ')
        echo -n "  Checking for $OLLAMA_MODEL model... "
        if ollama list | grep -q "$OLLAMA_MODEL"; then
            echo -e "${GREEN}✓ Found${NC}"
        else
            echo -e "${YELLOW}Not found${NC}"
            echo -e "${YELLOW}  Pulling $OLLAMA_MODEL (this may take a few minutes)...${NC}"
            ollama pull "$OLLAMA_MODEL"
            echo -e "${GREEN}✓ Model downloaded${NC}"
        fi
        ;;

    "bedrock")
        echo -e "${YELLOW}Provider: AWS Bedrock${NC}"
        BEDROCK_MODEL=$(grep "^BEDROCK_MODEL=" .env | cut -d'=' -f2 | tr -d ' "' | tr -d "'")
        echo -e "  Model: ${GREEN}${BEDROCK_MODEL:-anthropic.claude-3-sonnet-20240229-v1:0}${NC}"

        # Check for bearer token
        if grep -q "^AWS_BEARER_TOKEN_BEDROCK=" .env; then
            echo -e "${GREEN}✓ AWS bearer token configured${NC}"
        else
            echo -e "${YELLOW}⚠ AWS_BEARER_TOKEN_BEDROCK not set${NC}"
            echo -e "  Run: ${BLUE}bash backend/scripts/get_aws_token.sh${NC}"
        fi
        ;;

    "anthropic")
        echo -e "${YELLOW}Provider: Anthropic API${NC}"
        ANTHROPIC_MODEL=$(grep "^ANTHROPIC_MODEL=" .env | cut -d'=' -f2 | tr -d ' "' | tr -d "'")
        echo -e "  Model: ${GREEN}${ANTHROPIC_MODEL:-claude-sonnet-4-6}${NC}"
        if grep -q "^ANTHROPIC_API_KEY=" .env; then
            echo -e "${GREEN}✓ API key configured${NC}"
        else
            echo -e "${RED}✗ ANTHROPIC_API_KEY not found in .env${NC}"
            exit 1
        fi
        ;;

    *)
        echo -e "${RED}✗ Unknown LLM_PROVIDER: $LLM_PROVIDER${NC}"
        echo "  Supported providers: ollama, bedrock, anthropic"
        exit 1
        ;;
esac

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
if [ "$LLM_PROVIDER" = "ollama" ]; then
    echo -e "  ${GREEN}Ollama:${NC}    http://localhost:11434"
fi
echo ""
echo -e "${YELLOW}Log Files:${NC}"
if [ "$LLM_PROVIDER" = "ollama" ] && [ -f "$LOG_DIR/ollama.log" ]; then
    echo -e "  Ollama:   $LOG_DIR/ollama.log"
fi
echo -e "  Backend:  $LOG_DIR/backend.log"
echo -e "  Frontend: $LOG_DIR/frontend.log"
echo ""
echo -e "${YELLOW}Quick Test Commands:${NC}"
echo -e "  ${BLUE}# Test backend health${NC}"
echo -e "  curl http://localhost:8000/api/health"
echo ""
echo -e "  ${BLUE}# Check available LLM models${NC}"
echo -e "  curl http://localhost:8000/api/llm/models"
echo ""
echo -e "  ${BLUE}# Check persona intelligence status${NC}"
echo -e "  curl http://localhost:8000/api/swarm/persona-status | jq"
echo ""
echo -e "  ${BLUE}# Test samples (choose one):${NC}"
echo -e "  curl -X POST http://localhost:8000/api/swarm/run/quick \\"
echo -e "    -F \"file=@samples/capital-one-breach-replica.tf\""
echo -e "  curl -X POST http://localhost:8000/api/swarm/run/quick \\"
echo -e "    -F \"file=@samples/scarleteel-breach-replica.tf\""
echo ""
echo -e "${YELLOW}Four Run Modes Available:${NC}"
echo -e "  ${GREEN}/api/swarm/run${NC}             ${BLUE}# Full pipeline (all agents, ~25-30 min)${NC}"
echo -e "  ${GREEN}/api/swarm/run/quick${NC}       ${BLUE}# Quick test (2 agents, ~14 min)${NC}"
echo -e "  ${GREEN}/api/swarm/run/single${NC}      ${BLUE}# Single agent (specify ?agent_name=...)${NC}"
echo -e "  ${GREEN}/api/swarm/run/stigmergic${NC}  ${BLUE}# Stigmergic swarm (sequential, emergent)${NC}"
echo ""
echo -e "${PURPLE}Living Intelligence System:${NC}"
echo -e "  ${BLUE}# Setup automatic daily updates (run once)${NC}"
echo -e "  ./setup-auto-intel-sync.sh"
echo ""
echo -e "  ${BLUE}# Sync threat intel manually${NC}"
echo -e "  python3 backend/scripts/sync_intel.py --force"
echo ""
echo -e "  ${BLUE}# Review generated patches${NC}"
echo -e "  python3 backend/scripts/review_patches.py --summary"
echo ""
echo -e "  ${BLUE}# Check persona intelligence status (API)${NC}"
echo -e "  curl http://localhost:8000/api/swarm/persona-status | jq"
echo ""
echo -e "  ${BLUE}# Test Bedrock connection${NC}"
echo -e "  python3 backend/scripts/test_bedrock_connection.py"
echo ""
echo -e "${YELLOW}Recent Updates (2026-04-25):${NC}"
echo -e "  ${GREEN}✓${NC} Living Intelligence System ${GREEN}fully operational${NC}"
echo -e "  ${GREEN}✓${NC} ${GREEN}69 AI-generated patches${NC} applied to personas"
echo -e "  ${GREEN}✓${NC} Vulnerability Intelligence UI ${GREEN}(CVE evidence in paths)${NC}"
echo -e "  ${GREEN}✓${NC} Persona status panel shows patch currency"
echo -e "  ${GREEN}✓${NC} CVE aggregation summary (KEV, PoC, EPSS, CVSS)"
echo -e "  ${GREEN}✓${NC} AWS Bedrock + Anthropic API support"
echo -e "  ${GREEN}✓${NC} Attack paths support ${GREEN}up to 10 steps${NC} (was 3-5)"
echo ""
echo -e "${YELLOW}View Real-Time Logs:${NC}"
echo -e "  tail -f $LOG_DIR/backend.log   ${BLUE}# Backend logs${NC}"
if [ "$LLM_PROVIDER" = "ollama" ]; then
    echo -e "  tail -f $LOG_DIR/ollama.log    ${BLUE}# Ollama logs${NC}"
fi
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
