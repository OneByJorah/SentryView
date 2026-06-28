#!/usr/bin/env bash
set -euo pipefail

SERVER="${1:-localhost}"
printf "SentryView Healthcheck\nTarget: %s\n\n" "$SERVER"

check_service() {
    local name="$1"
    local url="$2"
    local expected="${3:-}"

    if [[ -n "$expected" ]]; then
        if curl -sf "$url" | grep -q "$expected"; then
            printf "  ✅ %s\n" "$name"
            return 0
        fi
    else
        if curl -sf "$url" >/dev/null; then
            printf "  ✅ %s\n" "$name"
            return 0
        fi
    fi
    printf "  ❌ %s\n" "$name"
    return 1
}

FAILED=0

echo "Core:"
check_service "Frontend" "http://$SERVER:3000/" "SentryView" || FAILED=1
check_service "Backend" "http://$SERVER:5000/health" "ok" || FAILED=1

echo ""
echo "Dependencies:"
check_service "PostgreSQL" "http://$SERVER:5432/" "" || FAILED=1
check_service "Redis" "http://$SERVER:6379/" "" || FAILED=1

echo ""
if [[ $FAILED -eq 0 ]]; then
    echo "🎉 All services healthy!"
    exit 0
else
    echo "⚠️  Some services are down"
    exit 1
fi