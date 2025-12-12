#!/usr/bin/env python3
"""
Direct Wazuh Dashboard Import via API
Imports dashboard and visualizations directly to Wazuh without UI
"""

import json
import requests
import urllib3
import sys
from typing import Dict, List

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WazuhDashboardImporter:
    def __init__(self, url: str, username: str = "admin", password: str = None):
        self.url = url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False

    def import_dashboard(self, json_file: str) -> bool:
        """Import dashboard JSON directly"""

        print("\n" + "=" * 80)
        print("WAZUH DASHBOARD DIRECT IMPORT")
        print("=" * 80)

        try:
            # Read the JSON file
            print(f"\nReading dashboard file: {json_file}")
            with open(json_file, 'r') as f:
                dashboard_data = json.load(f)

            print(f"✅ File loaded successfully")
            print(f"   Objects to import: {len(dashboard_data.get('objects', []))}")

            # Get objects
            objects = dashboard_data.get('objects', [])
            print(f"\nObjects in file:")
            for obj in objects:
                print(f"  • {obj.get('type')}: {obj.get('id', obj.get('attributes', {}).get('title', 'Unknown'))}")

            print("\n" + "-" * 80)
            print("ATTEMPTING DIRECT IMPORT VIA OPENREEARCH DASHBOARDS")
            print("-" * 80)

            # Try to import each object
            imported_count = 0
            for obj in objects:
                obj_type = obj.get('type')
                obj_id = obj.get('id')

                # Skip if no ID
                if not obj_id:
                    obj_id = obj.get('attributes', {}).get('title', '').lower().replace(' ', '-')

                print(f"\nImporting {obj_type}: {obj_id}")

                # Construct import URL
                import_url = f"{self.url}/api/saved_objects/{obj_type}/{obj_id}"

                # Prepare request
                headers = {"Content-Type": "application/json"}

                # Import the object
                try:
                    response = self.session.post(
                        import_url,
                        json=obj.get('attributes', {}),
                        headers=headers,
                        timeout=10
                    )

                    if response.status_code in [200, 201]:
                        print(f"  ✅ Success ({response.status_code})")
                        imported_count += 1
                    else:
                        print(f"  ⚠️  Status: {response.status_code}")
                        print(f"  Response: {response.text[:200]}")

                except Exception as e:
                    print(f"  ❌ Error: {str(e)}")

            print("\n" + "=" * 80)
            print(f"IMPORT RESULTS: {imported_count}/{len(objects)} objects imported")
            print("=" * 80)

            if imported_count > 0:
                print("\n✅ Dashboard import complete!")
                print("\nNext steps:")
                print("  1. Refresh Wazuh Dashboard: https://10.10.10.40")
                print("  2. Go to: Dashboards")
                print("  3. Find: 'Threat Intelligence Summary'")
                print("  4. Click: Open")
                return True
            else:
                print("\n⚠️ No objects imported. This might indicate:")
                print("  • API authentication issue")
                print("  • Missing required fields in JSON")
                print("  • Dashboard already exists")
                return False

        except FileNotFoundError:
            print(f"❌ Error: File not found: {json_file}")
            return False
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON file: {json_file}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return False


def main():
    # Configuration
    WAZUH_URL = "https://10.10.10.40"
    DASHBOARD_FILE = "docs/wazuh-threat-intelligence-dashboard.json"

    # Create importer
    importer = WazuhDashboardImporter(WAZUH_URL)

    # Import dashboard
    success = importer.import_dashboard(DASHBOARD_FILE)

    if success:
        print("\n✅ Import completed successfully!")
        print("\nDashboard should now be available at:")
        print("  https://10.10.10.40/app/dashboards/dashboard/threat-intelligence-summary")
    else:
        print("\n⚠️ Import encountered issues. Trying alternative method...")
        print("\nAlternative: Import via Wazuh UI")
        print("  1. Open: https://10.10.10.40")
        print("  2. Menu → Management → Saved Objects")
        print("  3. Click: Import")
        print("  4. Select: docs/wazuh-threat-intelligence-dashboard.json")


if __name__ == "__main__":
    main()
