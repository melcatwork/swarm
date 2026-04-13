#!/bin/bash
# Start all services in tmux with split panes for easy monitoring

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SESSION_NAME="swarm-tm"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}   Swarm TM - Tmux Start${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo -e "${YELLOW}tmux not installed. Using regular start script...${NC}"
    exec ./start-all.sh
fi

# Check if session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo -e "${YELLOW}Session '$SESSION_NAME' already exists${NC}"
    echo -e "Options:"
    echo -e "  1. Attach to existing session: ${GREEN}tmux attach -t $SESSION_NAME${NC}"
    echo -e "  2. Kill and restart: ${RED}tmux kill-session -t $SESSION_NAME${NC} then run this script again"
    exit 1
fi

echo -e "${BLUE}Creating tmux session with 4 panes...${NC}"
echo ""

# Create new tmux session with 4 panes
tmux new-session -d -s "$SESSION_NAME" -n "swarm"

# Split into 4 panes:
# ┌─────────┬─────────┐
# │ Ollama  │ Backend │
# ├─────────┼─────────┤
# │Frontend │  Logs   │
# └─────────┴─────────┘

tmux split-window -h -t "$SESSION_NAME"
tmux split-window -v -t "$SESSION_NAME"
tmux select-pane -t "$SESSION_NAME":0.0
tmux split-window -v -t "$SESSION_NAME"

# =============================================================================
# Pane 0: Ollama
# =============================================================================

tmux select-pane -t "$SESSION_NAME":0.0
tmux send-keys -t "$SESSION_NAME":0.0 "echo -e '${BLUE}=== OLLAMA ===${NC}'" C-m
tmux send-keys -t "$SESSION_NAME":0.0 "# Check if Ollama is running" C-m

# Check if Ollama is already running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    tmux send-keys -t "$SESSION_NAME":0.0 "echo -e '${GREEN}✓ Ollama already running${NC}'" C-m
    tmux send-keys -t "$SESSION_NAME":0.0 "ollama list" C-m
else
    tmux send-keys -t "$SESSION_NAME":0.0 "echo -e '${YELLOW}Starting Ollama...${NC}'" C-m
    tmux send-keys -t "$SESSION_NAME":0.0 "ollama serve" C-m
    sleep 3
fi

# =============================================================================
# Pane 1: Backend
# =============================================================================

tmux select-pane -t "$SESSION_NAME":0.1
tmux send-keys -t "$SESSION_NAME":0.1 "echo -e '${BLUE}=== BACKEND (FastAPI) ===${NC}'" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "cd backend" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "source .venv/bin/activate" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "echo -e '${YELLOW}Starting uvicorn...${NC}'" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "sleep 3" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" C-m

# =============================================================================
# Pane 2: Frontend
# =============================================================================

tmux select-pane -t "$SESSION_NAME":0.2
tmux send-keys -t "$SESSION_NAME":0.2 "echo -e '${BLUE}=== FRONTEND ===${NC}'" C-m

# Find frontend directory
if [ -d "frontend" ]; then
    FRONTEND_DIR="frontend"
elif [ -d "client" ]; then
    FRONTEND_DIR="client"
elif [ -d "ui" ]; then
    FRONTEND_DIR="ui"
else
    tmux send-keys -t "$SESSION_NAME":0.2 "echo -e '${RED}Frontend directory not found${NC}'" C-m
    FRONTEND_DIR=""
fi

if [ -n "$FRONTEND_DIR" ]; then
    tmux send-keys -t "$SESSION_NAME":0.2 "cd $FRONTEND_DIR" C-m
    tmux send-keys -t "$SESSION_NAME":0.2 "echo -e '${YELLOW}Starting Vite dev server...${NC}'" C-m
    tmux send-keys -t "$SESSION_NAME":0.2 "sleep 5" C-m
    tmux send-keys -t "$SESSION_NAME":0.2 "npm run dev" C-m
fi

# =============================================================================
# Pane 3: Logs and Commands
# =============================================================================

tmux select-pane -t "$SESSION_NAME":0.3
tmux send-keys -t "$SESSION_NAME":0.3 "echo -e '${BLUE}=== QUICK COMMANDS ===${NC}'" C-m
tmux send-keys -t "$SESSION_NAME":0.3 "echo ''" C-m
tmux send-keys -t "$SESSION_NAME":0.3 "echo -e '${GREEN}Waiting for services to start...${NC}'" C-m
tmux send-keys -t "$SESSION_NAME":0.3 "sleep 10" C-m
tmux send-keys -t "$SESSION_NAME":0.3 "clear" C-m

# Show status after services start
tmux send-keys -t "$SESSION_NAME":0.3 "cat << 'EOF'
${BLUE}=================================
  Swarm TM - All Services Running
=================================${NC}

${YELLOW}Service URLs:${NC}
  ${GREEN}Frontend:${NC}  http://localhost:5173
  ${GREEN}Backend:${NC}   http://localhost:8000
  ${GREEN}API Docs:${NC}  http://localhost:8000/docs
  ${GREEN}Ollama:${NC}    http://localhost:11434

${YELLOW}Quick Test Commands:${NC}
  ${BLUE}# Check backend health${NC}
  curl http://localhost:8000/api/health

  ${BLUE}# Run background analysis${NC}
  cd backend
  ./test_background_api.sh ../samples/file-transfer-system.tf

  ${BLUE}# Submit file manually${NC}
  curl -X POST http://localhost:8000/api/swarm/run/quick/background \\
    -F \"file=@samples/file-transfer-system.tf\"

${YELLOW}Tmux Commands:${NC}
  ${BLUE}Ctrl+B then arrow keys${NC}  - Switch between panes
  ${BLUE}Ctrl+B then [${NC}            - Scroll mode (q to exit)
  ${BLUE}Ctrl+B then d${NC}            - Detach (keeps running)
  ${BLUE}tmux attach -t swarm-tm${NC}  - Re-attach later
  ${BLUE}Ctrl+C in each pane${NC}      - Stop services
  ${BLUE}exit${NC} in each pane        - Close pane
  ${BLUE}./stop-all.sh${NC}            - Stop everything

${BLUE}=================================${NC}

${GREEN}Press Ctrl+B then arrow keys to switch panes${NC}

EOF
" C-m

# Focus on the logs pane
tmux select-pane -t "$SESSION_NAME":0.3

# Attach to session
echo -e "${GREEN}✓ Tmux session created!${NC}"
echo ""
echo -e "${YELLOW}Attaching to session...${NC}"
echo ""
echo -e "${BLUE}Tmux Quick Reference:${NC}"
echo -e "  ${GREEN}Ctrl+B${NC} then ${GREEN}arrow keys${NC} - Navigate between panes"
echo -e "  ${GREEN}Ctrl+B${NC} then ${GREEN}[${NC}          - Scroll mode (q to quit)"
echo -e "  ${GREEN}Ctrl+B${NC} then ${GREEN}d${NC}          - Detach session (keeps running)"
echo -e "  ${GREEN}Ctrl+B${NC} then ${GREEN}:${NC}          - Command mode"
echo ""
echo -e "${YELLOW}To stop all services:${NC} ./stop-all.sh"
echo ""
sleep 2

tmux attach -t "$SESSION_NAME"
