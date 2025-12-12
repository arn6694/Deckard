# Manual Dashboard Import - Step by Step

Since we're having difficulty with the API, let's use the manual UI import method which is reliable.

## You're Already in the Right Place!

Looking at your second screenshot, you're in the "**Editing New Dashboard**" view. This is perfect!

## How to Import Dashboard

### Option A: Using the "Add" button in your current screen

1. **You're in Dashboard Edit mode** - Perfect!
2. Look for: **"Add"** button at the top (next to "Options", "Share", "Cancel", "Save")
3. Click: **"Add"**
4. This should open an import/add dialog

### Option B: Go back and use Dashboards menu

1. Click: **"Dashboards"** link at the top (left side where it says "Dashboards" / "Editing New Dashboard")
2. This takes you back to dashboard list
3. Look for: **"Import"** button or icon
4. Or: Look for a **three-dot menu** (⋮) icon

### Option C: Use the left sidebar

1. Look at the **left sidebar** (might need to click hamburger menu ☰)
2. Find: **"Management"** or **"Admin"**
3. Look for: **"Saved Objects"**
4. Click: **"Import"**

---

## If None of Those Work

Try accessing management directly via URL:
```
https://10.10.10.40/app/management/opensearch_dashboards/objects
```

Or:
```
https://10.10.10.40/app/dev_tools
```

---

## Once You Find Import

1. Click: **Import**
2. Drag and drop OR click to select: `docs/wazuh-threat-intelligence-dashboard.json`
3. Click: **Import**
4. Wait for confirmation
5. Go to: Dashboards
6. Find: "Threat Intelligence Summary"
7. Click: Open

---

## What Should Happen

After importing:
- Dashboard appears in dashboard list
- All 6 widgets will be visible
- Data from Wazuh alerts will populate the visualizations
- Dashboard updates every 5 minutes automatically

---

## Can You Help Me Locate Import?

Can you tell me:

1. **In your current "Editing New Dashboard" screen** (the second image), do you see any buttons or menus at the top?
   - What text/buttons do you see?

2. **In the left sidebar**, when you click the hamburger menu (☰), what options appear?
   - List them for me

3. **Are there any other pages/tabs** you can access before you went to "Create new dashboard"?

Once I know what's visible, I can guide you directly to the import function!

