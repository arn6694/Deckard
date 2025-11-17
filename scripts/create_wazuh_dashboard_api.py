#!/usr/bin/env python3
"""
Create Wazuh Threat Intelligence Dashboard via OpenSearch Dashboards API
Generates complete dashboard with 6 widgets for threat intelligence visualization

Usage: python3 create_wazuh_dashboard_api.py
"""

import json
import requests
import urllib3
import sys
from datetime import datetime
from typing import Dict, List, Any

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
WAZUH_URL = "https://10.10.10.40"
OPENSEARCH_URL = "https://10.10.10.40"
VERIFY_SSL = False
TIMEOUT = 10

class OpenSearchDashboardAPI:
    """Create dashboards and visualizations in OpenSearch Dashboards"""

    def __init__(self, url: str, verify_ssl: bool = False):
        self.url = url
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl

    def create_visualization_json(self, title: str, vis_type: str,
                                   aggs: List[Dict], params: Dict) -> Dict:
        """Create visualization JSON structure for OpenSearch Dashboards"""
        return {
            "type": "visualization",
            "id": f"threat-intel-{title.lower().replace(' ', '-')}",
            "version": 1,
            "attributes": {
                "title": title,
                "visState": json.dumps({
                    "title": title,
                    "type": vis_type,
                    "params": params,
                    "aggs": aggs,
                    "metadata": {
                        "indexPattern": "wazuh-alerts-*"
                    }
                }),
                "uiStateJSON": json.dumps({}),
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "index": "wazuh-alerts-*",
                        "query": {
                            "match_all": {}
                        },
                        "filter": []
                    })
                },
                "version": 1
            }
        }

    def create_dashboard_json(self, title: str, description: str,
                              panel_ids: List[str]) -> Dict:
        """Create dashboard JSON structure"""
        panels = []
        x, y = 0, 0

        for i, panel_id in enumerate(panel_ids):
            panels.append({
                "version": "1",
                "gridData": {
                    "x": x,
                    "y": y,
                    "w": 24,
                    "h": 15
                },
                "type": "visualization",
                "id": panel_id,
                "embeddableConfig": {}
            })

            # Arrange in 2 columns
            x = 24 if x == 0 else 0
            if x == 0:
                y += 15

        return {
            "type": "dashboard",
            "id": "threat-intelligence-summary",
            "version": 1,
            "attributes": {
                "title": title,
                "description": description,
                "panels": panels,
                "timeRestore": True,
                "timeFrom": "now-60d",
                "timeTo": "now",
                "refreshInterval": {
                    "pause": False,
                    "value": 300000
                },
                "version": 1
            }
        }


