#!/bin/bash
# Check pipeline status from latest run

echo "=== Pipeline Diagnostics ==="
echo ""

echo "1. Exploration Phase:"
grep "exploration complete.*paths" logs/backend.log | tail -3
echo ""

echo "2. Evaluation Phase:"
grep "Evaluation complete.*paths" logs/backend.log | tail -3
echo ""

echo "3. Adversarial Validation:"
grep "Arbitrator produced.*paths" logs/backend.log | tail -3
echo ""

echo "4. Recent Warnings (missing fields):"
grep "WARNING.*missing" logs/backend.log | tail -10
echo ""

echo "5. Final Results:"
grep "pipeline complete.*validated paths" logs/backend.log | tail -3
echo ""

echo "6. JSON Parsing Errors:"
grep "Failed to parse JSON" logs/backend.log | tail -5
echo ""

echo "=== Last Run Summary ==="
LAST_RUN=$(grep -n "Single Agent Pipeline with\|Quick Pipeline\|Full Pipeline" logs/backend.log | tail -1)
if [ -n "$LAST_RUN" ]; then
    LINE_NUM=$(echo "$LAST_RUN" | cut -d: -f1)
    echo "Found pipeline run at line $LINE_NUM"
    tail -n +$LINE_NUM logs/backend.log | grep "Phase\|complete\|paths\|ERROR" | head -20
fi
