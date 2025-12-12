# Phase 6: n8n Workflow Setup & Configuration

**Status:** Ready for import and configuration

This document covers setting up the automated malware IP blocking workflow in n8n.

## What's Been Completed

✅ **Blocking Script Deployed** - `/usr/local/bin/block-malicious-ip.sh` on Firewalla (10.10.10.1)
✅ **Wazuh Integration** - Webhook configured to send ALARM_INTEL events to n8n
✅ **SSH Authentication** - n8n's SSH key added to Firewalla root authorized_keys
✅ **Connectivity Verified** - n8n can SSH to Firewalla and execute blocking script

## What Needs Configuration

You need to:
1. Import the n8n workflow
2. Configure SSH credentials for n8n
3. Test with a real ALARM_INTEL event

---

## Step 1: Import the Workflow into n8n

### Method A: Via n8n UI (Recommended)

1. **Access n8n:**
   - URL: `https://n8n.ratlm.com` or `http://10.10.10.52:5678`
   - Log in with your credentials

2. **Import the workflow:**
   - Click **"+ Add new"** → **"Import from file"**
   - Upload: `/tmp/n8n-phase6-final-workflow.json`
   - Click **Import**

3. **Verify the workflow structure:**
   - Should see 6 nodes:
     - `Webhook: Wazuh Alert` (entry point)
     - `Extract: IP & Details` (parse alert)
     - `Decision: Critical Alert?` (filter by severity)
     - `Execute: Block on Firewalla` (SSH execution)
     - `Notify: Alert Blocked` (notification)
     - `Log: Low Severity` (non-blocking log)

---

## Step 2: Configure SSH Credentials

The workflow needs SSH credentials to connect to Firewalla.

### In n8n UI:

1. **Create SSH Credential:**
   - Click **Credentials** (bottom left)
   - Click **+ Create New**
   - Search for **"SSH"**
   - Select **"SSH (Key-based Auth)"**

