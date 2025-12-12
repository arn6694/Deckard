# Wazuh Dashboard Import - Updated Instructions

## The Issue

You're seeing:
- Empty dashboard list (no dashboards exist yet)
- "Add panels" shows "No matching objects found" (no visualizations exist yet)

This means we need to import the saved objects (visualizations + dashboard) first.

---

## Where to Find Import

### Method 1: Left Sidebar Menu
1. Look at the **left sidebar** (hamburger menu ☰)
2. Click the menu icon in top-left
3. Look for one of these options:
   - **Stack Management**
   - **Management**
   - **Settings**
   - **Admin**

### Method 2: Try Direct URL
Go directly to:
```
https://10.10.10.40/app/management/opensearch_dashboards/objects
```

Or try:
```
https://10.10.10.40/app/management
```

### Method 3: Look for Import Icon
Sometimes import is accessible via:
- Menu icon (☰) → Management → Saved Objects
- Or a direct "Import" button somewhere

---

## What We're Looking For

We need to find the **Saved Objects** section where you can:
- Import objects
- Upload the JSON file
- See list of dashboards/visualizations

---

## Can You Help Me?

Can you describe what you see in the left sidebar? When you click the menu icon (☰), what options do you see? For example:
- Discover?
- Dashboards?
- Visualizations?
- Any "Management" option?
- Any "Settings" option?

---

## Alternative: Import via API

If we can't find the UI import, we can do it via command line:

```bash
# Import the dashboard via curl
curl -X POST "https://10.10.10.40/api/saved_objects/dashboard/threat-intelligence-summary" \
  -H "Content-Type: application/json" \
  -d @docs/wazuh-threat-intelligence-dashboard.json
```

But first, let's try to find the UI import option. Can you tell me what's in your left sidebar menu?

