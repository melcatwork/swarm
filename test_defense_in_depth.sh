#!/bin/bash
# Test script to verify defense-in-depth implementation

echo "========================================"
echo "Defense-in-Depth Implementation Test"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Find Python interpreter
PYTHON_BIN="backend/.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    echo -e "${YELLOW}Note:${NC} Using system python3 (venv not found at $PYTHON_BIN)"
    PYTHON_BIN="python3"
fi

# Test 1: Check backend health
echo -e "${YELLOW}[Test 1]${NC} Checking backend health..."
HEALTH=$(curl -s http://localhost:8000/api/health)
if echo "$HEALTH" | grep -q '"status":"ok"'; then
    echo -e "${GREEN}✓ PASS${NC} - Backend is healthy"
else
    echo -e "${RED}✗ FAIL${NC} - Backend is not healthy"
    exit 1
fi
echo ""

# Test 2: Check if defense_layers module exists
echo -e "${YELLOW}[Test 2]${NC} Checking if defense_layers.py exists..."
if [ -f "backend/app/swarm/defense_layers.py" ]; then
    echo -e "${GREEN}✓ PASS${NC} - defense_layers.py exists"
    LINE_COUNT=$(wc -l < backend/app/swarm/defense_layers.py)
    echo "   Lines: $LINE_COUNT"
else
    echo -e "${RED}✗ FAIL${NC} - defense_layers.py not found"
    exit 1
fi
echo ""

# Test 3: Check if defense_layers can be imported
echo -e "${YELLOW}[Test 3]${NC} Testing defense_layers module import..."
cd backend
IMPORT_TEST=$($PYTHON_BIN -c "from app.swarm.defense_layers import get_defense_in_depth_mitigations, DefenseLayer; print('OK')" 2>&1)
cd ..
if echo "$IMPORT_TEST" | grep -q "OK"; then
    echo -e "${GREEN}✓ PASS${NC} - defense_layers module imports successfully"
else
    echo -e "${RED}✗ FAIL${NC} - defense_layers module import failed"
    echo "$IMPORT_TEST"
    exit 1
fi
echo ""

# Test 4: Test getting mitigations for a specific technique
echo -e "${YELLOW}[Test 4]${NC} Testing mitigation retrieval for T1078.004..."
cd backend
MITIGATION_TEST=$($PYTHON_BIN -c "
from app.swarm.defense_layers import get_defense_in_depth_mitigations
mitigations = get_defense_in_depth_mitigations('T1078.004')
layer_count = sum(len(mits) for mits in mitigations.values())
print(f'{layer_count}')
" 2>&1)
cd ..

if [ "$MITIGATION_TEST" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC} - Retrieved $MITIGATION_TEST mitigations for T1078.004"
else
    echo -e "${RED}✗ FAIL${NC} - No mitigations found for T1078.004"
    echo "Output: $MITIGATION_TEST"
    exit 1
fi
echo ""

# Test 5: Count total techniques with defense-in-depth
echo -e "${YELLOW}[Test 5]${NC} Counting techniques with defense-in-depth..."
cd backend
TECHNIQUE_COUNT=$($PYTHON_BIN -c "
from app.swarm.defense_layers import DEFENSE_IN_DEPTH_MITIGATIONS
print(len(DEFENSE_IN_DEPTH_MITIGATIONS))
" 2>&1)
cd ..

echo -e "${GREEN}✓ INFO${NC} - $TECHNIQUE_COUNT techniques have defense-in-depth mitigations"
echo ""

# Test 6: Verify defense layers are defined
echo -e "${YELLOW}[Test 6]${NC} Verifying defense layers..."
cd backend
LAYERS=$($PYTHON_BIN -c "
from app.swarm.defense_layers import DefenseLayer
layers = [layer.value for layer in DefenseLayer]
print(','.join(layers))
" 2>&1)
cd ..

if echo "$LAYERS" | grep -q "preventive" && echo "$LAYERS" | grep -q "detective"; then
    echo -e "${GREEN}✓ PASS${NC} - Defense layers defined: $LAYERS"
else
    echo -e "${RED}✗ FAIL${NC} - Defense layers not properly defined"
    exit 1
fi
echo ""

# Test 7: Check frontend component for defense-in-depth UI
echo -e "${YELLOW}[Test 7]${NC} Checking frontend defense-in-depth UI..."
if grep -q "Defense-in-Depth Mitigations" frontend/src/pages/ThreatModelPage.jsx; then
    echo -e "${GREEN}✓ PASS${NC} - Frontend UI includes defense-in-depth display"
else
    echo -e "${RED}✗ FAIL${NC} - Frontend UI not updated"
    exit 1
fi
echo ""

# Test 8: Check for priority fields in models
echo -e "${YELLOW}[Test 8]${NC} Checking enhanced models..."
if grep -q "defense_layer.*Optional" backend/app/swarm/models.py; then
    echo -e "${GREEN}✓ PASS${NC} - Models include defense_layer field"
else
    echo -e "${RED}✗ FAIL${NC} - Models not enhanced"
    exit 1
fi
echo ""

# Test 9: Count total mitigations
echo -e "${YELLOW}[Test 9]${NC} Counting total mitigations..."
cd backend
TOTAL_MITIGATIONS=$($PYTHON_BIN -c "
from app.swarm.defense_layers import DEFENSE_IN_DEPTH_MITIGATIONS
total = 0
for technique, layers in DEFENSE_IN_DEPTH_MITIGATIONS.items():
    for layer, mits in layers.items():
        total += len(mits)
print(total)
" 2>&1)
cd ..

echo -e "${GREEN}✓ INFO${NC} - Total mitigations defined: $TOTAL_MITIGATIONS"
echo ""

# Test 10: Check documentation
echo -e "${YELLOW}[Test 10]${NC} Checking documentation..."
DOC_PASS=0
if [ -f "DEFENSE_IN_DEPTH_GUIDE.md" ]; then
    echo -e "${GREEN}✓ PASS${NC} - User guide exists"
    DOC_PASS=$((DOC_PASS + 1))
else
    echo -e "${RED}✗ FAIL${NC} - User guide missing"
fi

if [ -f "DEFENSE_IN_DEPTH_CHANGES.md" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Changes documentation exists"
    DOC_PASS=$((DOC_PASS + 1))
else
    echo -e "${RED}✗ FAIL${NC} - Changes documentation missing"
fi
echo ""

if [ $DOC_PASS -lt 2 ]; then
    exit 1
fi

# Summary
echo "========================================"
echo -e "${GREEN}All Tests Passed!${NC}"
echo "========================================"
echo ""
echo "Defense-in-Depth Implementation Summary:"
echo "  - Techniques covered: $TECHNIQUE_COUNT"
echo "  - Total mitigations: $TOTAL_MITIGATIONS"
echo "  - Defense layers: $LAYERS"
echo ""
echo "Next Steps:"
echo "  1. Run a threat model: ./start-all.sh"
echo "  2. Upload a .tf file at http://localhost:5173"
echo "  3. Run 'Quick Run' or 'Single Agent Test'"
echo "  4. Click 'Show Defense-in-Depth Mitigations' to see layered controls"
echo ""
echo "Documentation:"
echo "  - User Guide: cat DEFENSE_IN_DEPTH_GUIDE.md"
echo "  - Changes: cat DEFENSE_IN_DEPTH_CHANGES.md"
echo ""
