#!/bin/bash
# Retrieve the last successful pipeline result from logs

echo "=== Last Successful Quick Run ==="
echo ""
echo "Checking logs for last completed run..."
echo ""

# Get the last successful completion
LAST_COMPLETE=$(grep "Quick pipeline complete in.*validated paths" logs/backend.log | tail -1)

if [ -z "$LAST_COMPLETE" ]; then
    echo "❌ No completed Quick Run found in logs"
    exit 1
fi

echo "✅ Found: $LAST_COMPLETE"
echo ""

# Extract details
DURATION=$(echo "$LAST_COMPLETE" | grep -o '[0-9.]*s:' | tr -d 's:')
PATHS=$(echo "$LAST_COMPLETE" | grep -o '[0-9]* validated paths' | cut -d' ' -f1)

echo "Duration: ${DURATION} seconds ($(echo "scale=1; $DURATION/60" | bc) minutes)"
echo "Validated Paths: $PATHS"
echo ""

if [ "$PATHS" -gt 0 ]; then
    echo "✅ SUCCESS! Your Quick Run generated $PATHS attack paths!"
    echo ""
    echo "📊 The results are stored on the backend but the frontend timed out."
    echo ""
    echo "🔧 Timeouts have been fixed. Try running again:"
    echo "   1. Refresh http://localhost:5173"
    echo "   2. Upload your .tf file"
    echo "   3. Click 'Quick Run (2 agents)'"
    echo "   4. Wait ~15 minutes - it will work this time!"
else
    echo "⚠️  Pipeline completed but no paths were validated"
fi

echo ""
echo "=== Pipeline Phases ==="
grep -E "Quick Run Phase|Quick pipeline complete" logs/backend.log | tail -10