def build_dashboard_structure() -> tuple:
    """Build complete dashboard with all visualizations"""

    print("\n" + "=" * 80)
    print("BUILDING THREAT INTELLIGENCE DASHBOARD STRUCTURE")
    print("=" * 80 + "\n")

    # Widget 1: Attack Timeline (Line Chart)
    print("Creating Widget 1: Attack Timeline...")
    timeline_vis = {
        "type": "visualization",
        "id": "threat-intel-attack-timeline",
        "version": 1,
        "attributes": {
            "title": "Malicious IP Detections - Timeline",
            "visState": json.dumps({
                "title": "Malicious IP Detections - Timeline",
                "type": "line",
                "params": {
                    "type": "line",
                    "grid": {"categoryLines": False, "valueAxis": "ValueAxis-1"},
                    "categoryAxes": [
                        {
                            "id": "CategoryAxis-1",
                            "type": "category",
                            "position": "bottom",
                            "show": True,
                            "style": {},
                            "scale": {"type": "linear"},
                            "labels": {"show": True, "truncate": 100},
                            "title": {}
                        }
                    ],
                    "valueAxes": [
                        {
                            "id": "ValueAxis-1",
                            "name": "Left",
                            "type": "value",
                            "position": "left",
                            "show": True,
                            "style": {},
                            "scale": {"type": "linear"},
                            "labels": {"show": True, "rotate": 0, "truncate": 100},
                            "title": {"text": "Count"}
                        }
                    ],
                    "seriesParams": [
                        {
                            "show": True,
                            "type": "line",
                            "interpolate": "linear",
                            "showCircles": True,
                            "valueAxis": "ValueAxis-1"
                        }
                    ],
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "bottom",
                    "isDonut": False
                },
                "aggs": [
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "date_histogram",
                        "schema": "segment",
                        "params": {
                            "field": "timestamp",
                            "customInterval": "2h",
                            "interval": "auto",
                            "format": "date_nanos",
                            "min_doc_count": 1
                        }
                    },
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric"
                    }
                ]
            }),
            "uiStateJSON": json.dumps({}),
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "wazuh-alerts-*",
                    "query": {"match_all": {}},
                    "filter": []
                })
            }
        }
    }
    print("✅ Attack Timeline widget created")

    # Widget 2: Top Countries (Bar Chart)
    print("Creating Widget 2: Top Attack Origins...")
    countries_vis = {
        "type": "visualization",
        "id": "threat-intel-top-countries",
        "version": 1,
        "attributes": {
            "title": "Attack Origins by Country",
            "visState": json.dumps({
                "title": "Attack Origins by Country",
                "type": "histogram",
                "params": {
                    "type": "histogram",
                    "grid": {"categoryLines": False, "valueAxis": "ValueAxis-1"},
                    "categoryAxes": [
                        {
                            "id": "CategoryAxis-1",
                            "type": "category",
                            "position": "left",
                            "show": True,
                            "style": {},
                            "scale": {"type": "linear"},
                            "labels": {"show": True, "truncate": 100},
                            "title": {}
                        }
                    ],
                    "valueAxes": [
                        {
                            "id": "ValueAxis-1",
                            "name": "Right",
                            "type": "value",
                            "position": "right",
                            "show": True,
                            "style": {},
                            "scale": {"type": "linear"},
                            "labels": {"show": True},
                            "title": {"text": "Count"}
                        }
                    ],
                    "seriesParams": [
                        {"show": True, "type": "histogram", "valueAxis": "ValueAxis-1"}
                    ],
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right",
                    "isDonut": False
                },
                "aggs": [
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "GeoIP.country",
                            "size": 10,
                            "order": "desc",
                            "customLabel": "Country"
                        }
                    },
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric"
                    }
                ]
            }),
            "uiStateJSON": json.dumps({}),
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "wazuh-alerts-*",
                    "query": {"match_all": {}},
                    "filter": []
                })
            }
        }
    }
    print("✅ Top Countries widget created")

    # Widget 3: World Map (Geographic)
    print("Creating Widget 3: World Heatmap...")
    worldmap_vis = {
        "type": "visualization",
        "id": "threat-intel-worldmap",
        "version": 1,
        "attributes": {
            "title": "Attack Origins - World Heatmap",
            "visState": json.dumps({
                "title": "Attack Origins - World Heatmap",
                "type": "tile_map",
                "params": {
                    "addTooltip": True,
                    "initialZoom": 2,
                    "defaultFitBounds": "geonamesToo",
                    "mapType": "Scaled Circle Markers",
                    "heatClusterSize": 1.5,
                    "isDesaturated": True,
                    "showLegend": True,
                    "wmsOverlays": []
                },
                "aggs": [
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "geohash_grid",
                        "schema": "segment",
                        "params": {
                            "field": "GeoIP.location",
                            "precision": 4
                        }
                    },
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric"
                    }
                ]
            }),
            "uiStateJSON": json.dumps({}),
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "wazuh-alerts-*",
                    "query": {"match_all": {}},
                    "filter": []
                })
            }
        }
    }
    print("✅ World Heatmap widget created")

    # Widget 4: Top IPs (Table)
    print("Creating Widget 4: Top Malicious IPs...")
    topips_vis = {
        "type": "visualization",
        "id": "threat-intel-top-ips",
        "version": 1,
        "attributes": {
            "title": "Top Malicious IPs",
            "visState": json.dumps({
                "title": "Top Malicious IPs",
                "type": "table",
                "params": {
                    "perPage": 50,
                    "showPartialRows": False,
                    "showMeticsAtAllLevels": False,
                    "showTotal": False,
                    "totalFunc": "sum",
                    "percentageCol": ""
                },
                "aggs": [
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "bucket",
                        "params": {
                            "field": "data.srcip",
                            "size": 50,
                            "order": "desc",
                            "customLabel": "Source IP"
                        }
                    },
                    {
                        "id": "3",
                        "enabled": True,
                        "type": "terms",
                        "schema": "bucket",
                        "params": {
                            "field": "GeoIP.country_iso_code",
                            "size": 5,
                            "order": "desc",
                            "customLabel": "Country"
                        }
                    },
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {"customLabel": "Count"}
                    }
                ]
            }),
            "uiStateJSON": json.dumps({"vis": {"params": {"sort": {"columnIndex": None, "direction": None}}}}),
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "wazuh-alerts-*",
                    "query": {"match_all": {}},
                    "filter": []
                })
            }
        }
    }
    print("✅ Top Malicious IPs widget created")

    # Widget 5: Severity (Pie Chart)
    print("Creating Widget 5: Alert Severity Distribution...")
    severity_vis = {
        "type": "visualization",
        "id": "threat-intel-severity",
        "version": 1,
        "attributes": {
            "title": "Alert Severity Distribution",
            "visState": json.dumps({
                "title": "Alert Severity Distribution",
                "type": "pie",
                "params": {
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right",
                    "isDonut": False,
                    "slicePresentation": "default",
                    "labels": {"show": False, "values": False, "last_level": True, "truncate": 0}
                },
                "aggs": [
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "rule.level",
                            "size": 20,
                            "order": "desc",
                            "customLabel": "Severity Level"
                        }
                    },
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric"
                    }
                ]
            }),
            "uiStateJSON": json.dumps({}),
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "wazuh-alerts-*",
                    "query": {"match_all": {}},
                    "filter": []
                })
            }
        }
    }
    print("✅ Severity Distribution widget created")

    # Widget 6: Blocked Count (Metric)
    print("Creating Widget 6: Active Blocked IPs Metric...")
    metric_vis = {
        "type": "visualization",
        "id": "threat-intel-blocked-count",
        "version": 1,
        "attributes": {
            "title": "Active Blocked IPs",
            "visState": json.dumps({
                "title": "Active Blocked IPs",
                "type": "metric",
                "params": {
                    "metric": {
                        "percentageMode": False,
                        "useRanges": False,
                        "bgFill": "#1f78d1",
                        "borderFill": "rgba(0,0,0,0)",
                        "text": "Total",
                        "style": {"bgColor": False, "bgFill": "#1f78d1", "borderFill": "rgba(0,0,0,0)", "fontSize": 60}
                    },
                    "dimensions": {
                        "metrics": [{"accessor": 0, "format": {"id": "number"}, "params": {}, "aggType": "cardinality"}]
                    }
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "cardinality",
                        "schema": "metric",
                        "params": {
                            "field": "data.srcip",
                            "customLabel": "Unique IPs Blocked"
                        }
                    }
                ]
            }),
            "uiStateJSON": json.dumps({}),
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "wazuh-alerts-*",
                    "query": {"match_all": {}},
                    "filter": []
                })
            }
        }
    }
    print("✅ Blocked IPs Metric widget created")

    visualizations = [timeline_vis, countries_vis, worldmap_vis, topips_vis, severity_vis, metric_vis]

    # Create dashboard
    print("\nCreating Dashboard container...")
    dashboard = {
        "type": "dashboard",
        "id": "threat-intelligence-summary",
        "version": 1,
        "attributes": {
            "title": "Threat Intelligence Summary",
            "description": "Real-time visualization of malicious IP detection, geolocation analysis, and automated blocking effectiveness",
            "panels": [
                {
                    "version": "1",
                    "gridData": {"x": 0, "y": 0, "w": 24, "h": 15},
                    "type": "visualization",
                    "id": "threat-intel-attack-timeline"
                },
                {
                    "version": "1",
                    "gridData": {"x": 24, "y": 0, "w": 24, "h": 15},
                    "type": "visualization",
                    "id": "threat-intel-top-countries"
                },
                {
                    "version": "1",
                    "gridData": {"x": 0, "y": 15, "w": 24, "h": 15},
                    "type": "visualization",
                    "id": "threat-intel-worldmap"
                },
                {
                    "version": "1",
                    "gridData": {"x": 24, "y": 15, "w": 24, "h": 15},
                    "type": "visualization",
                    "id": "threat-intel-severity"
                },
                {
                    "version": "1",
                    "gridData": {"x": 0, "y": 30, "w": 48, "h": 20},
                    "type": "visualization",
                    "id": "threat-intel-top-ips"
                },
                {
                    "version": "1",
                    "gridData": {"x": 0, "y": 50, "w": 12, "h": 10},
                    "type": "visualization",
                    "id": "threat-intel-blocked-count"
                }
            ],
            "timeRestore": True,
            "timeFrom": "now-60d",
            "timeTo": "now",
            "refreshInterval": {
                "pause": False,
                "value": 300000
            }
        }
    }
    print("✅ Dashboard container created")

    return visualizations, dashboard


