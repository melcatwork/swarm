#!/bin/bash
# Setup automatic persona intelligence updates via cron
# Run this script once to enable daily automatic updates

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Swarm TM - Auto Intelligence Sync Setup${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Get absolute path to project
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${YELLOW}Project directory:${NC} $PROJECT_DIR"
echo ""

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Please create .env file with LLM configuration first"
    exit 1
fi

# Check for Bedrock or Anthropic credentials
if grep -q "^AWS_BEARER_TOKEN_BEDROCK=" "$PROJECT_DIR/.env" 2>/dev/null; then
    LLM_CONFIGURED="AWS Bedrock"
    TOKEN_REFRESH_NEEDED=true
elif grep -q "^ANTHROPIC_API_KEY=" "$PROJECT_DIR/.env" 2>/dev/null; then
    LLM_CONFIGURED="Anthropic API"
    TOKEN_REFRESH_NEEDED=false
else
    echo -e "${RED}✗ No LLM credentials found${NC}"
    echo "Set AWS_BEARER_TOKEN_BEDROCK or ANTHROPIC_API_KEY to enable auto-sync"
    exit 1
fi

echo -e "${GREEN}✓ LLM configured:${NC} $LLM_CONFIGURED"
echo ""

# Check if crontab exists
if crontab -l > /dev/null 2>&1; then
    echo -e "${YELLOW}Current crontab entries:${NC}"
    crontab -l | grep -v "^#" | grep -v "^$" || echo "  (none)"
    echo ""
fi

# Prepare cron entries
SYNC_CRON="0 2 * * * cd $PROJECT_DIR && /usr/bin/python3 backend/scripts/sync_intel.py --force >> logs/intel-sync.log 2>&1"

if [ "$TOKEN_REFRESH_NEEDED" = true ]; then
    TOKEN_CRON="0 0 * * * cd $PROJECT_DIR && bash backend/scripts/get_aws_token.sh >> logs/token-refresh.log 2>&1"
fi

echo -e "${BLUE}Proposed cron jobs:${NC}"
echo ""
echo -e "${GREEN}1. Daily intelligence sync (runs at 2:00 AM):${NC}"
echo "   $SYNC_CRON"
echo ""

if [ "$TOKEN_REFRESH_NEEDED" = true ]; then
    echo -e "${GREEN}2. Daily AWS token refresh (runs at midnight):${NC}"
    echo "   $TOKEN_CRON"
    echo ""
fi

echo -e "${YELLOW}This will:${NC}"
echo "  • Pull latest threat intelligence from CISA KEV, MITRE ATT&CK"
echo "  • Generate AI patches for persona updates (using $LLM_CONFIGURED)"
echo "  • Apply patches automatically (no manual review)"
echo "  • Log all output to logs/intel-sync.log"
if [ "$TOKEN_REFRESH_NEEDED" = true ]; then
    echo "  • Refresh AWS Bedrock token daily (tokens expire after 12 hours)"
fi
echo ""

read -p "Install these cron jobs? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cancelled.${NC}"
    exit 0
fi

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Install cron jobs
echo -e "${BLUE}Installing cron jobs...${NC}"

# Get existing crontab or create empty
TEMP_CRON=$(mktemp)
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# Remove old swarm-tm entries if they exist
sed -i '' '/swarm-tm/d' "$TEMP_CRON" 2>/dev/null || true
sed -i '' '/sync_intel.py/d' "$TEMP_CRON" 2>/dev/null || true
sed -i '' '/get_aws_token.sh/d' "$TEMP_CRON" 2>/dev/null || true

# Add new entries with comments
echo "" >> "$TEMP_CRON"
echo "# Swarm TM - Automated Intelligence Sync" >> "$TEMP_CRON"
echo "$SYNC_CRON" >> "$TEMP_CRON"

if [ "$TOKEN_REFRESH_NEEDED" = true ]; then
    echo "# Swarm TM - AWS Token Refresh" >> "$TEMP_CRON"
    echo "$TOKEN_CRON" >> "$TEMP_CRON"
fi

# Install new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo -e "${GREEN}✓ Cron jobs installed successfully!${NC}"
echo ""

# Verify installation
echo -e "${BLUE}Verification:${NC}"
echo ""
crontab -l | grep -A 1 "Swarm TM"
echo ""

echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next automatic update:${NC} Tomorrow at 2:00 AM"
echo -e "${YELLOW}Logs will be written to:${NC} logs/intel-sync.log"
if [ "$TOKEN_REFRESH_NEEDED" = true ]; then
    echo -e "${YELLOW}Token refresh:${NC} Daily at midnight (logs/token-refresh.log)"
fi
echo ""
echo -e "${BLUE}Manual commands:${NC}"
echo -e "  ${GREEN}Run sync now:${NC}        python3 backend/scripts/sync_intel.py --force"
echo -e "  ${GREEN}Check patch status:${NC}  python3 backend/scripts/review_patches.py --summary"
echo -e "  ${GREEN}View sync log:${NC}       tail -f logs/intel-sync.log"
echo -e "  ${GREEN}Remove cron jobs:${NC}    crontab -e (then delete the Swarm TM lines)"
echo ""
echo -e "${BLUE}================================================${NC}"
