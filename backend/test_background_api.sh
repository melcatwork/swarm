#!/bin/bash
# Test script for background pipeline API

set -e

BASE_URL="http://localhost:8000"
FILE="${1:-../samples/file-transfer-system.tf}"

echo "=================================="
echo "Testing Background Pipeline API"
echo "=================================="
echo ""

# Check if backend is running
echo "1. Checking backend health..."
if ! curl -s "${BASE_URL}/api/health" > /dev/null; then
    echo "✗ Backend is not running at ${BASE_URL}"
    echo "  Start it with: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
    exit 1
fi
echo "✓ Backend is running"
echo ""

# Submit file
echo "2. Submitting file: $FILE"
if [ ! -f "$FILE" ]; then
    echo "✗ File not found: $FILE"
    exit 1
fi

SUBMIT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/swarm/run/quick/background" \
  -F "file=@$FILE")

echo "$SUBMIT_RESPONSE" | jq '.'

JOB_ID=$(echo "$SUBMIT_RESPONSE" | jq -r '.job_id')

if [ "$JOB_ID" = "null" ] || [ -z "$JOB_ID" ]; then
    echo "✗ Failed to submit job"
    echo "$SUBMIT_RESPONSE"
    exit 1
fi

echo "✓ Job submitted successfully"
echo "  Job ID: $JOB_ID"
echo ""

# Poll for status
echo "3. Polling job status (will take 5-10 minutes)..."
echo "   Press Ctrl+C to stop polling (job will continue in background)"
echo ""

LAST_STATUS=""
while true; do
    STATUS_RESPONSE=$(curl -s "${BASE_URL}/api/swarm/job/${JOB_ID}/status")

    CURRENT_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
    PROGRESS=$(echo "$STATUS_RESPONSE" | jq -r '.progress_percent')
    PHASE=$(echo "$STATUS_RESPONSE" | jq -r '.current_phase')
    ELAPSED=$(echo "$STATUS_RESPONSE" | jq -r '.elapsed_seconds // 0')

    # Only print if status changed
    if [ "$CURRENT_STATUS" != "$LAST_STATUS" ]; then
        echo ""
        echo "[$PROGRESS%] Status: $CURRENT_STATUS"
        echo "Phase: $PHASE"
        echo "Elapsed: ${ELAPSED}s"
        LAST_STATUS="$CURRENT_STATUS"
    else
        # Print progress on same line
        printf "\r[$PROGRESS%%] $CURRENT_STATUS: $PHASE (${ELAPSED}s)                    "
    fi

    if [ "$CURRENT_STATUS" = "completed" ]; then
        echo ""
        echo ""
        echo "✓ Analysis completed!"
        break
    elif [ "$CURRENT_STATUS" = "failed" ]; then
        echo ""
        echo ""
        echo "✗ Analysis failed!"
        ERROR=$(echo "$STATUS_RESPONSE" | jq -r '.error')
        echo "Error: $ERROR"
        echo ""
        echo "Full status response:"
        echo "$STATUS_RESPONSE" | jq '.'
        exit 1
    fi

    sleep 10
done

# Get results
echo ""
echo "4. Fetching results..."
RESULT_RESPONSE=$(curl -s "${BASE_URL}/api/swarm/job/${JOB_ID}/result")

# Save to file
OUTPUT_FILE="threat_model_${JOB_ID}.json"
echo "$RESULT_RESPONSE" | jq '.result' > "$OUTPUT_FILE"

echo "✓ Results saved to: $OUTPUT_FILE"
echo ""

# Show summary
echo "5. Analysis Summary:"
echo "----------------------------------"
FINAL_PATHS=$(echo "$RESULT_RESPONSE" | jq -r '.result.final_paths | length')
EXEC_TIME=$(echo "$RESULT_RESPONSE" | jq -r '.result.execution_time_seconds')
EXEC_SUMMARY=$(echo "$RESULT_RESPONSE" | jq -r '.result.executive_summary')

echo "Attack Paths Found: $FINAL_PATHS"
echo "Execution Time: ${EXEC_TIME}s"
echo ""
echo "Executive Summary:"
echo "$EXEC_SUMMARY"
echo ""

echo "=================================="
echo "✓ Background API Test Complete!"
echo "=================================="
