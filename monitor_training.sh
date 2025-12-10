#!/bin/bash

# Script to continuously monitor training progress

echo "============================================================"
echo "Training Monitor"
echo "============================================================"
echo ""
echo "This will check training status every 30 seconds."
echo "Press Ctrl+C to stop monitoring."
echo ""

while true; do
    clear
    echo "============================================================"
    echo "Training Status - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================================"
    echo ""
    
    # Check if process is running
    if pgrep -f "complete_training.py" > /dev/null; then
        echo "✅ Training process: RUNNING"
    else
        echo "⏳ Training process: NOT RUNNING"
    fi
    echo ""
    
    # Check if model exists
    if [ -f "models/auralguard_model.h5" ]; then
        SIZE=$(du -h models/auralguard_model.h5 | cut -f1)
        MTIME=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" models/auralguard_model.h5)
        echo "✅ Model file: EXISTS"
        echo "   Size: $SIZE"
        echo "   Modified: $MTIME"
        echo ""
        echo "🎉 TRAINING COMPLETE!"
        echo ""
        echo "Next steps:"
        echo "  docker-compose up -d"
        break
    else
        echo "⏳ Model file: NOT FOUND (training in progress)"
    fi
    echo ""
    
    # Check MLflow runs
    if [ -d "mlruns" ]; then
        RUN_COUNT=$(find mlruns -type d -name "run-*" 2>/dev/null | wc -l | tr -d ' ')
        echo "📊 MLflow runs: $RUN_COUNT"
    fi
    echo ""
    echo "============================================================"
    echo "Checking again in 30 seconds... (Press Ctrl+C to stop)"
    echo "============================================================"
    
    sleep 30
done