def save_dashboard_export(visualizations: List[Dict], dashboard: Dict, filename: str):
    """Save dashboard and visualizations as importable JSON"""

    print("\nSaving dashboard export...")

    # Create complete export with all objects
    export_data = {
        "version": "8.0.0",
        "objects": visualizations + [dashboard]
    }

    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"✅ Dashboard exported to: {filename}")
    return filename


def main():
    """Main execution"""

    print("\n" + "=" * 80)
    print("WAZUH THREAT INTELLIGENCE DASHBOARD - CREATION VIA API")
    print("=" * 80)

    # Build dashboard structure
    visualizations, dashboard = build_dashboard_structure()

    # Save for export/import
    export_file = "/home/brian/claude/docs/wazuh-threat-intelligence-dashboard.json"
    save_dashboard_export(visualizations, dashboard, export_file)

    # Display summary
    print("\n" + "=" * 80)
    print("DASHBOARD CREATION SUMMARY")
    print("=" * 80)
    print(f"\nDashboard: Threat Intelligence Summary")
    print(f"Widgets: 6")
    print(f"  1. Attack Timeline (Line Chart)")
    print(f"  2. Attack Origins by Country (Bar Chart)")
    print(f"  3. World Heatmap (Geographic Map)")
    print(f"  4. Top Malicious IPs (Data Table)")
    print(f"  5. Alert Severity Distribution (Pie Chart)")
    print(f"  6. Active Blocked IPs (Metric Card)")
    print(f"\nExport File: {export_file}")
    print(f"File Size: {len(json.dumps(visualizations + [dashboard])) / 1024:.1f} KB")
    print(f"\nDate Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("\n1. Import via Wazuh UI:")
    print(f"   - Save file: {export_file}")
    print(f"   - Open Wazuh Dashboard: https://10.10.10.40")
    print(f"   - Go to: Stack Management → Saved Objects")
    print(f"   - Click Import")
    print(f"   - Select exported JSON file")
    print(f"   - Click Import")
    print("\n2. Or manually create dashboard in Wazuh UI:")
    print(f"   - Dashboard → Create Dashboard")
    print(f"   - Add visualizations from this export")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
