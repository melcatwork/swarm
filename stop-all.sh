#!/bin/bash
# Stop all Swarm TM services

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}   Stopping Swarm TM Services${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check LLM provider for more accurate status
if [ -f ".env" ]; then
    LLM_PROVIDER=$(grep "^LLM_PROVIDER=" .env | cut -d'=' -f2 2>/dev/null)
else
    LLM_PROVIDER="unknown"
fi

echo -e "${YELLOW}LLM Provider:${NC} ${BLUE}$LLM_PROVIDER${NC}"
echo ""

STOPPED_ANY=false

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Show current status before stopping
echo -e "${YELLOW}Current Status:${NC}"
if check_port 5173; then
    echo -e "  Frontend:  ${GREEN}Running${NC} (port 5173)"
else
    echo -e "  Frontend:  ${BLUE}Not running${NC}"
fi

if check_port 8000; then
    echo -e "  Backend:   ${GREEN}Running${NC} (port 8000)"
else
    echo -e "  Backend:   ${BLUE}Not running${NC}"
fi

if check_port 11434; then
    echo -e "  Ollama:    ${GREEN}Running${NC} (port 11434)"
else
    echo -e "  Ollama:    ${BLUE}Not running${NC}"
fi
echo ""

# Kill tmux session if exists
if tmux has-session -t swarm-tm 2>/dev/null; then
    echo -e "${YELLOW}Stopping tmux session 'swarm-tm'...${NC}"
    tmux kill-session -t swarm-tm
    echo -e "${GREEN}✓ Tmux session stopped${NC}"
    STOPPED_ANY=true
fi

# Kill frontend
if pkill -f "vite" 2>/dev/null; then
    echo -e "${YELLOW}Stopping frontend (Vite)...${NC}"
    sleep 1
    echo -e "${GREEN}✓ Frontend stopped${NC}"
    STOPPED_ANY=true
fi

if pkill -f "npm run dev" 2>/dev/null; then
    sleep 1
fi

# Kill backend
if pkill -f "uvicorn app.main:app" 2>/dev/null; then
    echo -e "${YELLOW}Stopping backend (FastAPI)...${NC}"
    sleep 1
    echo -e "${GREEN}✓ Backend stopped${NC}"
    STOPPED_ANY=true
fi

# Also kill any Python processes running the backend
if pkill -f "python.*app.main" 2>/dev/null; then
    sleep 1
fi

# Check Ollama (don't auto-kill as it might be used by other projects)
if [ "$LLM_PROVIDER" = "ollama" ]; then
    if pgrep -x "ollama" > /dev/null; then
        echo -e "${YELLOW}Ollama is still running${NC}"
        echo -e "  ${BLUE}To stop Ollama:${NC} pkill -f 'ollama serve'"
        echo -e "  ${BLUE}Note:${NC} Ollama may be used by other projects"
    fi
elif [ "$LLM_PROVIDER" = "bedrock" ] || [ "$LLM_PROVIDER" = "anthropic" ]; then
    echo -e "${BLUE}No local LLM server to stop (using $LLM_PROVIDER)${NC}"
fi

# Clean up PID file
if [ -f "logs/services.pid" ]; then
    rm -f logs/services.pid
fi

echo ""

# Verify all services stopped
echo -e "${YELLOW}Verifying services stopped:${NC}"
STILL_RUNNING=false

if check_port 5173; then
    echo -e "  Frontend:  ${RED}Still running on port 5173${NC}"
    STILL_RUNNING=true
else
    echo -e "  Frontend:  ${GREEN}✓ Stopped${NC}"
fi

if check_port 8000; then
    echo -e "  Backend:   ${RED}Still running on port 8000${NC}"
    STILL_RUNNING=true
else
    echo -e "  Backend:   ${GREEN}✓ Stopped${NC}"
fi

if [ "$LLM_PROVIDER" = "ollama" ]; then
    if check_port 11434; then
        echo -e "  Ollama:    ${BLUE}Running (not stopped, may be used by other projects)${NC}"
    else
        echo -e "  Ollama:    ${GREEN}✓ Stopped${NC}"
    fi
else
    echo -e "  LLM:       ${BLUE}Using $LLM_PROVIDER (no local server)${NC}"
fi

echo ""
if [ "$STOPPED_ANY" = true ]; then
    if [ "$STILL_RUNNING" = true ]; then
        echo -e "${YELLOW}⚠ Some services are still running${NC}"
        echo -e "  Run ${BLUE}lsof -i :5173${NC} or ${BLUE}lsof -i :8000${NC} to identify processes"
        echo -e "  Force kill: ${BLUE}pkill -9 -f 'vite'${NC} or ${BLUE}pkill -9 -f 'uvicorn'${NC}"
    else
        echo -e "${GREEN}✓ All services stopped successfully${NC}"
    fi
else
    echo -e "${BLUE}No running services found${NC}"
fi

echo ""
echo -e "${YELLOW}To restart:${NC}"
echo -e "  ./start-all.sh        ${BLUE}# Standard mode (logs in terminal)${NC}"
echo -e "  ./start-all-tmux.sh   ${BLUE}# Tmux mode (split panes, recommended)${NC}"
echo ""
echo -e "${YELLOW}Quick Status Check:${NC}"
echo -e "  lsof -i :5173         ${BLUE}# Check frontend${NC}"
echo -e "  lsof -i :8000         ${BLUE}# Check backend${NC}"
if [ "$LLM_PROVIDER" = "ollama" ]; then
    echo -e "  lsof -i :11434        ${BLUE}# Check Ollama${NC}"
fi