2. **Fill in the details:**
   - **Credential Name:** `Firewalla-SSH-Key`
   - **Host:** `10.10.10.1`
   - **Port:** `22`
   - **Username:** `root`
   - **Private Key:** Paste the contents of n8n's private key:
     ```bash
     # On n8n server (10.10.10.52), get the key:
     ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.52 'cat ~/.ssh/id_rsa_n8n'
     ```
   - Copy the entire key (including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`)
   - Paste into the **Private Key** field in n8n

3. **Test the connection:**
   - Click **Test Connection**
   - Should show: ✅ **Success**

4. **Save** the credential

### In the Workflow:

1. **Open the workflow**
2. **Click the "Execute: Block on Firewalla" node** (the SSH node)
3. **In the right panel:**
   - Under **Credentials:**
     - Select **Firewalla-SSH-Key** from the dropdown
   - Click **Done**

---

## Step 3: Activate the Webhook

The webhook needs to be **listening** for incoming alerts from Wazuh.

1. **In the workflow:**
   - Click the **"Webhook: Wazuh Alert"** node
   - In the right panel, find the webhook URL
   - It should show: `https://n8n.ratlm.com/webhook/wazuh-alert-blocker`
   - Make note of this URL (it's already configured in Wazuh)

2. **Save the workflow:**
   - Click **Save** (or Ctrl+S)

3. **Activate the workflow:**
   - Toggle **Active** switch (top right) to ON
   - The workflow will now listen for incoming Wazuh alerts

---

## Step 4: Test the Workflow

### Automatic Test (Wait for Real Alert)

When Wazuh detects an ALARM_INTEL event with severity ≥7:
1. Wazuh sends webhook POST to n8n
2. n8n extracts the IP
3. n8n SSHes to Firewalla and executes the blocking script
4. IP is added to Firewalla's blocklist and iptables
5. Notification is sent (if configured)

### Manual Test (Simulate Alert)

If you want to test without waiting for a real attack:

```bash
# From any host that can reach n8n:
curl -X POST \
  http://10.10.10.52:5678/webhook/wazuh-alert-blocker \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "alert": {
        "data": {
          "srcip": "192.0.2.100",
          "country": "TEST_COUNTRY",
          "level": 10,
          "destip": "192.168.1.1"
        },
        "rule": {
          "id": "100051"
        }
      }
    }
  }'
```

**Expected response:**
```json
{
  "status": "success",
  "message": "Webhook received"
}
```

**Expected result on Firewalla:**
```bash
ssh root@10.10.10.1 'tail -5 /var/log/malware-blocks.log'
# Should show blocking entry for 192.0.2.100
```

---

## Workflow Logic Explained

### Decision Tree:

```
┌─ Wazuh Alert ────────────────┐
│  (ALARM_INTEL event)          │
└──────────┬────────────────────┘
           │
           ▼
┌─ Extract IP & Details ─────────┐
│  - Source IP (attacker)        │
│  - Country                     │
│  - Severity level              │
│  - Target device               │
└──────────┬────────────────────┘
           │
           ▼
┌─ Is Critical? (Severity ≥7) ──┐
│           YES / NO              │
└───┬──────────────────────┬─────┘
    │ YES (Critical)       │ NO (Low)
    ▼                      ▼
┌─ Execute Block ─┐    ┌─ Log Only ──┐
│ SSH → Firewalla │    │ No blocking │
│ iptables DROP   │    │             │
└─────────────────┘    └─────────────┘
    │
    ▼
┌─ Notify ───────┐
│ Send alert     │
│ (Slack/Email)  │
└────────────────┘
```

### Severity Threshold:

- **≥7 (High/Critical):** IP is **BLOCKED** immediately
- **<7 (Low/Medium):** IP is **LOGGED** but NOT blocked

This prevents alert fatigue from low-severity events while protecting against critical threats.

---

## Troubleshooting

### Webhook not receiving alerts

**Problem:** n8n workflow shows no activity even though Wazuh is running.

**Check:**
```bash
# 1. Verify Wazuh webhook configuration
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'sudo grep -A 5 "n8n" /var/ossec/etc/ossec.conf'

# 2. Check Wazuh integration logs
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'sudo tail -20 /var/ossec/logs/integrations.log'

# 3. Verify n8n webhook is active
# In n8n UI: Check the Webhook node shows "Listening"
```

### SSH connection fails

**Problem:** "Connection refused" or timeout when executing block.

**Check:**
```bash
# 1. Verify SSH connectivity from n8n to Firewalla
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.52 \
  'ssh -i ~/.ssh/id_rsa_n8n root@10.10.10.1 "id"'

# 2. Verify blocking script exists and is executable
ssh root@10.10.10.1 'ls -la /usr/local/bin/block-malicious-ip.sh'

# 3. Check Firewalla SSH logs
ssh brian@10.10.10.1 'sudo tail -20 /var/log/auth.log | grep sshd'
```

### IPs not being blocked

**Problem:** Script runs but IP doesn't appear in blocklist.

**Check:**
```bash
# 1. Verify iptables rules were added
ssh root@10.10.10.1 'iptables -L INPUT -n | grep DROP'

# 2. Verify blocklist database was updated
ssh root@10.10.10.1 'cat /etc/malware-blocklist.txt'

# 3. Check script logs
ssh root@10.10.10.1 'tail -20 /var/log/malware-blocks.log'
```

---

## Files & Locations

| Item | Location |
|------|----------|
| **n8n Workflow JSON** | `/tmp/n8n-phase6-final-workflow.json` |
| **Blocking Script** | `/usr/local/bin/block-malicious-ip.sh` (on Firewalla) |
| **Blocklist Database** | `/etc/malware-blocklist.txt` (on Firewalla) |
| **Block Logs** | `/var/log/malware-blocks.log` (on Firewalla) |
| **n8n SSH Key** | `~/.ssh/id_rsa_n8n` (on n8n server) |
| **Wazuh Config** | `/var/ossec/etc/ossec.conf` (on Wazuh) |
| **Wazuh Integration** | `/var/ossec/integrations/wazuh-webhook-n8n.py` (on Wazuh) |

---

## Security Considerations

### SSH Key Management

- **n8n's private key** (`id_rsa_n8n`) is stored only on the n8n server
- **Public key** is in Firewalla's `root/.ssh/authorized_keys`
- No key material is stored in n8n credentials (uses reference)

### Firewall Access

- n8n connects to Firewalla on **port 22 (SSH)** only
- Firewalla executes **only** the blocking script
- No password authentication (key-based only)

### Alert Filtering

- Only **severity ≥7** events trigger blocking
- Low-severity events are logged for audit trail
- No false-positive blocking of legitimate traffic

---

## Next Steps After Setup

1. **Monitor** - Watch n8n execution logs for first real alert
2. **Test** - Send manual test webhook to verify flow
3. **Tune** - Adjust severity threshold if needed
4. **Future: DNS Blocking** - Implement Phase 7 permanent blocklist (separate project)

---

## Commands Quick Reference

```bash
# Test n8n SSH to Firewalla
ssh -i ~/.ssh/id_rsa_n8n root@10.10.10.1 'id'

# View blocked IPs
cat /etc/malware-blocklist.txt

# Test blocking script manually
/usr/local/bin/block-malicious-ip.sh 203.45.67.89 TestCountry

# Check iptables rules
iptables -L INPUT -n | grep DROP

# View block logs
tail -f /var/log/malware-blocks.log
```

---

**Status:** Phase 6 ready for testing. Once workflow is imported and credentials configured, system will automatically block malicious IPs detected by Wazuh.

**Last Updated:** November 17, 2025
