#!/bin/bash
while true; do
  sleep 5
  STATUS=$(curl -s http://127.0.0.1:8080/health || echo offline)
  if [[ "$STATUS" != *'ok'* ]]; then
    echo "[MONITOR] Backend is OFFLINE or not responding at \\$(date)" | tee -a monitor.log
    tail -20 "$FRONTEND_DIR/backend.log"
    echo "[MONITOR] Suggestion: Make sure you have a terminal open running: cd $BACKEND_DIR && python3 main.py"
  fi
  if grep -q 'Status: Offline' "$FRONTEND_DIR/frontend.log"; then
    echo "[MONITOR] Frontend is showing Status: Offline at \\$(date)" | tee -a monitor.log
    tail -20 "$FRONTEND_DIR/frontend.log"
    echo "[MONITOR] Suggestion: Check backend terminal and logs above."
  fi
  sleep 10
done
