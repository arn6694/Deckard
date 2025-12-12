#!/usr/bin/env python3
"""
Create Wazuh Dashboard directly via Wazuh API
Uses Wazuh manager to create dashboard and visualizations
"""

import requests
import json
import urllib3
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WazuhDashboardCreator:
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.token = None
        self.session = requests.Session()
        self.session.verify = False

    def authenticate(self):
        """Get authentication token from Wazuh"""
        print("Authenticating with Wazuh API...")
        try:
            response = self.session.post(
                f"{self.url}/api/authenticate",
                auth=(self.user, self.password),
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def get_headers(self):
        """Get headers with authentication token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def check_wazuh_status(self):
        """Check if Wazuh API is working"""
        print("\nChecking Wazuh status...")
        try:
            response = self.session.get(
                f"{self.url}/api/cluster/status",
                headers=self.get_headers(),
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Wazuh API is working")
                print(f"   Cluster status: {data.get('data', {}).get('status')}")
                return True
            else:
                print(f"⚠️ Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def check_indices(self):
        """Check if wazuh-alerts index exists"""
        print("\nChecking Wazuh alert indices...")
        try:
            # Try to get indices from Wazuh API
            response = self.session.get(
                f"{self.url}/api/indices",
                headers=self.get_headers(),
                timeout=10
            )

            if response.status_code == 200:
                print(f"✅ Indices available")
                return True
            else:
                print(f"⚠️ Could not query indices: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def load_dashboard_json(self, json_file):
        """Load dashboard JSON from file"""
        print(f"\nLoading dashboard from: {json_file}")
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            print(f"✅ Dashboard JSON loaded")
            print(f"   Objects: {len(data.get('objects', []))}")
            return data
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return None

    def import_dashboard_objects(self, json_file):
        """Import dashboard objects via Wazuh integration"""
        print("\n" + "="*80)
        print("ATTEMPTING DASHBOARD IMPORT VIA WAZUH API")
        print("="*80)

        # Load dashboard JSON
        dashboard_data = self.load_dashboard_json(json_file)
        if not dashboard_data:
            return False

        # Get objects
        objects = dashboard_data.get('objects', [])
        print(f"\nImporting {len(objects)} objects...")
        print()

        imported = 0
        failed = 0

        # Try to import each object
        for obj in objects:
            obj_type = obj.get('type')
            obj_id = obj.get('id')
            obj_attrs = obj.get('attributes', {})

            print(f"Importing {obj_type}: {obj_id}")

            # Try different API endpoints
            endpoints_to_try = [
                f"{self.url}/api/saved_objects/{obj_type}/{obj_id}",
                f"{self.url}/kibana/api/saved_objects/{obj_type}/{obj_id}",
                f"{self.url}/opensearch-dashboards/api/saved_objects/{obj_type}/{obj_id}",
            ]

            success = False
            for endpoint in endpoints_to_try:
                try:
                    response = self.session.post(
                        endpoint,
                        json=obj_attrs,
                        headers=self.get_headers(),
                        timeout=10
                    )

                    if response.status_code in [200, 201, 409]:
                        print(f"  ✅ Success at: {endpoint.split('/api/')[1] if '/api/' in endpoint else endpoint}")
                        imported += 1
                        success = True
                        break
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        print(f"  Status: {response.status_code}")

                except Exception as e:
                    continue

            if not success:
                print(f"  ⚠️ Could not import via any endpoint")
                failed += 1

        print("\n" + "="*80)
        print("IMPORT RESULTS")
        print("="*80)
        print(f"Imported: {imported}/{len(objects)}")
        print(f"Failed: {failed}/{len(objects)}")

        return imported > 0

def main():
    """Main execution"""

    # Load credentials
    env_file = Path("/home/brian/claude/.env.wazuh")
    if not env_file.exists():
        print("❌ Error: .env.wazuh not found")
        return False

    env_vars = {}
    with open(env_file) as f:
        for line in f:
            if '=' in line:
                key, val = line.strip().split('=', 1)
                env_vars[key] = val

    url = env_vars.get('WAZUH_URL')
    user = env_vars.get('WAZUH_USER')
    password = env_vars.get('WAZUH_PASSWORD')

    print("="*80)
    print("WAZUH DASHBOARD CREATION VIA API")
    print("="*80)
    print(f"\nURL: {url}")
    print(f"User: {user}")
    print()

    # Create dashboard creator
    creator = WazuhDashboardCreator(url, user, password)

    # Authenticate
    if not creator.authenticate():
        print("\n❌ Authentication failed")
        return False

    # Check Wazuh status
    creator.check_wazuh_status()

    # Check indices
    creator.check_indices()

    # Import dashboard
    success = creator.import_dashboard_objects("docs/wazuh-threat-intelligence-dashboard.json")

    print("\n" + "="*80)
    if success:
        print("✅ DASHBOARD IMPORT SUCCESSFUL!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Go to: https://10.10.10.40")
        print("  2. Refresh page (F5)")
        print("  3. Navigate to: Dashboards")
        print("  4. Find: 'Threat Intelligence Summary'")
        print("  5. Click: Open")
    else:
        print("⚠️ DASHBOARD IMPORT ENCOUNTERED ISSUES")
        print("="*80)
        print("\nManual import steps:")
        print("  1. Go to: https://10.10.10.40/app/management")
        print("  2. Find: 'Saved Objects' or 'Import/Export'")
        print("  3. Click: Import")
        print("  4. Select: docs/wazuh-threat-intelligence-dashboard.json")
    print()

if __name__ == "__main__":
    main()
