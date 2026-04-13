#!/bin/bash
# Check status of all Swarm TM services

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}   Swarm TM - Service Status${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Function to check if service is running
check_service() {
    local name=$1
    local url=$2
    local display_name=$3

    if curl -s --max-time 2 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $display_name"
        echo -e "  ${BLUE}$url${NC}"
        return 0
    else
        echo -e "${RED}✗${NC} $display_name"
        echo -e "  ${RED}Not responding at $url${NC}"
        return 1
    fi
}

# Check Ollama
echo -e "${YELLOW}[1/4] Ollama${NC}"
if check_service "ollama" "http://localhost:11434/api/tags" "Ollama Server"; then
    # Show available models
    MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | tr '\n' ', ' | sed 's/,$//')
    if [ -n "$MODELS" ]; then
        echo -e "  ${BLUE}Models: ${MODELS}${NC}"
    fi
fi
echo ""

# Check Backend
echo -e "${YELLOW}[2/4] Backend (FastAPI)${NC}"
if check_service "backend" "http://localhost:8000/api/health" "Backend API"; then
    # Show LLM status
    LLM_STATUS=$(curl -s http://localhost:8000/api/llm-status 2>/dev/null)
    if [ -n "$LLM_STATUS" ]; then
        PROVIDER=$(echo "$LLM_STATUS" | grep -o '"provider":"[^"]*"' | cut -d'"' -f4)
        MODEL=$(echo "$LLM_STATUS" | grep -o '"model":"[^"]*"' | cut -d'"' -f4)
        CONFIGURED=$(echo "$LLM_STATUS" | grep -o '"configured":[^,}]*' | cut -d':' -f2)

        echo -e "  ${BLUE}LLM Provider: ${PROVIDER}${NC}"
        echo -e "  ${BLUE}Model: ${MODEL}${NC}"
        if [ "$CONFIGURED" = "true" ]; then
            echo -e "  ${GREEN}✓ LLM Configured${NC}"
        else
            echo -e "  ${RED}✗ LLM Not Configured${NC}"
        fi
    fi

    # Check for running jobs
    JOBS=$(curl -s http://localhost:8000/api/swarm/jobs 2>/dev/null)
    if [ -n "$JOBS" ]; then
        JOB_COUNT=$(echo "$JOBS" | grep -o '"job_id"' | wc -l | tr -d ' ')
        if [ "$JOB_COUNT" -gt 0 ]; then
            echo -e "  ${BLUE}Recent Jobs: ${JOB_COUNT}${NC}"
        fi
    fi
fi
echo ""

# Check Frontend
echo -e "${YELLOW}[3/4] Frontend${NC}"
check_service "frontend" "http://localhost:5173" "Frontend (Vite)"
echo ""

# Check processes
echo -e "${YELLOW}[4/4] Running Processes${NC}"

OLLAMA_PID=$(pgrep -x ollama)
if [ -n "$OLLAMA_PID" ]; then
    echo -e "${GREEN}✓${NC} Ollama (PID: $OLLAMA_PID)"
else
    echo -e "${RED}✗${NC} Ollama (not running)"
fi

BACKEND_PID=$(pgrep -f "uvicorn app.main:app")
if [ -n "$BACKEND_PID" ]; then
    echo -e "${GREEN}✓${NC} Backend (PID: $BACKEND_PID)"
else
    echo -e "${RED}✗${NC} Backend (not running)"
fi

FRONTEND_PID=$(pgrep -f "vite")
if [ -n "$FRONTEND_PID" ]; then
    echo -e "${GREEN}✓${NC} Frontend (PID: $FRONTEND_PID)"
else
    echo -e "${RED}✗${NC} Frontend (not running)"
fi

# Check tmux session
if tmux has-session -t swarm-tm 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Tmux session 'swarm-tm' (active)"
    echo -e "  ${BLUE}Attach with: tmux attach -t swarm-tm${NC}"
fi

echo ""

# Summary
echo -e "${BLUE}=================================${NC}"

ALL_RUNNING=true
if ! curl -s --max-time 2 http://localhost:11434/api/tags > /dev/null 2>&1; then
    ALL_RUNNING=false
fi
if ! curl -s --max-time 2 http://localhost:8000/api/health > /dev/null 2>&1; then
    ALL_RUNNING=false
fi

if [ "$ALL_RUNNING" = true ]; then
    echo -e "${GREEN}✓ All core services are running${NC}"
    echo ""
    echo -e "${YELLOW}Quick Actions:${NC}"
    echo -e "  ${BLUE}Open Frontend:${NC}   open http://localhost:5173"
    echo -e "  ${BLUE}Open API Docs:${NC}   open http://localhost:8000/docs"
    echo -e "  ${BLUE}Run Test:${NC}        cd backend && ./test_background_api.sh ../samples/file-transfer-system.tf"
    echo -e "  ${BLUE}View Logs:${NC}       tail -f logs/backend.log"
    echo -e "  ${BLUE}Stop All:${NC}        ./stop-all.sh"
else
    echo -e "${RED}✗ Some services are not running${NC}"
    echo ""
    echo -e "${YELLOW}To start services:${NC}"
    echo -e "  ${BLUE}./start-all-tmux.sh${NC}   ${GREEN}# Recommended (tmux)${NC}"
    echo -e "  ${BLUE}./start-all.sh${NC}        ${GREEN}# Alternative${NC}"
fi

echo -e "${BLUE}=================================${NC}"
