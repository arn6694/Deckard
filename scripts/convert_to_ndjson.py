#!/usr/bin/env python3
"""
Convert dashboard JSON to NDJSON format for Wazuh import
NDJSON (newline-delimited JSON) is required by OpenSearch Dashboards
"""

import json
from pathlib import Path

def convert_json_to_ndjson(json_file, output_file):
    """Convert standard JSON to NDJSON format"""

    print(f"Converting {json_file} to NDJSON format...")

    # Read the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Get objects
    objects = data.get('objects', [])
    print(f"Found {len(objects)} objects to convert")

    # Write NDJSON format
    with open(output_file, 'w') as f:
        for obj in objects:
            # Each line is a complete JSON object
            ndjson_line = {
                "type": obj.get('type'),
                "id": obj.get('id'),
                "attributes": obj.get('attributes', {}),
                "version": obj.get('version', 1)
            }

            # Write as one line
            f.write(json.dumps(ndjson_line) + '\n')

    print(f"✅ Converted to NDJSON format: {output_file}")
    print(f"   Objects: {len(objects)}")

    # Verify the file
    with open(output_file, 'r') as f:
        lines = f.readlines()

    print(f"   Lines in NDJSON: {len(lines)}")
    print(f"   File size: {Path(output_file).stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    json_file = "docs/wazuh-threat-intelligence-dashboard.json"
    output_file = "docs/wazuh-threat-intelligence-dashboard.ndjson"

    convert_json_to_ndjson(json_file, output_file)

    print("\n" + "="*80)
    print("✅ CONVERSION COMPLETE")
    print("="*80)
    print(f"\nUse this file to import:")
    print(f"  File: {output_file}")
    print(f"\nSteps:")
    print(f"  1. Go to: https://10.10.10.40/app/management/opensearch_dashboards/objects")
    print(f"  2. Click: Import")
    print(f"  3. Select: {output_file}")
    print(f"  4. Click: Import")
    print()
