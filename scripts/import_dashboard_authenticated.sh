#!/bin/bash
#
# Import Wazuh Dashboard via Authenticated API
# Handles Wazuh authentication and imports dashboard objects
#

set -e

# Configuration
WAZUH_URL="https://10.10.10.40"
WAZUH_USER="admin"
WAZUH_PASS="${WAZUH_PASSWORD:-SecureAdminPassword123!}"  # Edit if different
DASHBOARD_FILE="docs/wazuh-threat-intelligence-dashboard.json"
COOKIE_JAR="/tmp/wazuh_cookies.txt"

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
    -u "$WAZUH_USER:$WAZUH_PASS" \
    -H "Content-Type: application/json")

TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.token // empty' 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Authentication failed"
    echo "Response: $AUTH_RESPONSE"
    echo ""
    echo "Possible issues:"
    echo "  1. Wrong password - check WAZUH_PASSWORD environment variable"
    echo "  2. Wazuh server not responding"
    echo "  3. API endpoint incorrect"
    exit 1
fi

echo "✅ Authentication successful"
echo "   Token: ${TOKEN:0:20}..."
echo ""

# Step 2: Import dashboard
echo "Step 2: Importing dashboard..."
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

    # Check if successful
    if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
        echo "✅"
        ((IMPORTED++))
    else
        echo "❌"
        ((FAILED++))
        echo "     Error: $(echo "$RESPONSE" | head -c 100)"
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
    echo "  2. Click: Dashboards"
    echo "  3. Find: 'Threat Intelligence Summary'"
    echo "  4. Click: Open Dashboard"
    echo ""
    echo "Your dashboard should now be available with all 6 widgets!"
else
    echo "⚠️ No objects imported"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Verify Wazuh is running"
    echo "  2. Check credentials: $WAZUH_USER / $WAZUH_PASS"
    echo "  3. Try manual import via UI"
fi

echo "================================================================================"

# Cleanup
rm -f "$COOKIE_JAR"
