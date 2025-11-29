#!/bin/bash
# check-doc-health.sh
# Silent documentation health check for session start
# Only outputs if significant drift detected (10+ files changed)

# Get the current working directory from environment or use pwd
PROJECT_DIR="${PWD:-$(pwd)}"
DOC_MANAGER_DIR="$PROJECT_DIR/.doc-manager"
BASELINE_FILE="$DOC_MANAGER_DIR/memory/repo-baseline.json"

# Check if doc-manager is initialized
if [ ! -d "$DOC_MANAGER_DIR" ]; then
    # Not initialized - silent exit
    exit 0
fi

# Check if baseline exists
if [ ! -f "$BASELINE_FILE" ]; then
    # No baseline - silent exit
    exit 0
fi

# Get baseline timestamp
BASELINE_MTIME=$(stat -c %Y "$BASELINE_FILE" 2>/dev/null || stat -f %m "$BASELINE_FILE" 2>/dev/null)
if [ -z "$BASELINE_MTIME" ]; then
    exit 0
fi

# Calculate days since last sync
CURRENT_TIME=$(date +%s)
DAYS_SINCE_SYNC=$(( (CURRENT_TIME - BASELINE_MTIME) / 86400 ))

# Count changed files since baseline (simplified check)
# This is a rough estimate - actual change detection uses the MCP tool
CHANGED_COUNT=0

# Try to detect changes using git if available
if command -v git &> /dev/null && [ -d "$PROJECT_DIR/.git" ]; then
    # Get files changed since baseline timestamp
    BASELINE_DATE=$(date -d "@$BASELINE_MTIME" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r "$BASELINE_MTIME" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
    if [ -n "$BASELINE_DATE" ]; then
        CHANGED_COUNT=$(git diff --name-only --since="$BASELINE_DATE" 2>/dev/null | wc -l)
    fi
fi

# Silent check - only output if significant drift (10+ files OR 7+ days)
if [ "$CHANGED_COUNT" -ge 10 ] || [ "$DAYS_SINCE_SYNC" -ge 7 ]; then
    # Output JSON for the hook system to process
    cat << EOF
{
    "drift_detected": true,
    "changed_count": $CHANGED_COUNT,
    "days_since_sync": $DAYS_SINCE_SYNC,
    "message": "Documentation may be out of sync. $CHANGED_COUNT files changed, last sync $DAYS_SINCE_SYNC days ago. Run /doc-status to check."
}
EOF
fi

# Exit successfully (silent if no significant drift)
exit 0
