#!/bin/bash

# MaxMind GeoIP Setup for Wazuh
# Downloads GeoLite2-City database and configures Wazuh for geolocation enrichment

set -e

echo "================================================"
echo "WAZUH GeoIP Enrichment Setup"
echo "================================================"
echo ""

# Load environment
source /home/brian/claude/.env.wazuh

LICENSE_KEY=$MAXMIND_LICENSE_KEY
WAZUH_MANAGER="10.10.10.40"
WAZUH_HOME="/var/ossec"

echo "MaxMind License Key: ${LICENSE_KEY:0:10}..."
echo "Wazuh Manager: $WAZUH_MANAGER"
echo ""

# Step 1: Download GeoLite2-City database
echo "Step 1: Downloading GeoLite2-City database..."
echo ""

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

cd $TEMP_DIR

# Download the database
echo "Downloading from MaxMind..."
wget -q "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=${LICENSE_KEY}&suffix=tar.gz" \
  -O GeoLite2-City.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ Failed to download GeoLite2 database"
    echo "   Check your license key and internet connection"
    exit 1
fi

echo "✅ Downloaded GeoLite2-City database"

# Extract the archive
tar -xzf GeoLite2-City.tar.gz
EXTRACTED_DIR=$(ls -d GeoLite2-City_*/ 2>/dev/null | head -1)

if [ -z "$EXTRACTED_DIR" ]; then
    echo "❌ Failed to extract database"
    exit 1
fi

echo "✅ Extracted database"
echo ""

# Step 2: Transfer to Wazuh Manager
echo "Step 2: Transferring database to Wazuh Manager ($WAZUH_MANAGER)..."
echo ""

# Create the GeoIP directory on Wazuh manager if it doesn't exist
ssh -o StrictHostKeyChecking=no brian@$WAZUH_MANAGER "sudo mkdir -p $WAZUH_HOME/etc/geoip" 2>/dev/null || true

# Copy the database file
MMDB_FILE="${EXTRACTED_DIR}GeoLite2-City.mmdb"
if [ ! -f "$MMDB_FILE" ]; then
    echo "❌ Could not find GeoLite2-City.mmdb in extracted archive"
    exit 1
fi

scp -o StrictHostKeyChecking=no "$MMDB_FILE" brian@$WAZUH_MANAGER:/tmp/GeoLite2-City.mmdb

# Move to final location with proper permissions (wazuh user, not ossec)
ssh -o StrictHostKeyChecking=no brian@$WAZUH_MANAGER "sudo mv /tmp/GeoLite2-City.mmdb $WAZUH_HOME/etc/geoip/ && sudo chmod 644 $WAZUH_HOME/etc/geoip/GeoLite2-City.mmdb"

echo "✅ Database installed on Wazuh Manager"
echo ""

# Step 3: Verify database is readable
echo "Step 3: Verifying database..."
ssh -o StrictHostKeyChecking=no brian@$WAZUH_MANAGER "ls -lh $WAZUH_HOME/etc/geoip/GeoLite2-City.mmdb"

echo ""
echo "================================================"
echo "✅ GeoIP DATABASE SETUP COMPLETE"
echo "================================================"
echo ""
echo "Database location: $WAZUH_HOME/etc/geoip/GeoLite2-City.mmdb"
echo ""
echo "Next: Configure Wazuh to use the GeoIP database for enrichment"
echo ""

