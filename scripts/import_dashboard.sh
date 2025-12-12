#!/bin/bash
#
# Import Wazuh Dashboard via Authenticated API
# Reads credentials from .env.wazuh file
#

set -e

# Load environment variables from .env file
ENV_FILE="/home/brian/claude/.env.wazuh"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env.wazuh file not found at $ENV_FILE"
    exit 1
fi

source "$ENV_FILE"

# Configuration
DASHBOARD_FILE="docs/wazuh-threat-intelligence-dashboard.json"

echo "================================================================================"
echo "WAZUH DASHBOARD IMPORT - AUTHENTICATED"
echo "================================================================================"
echo ""
echo "Configuration:"
echo "  URL: $WAZUH_URL"
echo "  User: $WAZUH_USER"
echo "  Dashboard: $DASHBOARD_FILE"
echo ""

# Check if file exists
if [ ! -f "$DASHBOARD_FILE" ]; then
    echo "❌ Error: Dashboard file not found: $DASHBOARD_FILE"
    exit 1
fi

echo "✅ Dashboard file found"
echo ""

# Step 1: Get authentication token
echo "Step 1: Authenticating with Wazuh..."
AUTH_RESPONSE=$(curl -s -k -X POST \
    "$WAZUH_URL/api/authenticate" \
    -u "$WAZUH_USER:$WAZUH_PASSWORD" \
    -H "Content-Type: application/json")

TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.token // empty' 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Authentication failed"
    echo "Response: $AUTH_RESPONSE"
    echo ""
    echo "Possible issues:"
    echo "  1. Wrong credentials in .env.wazuh"
    echo "  2. Wazuh server not responding"
    echo "  3. API endpoint incorrect"
    exit 1
fi

echo "✅ Authentication successful"
echo "   Token obtained (hidden for security)"
echo ""

# Step 2: Import dashboard
echo "Step 2: Importing dashboard objects..."
echo ""

# Parse JSON and extract objects
OBJECTS=$(jq '.objects' "$DASHBOARD_FILE")
OBJECT_COUNT=$(echo "$OBJECTS" | jq 'length')

echo "Found $OBJECT_COUNT objects to import:"
echo ""

IMPORTED=0
FAILED=0

# Import each object
for i in $(seq 0 $((OBJECT_COUNT - 1))); do
    OBJ=$(echo "$OBJECTS" | jq ".[$i]")
    OBJ_TYPE=$(echo "$OBJ" | jq -r '.type')
    OBJ_ID=$(echo "$OBJ" | jq -r '.id')
    OBJ_ATTRS=$(echo "$OBJ" | jq '.attributes')

    echo -n "  Importing $OBJ_TYPE: $OBJ_ID ... "

    # Import via API
    RESPONSE=$(curl -s -k -X POST \
        "$WAZUH_URL/api/saved_objects/$OBJ_TYPE/$OBJ_ID" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -H "osd-xsrf: true" \
        -d "$OBJ_ATTRS" 2>&1)

    # Check if successful (look for either 200/201 or valid JSON response)
    if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
        # Check if it's an error response
        ERROR=$(echo "$RESPONSE" | jq -r '.error // empty' 2>/dev/null)
        if [ -n "$ERROR" ]; then
            echo "⚠️ ($ERROR)"
            ((FAILED++))
        else
            echo "✅"
            ((IMPORTED++))
        fi
    else
        echo "❌"
        ((FAILED++))
    fi
done

echo ""
echo "================================================================================"
echo "IMPORT RESULTS"
echo "================================================================================"
echo "Imported: $IMPORTED/$OBJECT_COUNT"
echo "Failed: $FAILED/$OBJECT_COUNT"
echo ""

if [ $IMPORTED -gt 0 ]; then
    echo "✅ Dashboard import complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Go to: https://10.10.10.40"
    echo "  2. Refresh the page (F5)"
    echo "  3. Click: Dashboards"
    echo "  4. Find: 'Threat Intelligence Summary'"
    echo "  5. Click: Open Dashboard"
    echo ""
    echo "Your dashboard should now be available with all 6 widgets!"
    echo ""
    echo "Direct URL:"
    echo "  https://10.10.10.40/app/dashboards/dashboard/threat-intelligence-summary"
else
    echo "⚠️ No objects imported"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Verify Wazuh is running: curl -k https://10.10.10.40"
    echo "  2. Check credentials in .env.wazuh"
    echo "  3. Verify dashboard file exists: $DASHBOARD_FILE"
    echo "  4. Try manual import via UI"
fi

echo "================================================================================"
