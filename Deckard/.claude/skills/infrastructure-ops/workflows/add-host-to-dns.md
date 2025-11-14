---
name: add-host-to-dns
description: |
  Add a new host to the DNS system (.lan domain) in BIND9 primary and propagate to Pi-hole caches.
  USE WHEN user asks to: add host to DNS, add DNS record, add domain entry, register hostname
---

# Add Host to DNS Workflow

## What This Does

Adds a new hostname with IP address to the .lan domain in BIND9 primary DNS server (10.10.10.4), updates the zone serial number, and ensures Pi-hole DNS caches are cleared so all clients can resolve the new hostname immediately.

---

## Prerequisites

- Hostname to add (e.g., "ansible")
- IP address to assign (e.g., "10.10.10.30")
- SSH access to BIND9 primary (10.10.10.4)
- SSH access to both Pi-hole instances (10.10.10.22 and 10.10.10.23)
- Sudo/root access on all DNS servers

---

## Execution Steps

### Step 1: Add Record to BIND9 Zone File

Connect to BIND9 primary (10.10.10.4) and edit the lan zone file:

```bash
ssh brian@10.10.10.4 "sudo python3 << 'PYEOF'
import re

# Read the zone file
with open('/etc/bind/zones/db.lan', 'r') as f:
    content = f.read()

# Find insertion point (before 'Add more hosts' comment)
insert_point = content.find('; Add more hosts here')

# Create the new A record
new_record = 'HOSTNAME         IN      A       IP_ADDRESS\n'
new_record = new_record.replace('HOSTNAME', 'ansible')
new_record = new_record.replace('IP_ADDRESS', '10.10.10.30')

# Insert the record
content = content[:insert_point] + new_record + '\n' + content[insert_point:]

# Update serial number (YYYYMMDDNN format)
old_serial = re.search(r'(\d{10})', content)
if old_serial:
    old_num = old_serial.group(1)
    date_part = old_num[:8]
    nn_part = int(old_num[8:]) + 1
    new_serial = f'{date_part}{nn_part:02d}'
    content = content.replace(old_num, new_serial, 1)
    print(f'Updated serial: {old_num} -> {new_serial}')

# Write back to file
with open('/etc/bind/zones/db.lan', 'w') as f:
    f.write(content)

print(f'Added DNS record: HOSTNAME IN A IP_ADDRESS')
PYEOF
"
```

**What this does:**
- Reads current zone file
- Adds new A record in correct format
- Increments serial number (CRITICAL - must happen for secondary servers to update)
- Writes updated file back

### Step 2: Reload BIND9 to Activate Changes

```bash
ssh brian@10.10.10.4 "sudo rndc reload"
```

**Expected output:** `server reload successful`

### Step 3: Verify BIND9 Can Resolve the New Record

```bash
dig @10.10.10.4 HOSTNAME.lan +short
```

Should return the IP address. Example:
```
10.10.10.30
```

### Step 4: Clear Pi-hole DNS Caches

This is the CRITICAL step that many forget! Pi-hole caches negative responses (NXDOMAIN) from BIND9. When you add a new record, Pi-hole still returns the old negative response until its cache is cleared.

**Restart Pi-hole Primary (10.10.10.22):**
```bash
ssh brian@10.10.10.22 "sudo systemctl restart pihole-FTL && sleep 3 && echo 'Pi-hole Primary cache cleared'"
```

**Restart Pi-hole Secondary (10.10.10.23):**
```bash
ssh brian@10.10.10.23 "sudo systemctl restart pihole-FTL && sleep 3 && echo 'Pi-hole Secondary cache cleared'"
```

### Step 5: Verify Resolution from Client Hosts

Test from a host that uses Pi-hole for DNS (most clients do):

```bash
# From any client using Pi-hole DNS (e.g., ser8 at 10.10.10.96)
ssh brian@10.10.10.96 "ping -c 3 HOSTNAME.lan"
```

Should resolve and ping successfully. Example:
```
PING ansible.lan (10.10.10.30) 56(84) bytes of data.
64 bytes from 10.10.10.30: icmp_seq=1 ttl=64 time=2.22 ms
```

---

## How It Works: The DNS Architecture

Your DNS system has this hierarchy:

```
┌─────────────────────────────────────┐
│  BIND9 Primary (10.10.10.4)         │
│  Zone: db.lan                       │
│  Authority for .lan domain          │
└──────┬────────────────────────┬─────┘
       │                        │
       │ Forwards .lan queries  │
       │                        │
┌──────▼──────────┐   ┌────────▼──────────┐
│ Pi-hole Primary │   │ Pi-hole Secondary  │
│ (10.10.10.22)  │   │ (10.10.10.23)      │
│                │   │                    │
│ Caches results │   │ Caches results     │
│ Blocks ads     │   │ Blocks ads         │
└────┬───────────┘   └───────┬────────────┘
     │                       │
     └───────────┬───────────┘
                 │
         ┌───────▼────────┐
         │ Client Hosts   │
         │ (ser8, etc)    │
         │ Query Pi-hole  │
         └────────────────┘
```

**Key points:**
- BIND9 is the authoritative source for .lan zones
- Pi-hole forwards unknown queries to BIND9 and caches results
- Clients use Pi-hole (via DHCP or static config) for DNS
- Pi-hole ALSO blocks ads based on blocklists

**The caching issue:**
When BIND9 doesn't have a record, it returns NXDOMAIN (not found). Pi-hole caches this negative response. When you ADD the record to BIND9, Pi-hole still returns NXDOMAIN from its cache until restarted.

---

## Real-World Example: Adding Ansible Server

**Scenario:** New Ansible control server at 10.10.10.30 needs DNS entry

**Step-by-step:**

```bash
# 1. Add to BIND9
ssh brian@10.10.10.4 "sudo python3 << 'PYEOF'
import re
with open('/etc/bind/zones/db.lan', 'r') as f:
    content = f.read()
insert_point = content.find('; Add more hosts here')
content = content[:insert_point] + 'ansible         IN      A       10.10.10.30\n\n' + content[insert_point:]
old_serial = re.search(r'(\d{10})', content)
if old_serial:
    old_num = old_serial.group(1)
    new_serial = f'{old_num[:8]}{int(old_num[8:])+1:02d}'
    content = content.replace(old_num, new_serial, 1)
with open('/etc/bind/zones/db.lan', 'w') as f:
    f.write(content)
print('Added ansible A record')
PYEOF
"

# 2. Reload BIND9
ssh brian@10.10.10.4 "sudo rndc reload"

# 3. Verify BIND9 has it
dig @10.10.10.4 ansible.lan +short
# Output: 10.10.10.30

# 4. Clear Pi-hole caches (CRITICAL!)
ssh brian@10.10.10.22 "sudo systemctl restart pihole-FTL"
ssh brian@10.10.10.23 "sudo systemctl restart pihole-FTL"

# 5. Test from client
ssh brian@10.10.10.96 "ping -c 3 ansible.lan"
# Should succeed with 0% packet loss
```

---

## Troubleshooting

### Problem: New Host Can't Be Resolved from Client Machines

**Symptom:** `ping HOSTNAME.lan` returns "Name or service not known" even though BIND9 has the record

**Diagnosis Steps:**

1. **Verify BIND9 has the record:**
   ```bash
   dig @10.10.10.4 HOSTNAME.lan +short
   ```
   Should return IP address

2. **Verify BIND9 reloaded successfully:**
   ```bash
   ssh brian@10.10.10.4 "sudo journalctl -u named -n 20"
   ```
   Look for "zone reload successful" or errors

3. **Test direct query to Pi-hole:**
   ```bash
   dig @10.10.10.22 HOSTNAME.lan
   ```
   If this returns NXDOMAIN, Pi-hole cache is stale

4. **Clear Pi-hole caches and retry:**
   ```bash
   ssh brian@10.10.10.22 "sudo systemctl restart pihole-FTL && sleep 3"
   ssh brian@10.10.10.23 "sudo systemctl restart pihole-FTL && sleep 3"
   dig @10.10.10.22 HOSTNAME.lan +short
   ```
   Should now return IP address

### Problem: Serial Number Not Incrementing

**Symptom:** Zone serial stays the same despite changes

**Cause:** Python regex failed to match the serial number format

**Solution:** Check zone file format - serial must be 10 digits (YYYYMMDDNN):
```bash
ssh brian@10.10.10.4 "sudo grep -A 3 'SOA' /etc/bind/zones/db.lan | head -5"
```

Should show something like:
```
@       IN      SOA     dns1.lan. admin.lan. (
                        2025110306         ; Serial (YYYYMMDDNN)
```

If the format is different, manually update the serial before running the add script.

### Problem: Pi-hole Not Forwarding to BIND9

**Symptom:** Queries to Pi-hole time out or return refused

**Cause:** Forwarding configuration broken or Pi-hole service crashed

**Solution:** Check Pi-hole forwarding config:
```bash
ssh brian@10.10.10.22 "sudo cat /etc/dnsmasq.d/03-lan-bind9.conf"
```

Should contain:
```
server=/lan/10.10.10.4
server=/lan/10.10.10.2
```

If missing, check other dnsmasq config files:
```bash
ssh brian@10.10.10.22 "sudo ls /etc/dnsmasq.d/"
```

### Problem: Can Resolve from BIND9 but Not from Client

**Symptom:** `dig @10.10.10.4 HOSTNAME.lan` works but client ping fails

**Diagnosis:** Client is using wrong DNS server

Check client DNS configuration:
```bash
ssh brian@CLIENT_IP "resolvectl status | grep 'DNS Server'"
```

If it shows something other than 10.10.10.22/10.10.10.23:
- Check DHCP configuration on Firewalla
- Verify client's static DNS settings
- Restart client's DNS resolver: `sudo systemctl restart systemd-resolved`

---

## Common Mistakes to Avoid

1. **❌ Forgetting to increment serial number**
   - Secondary DNS servers won't update zone
   - Zone transfers fail silently
   - **Always increment YYYYMMDDNN**

2. **❌ Not reloading BIND9 after editing**
   - Changes won't take effect
   - Old zone still in memory
   - **Always run `sudo rndc reload`**

3. **❌ Not clearing Pi-hole caches**
   - Most common cause of "can't resolve" issues
   - Pi-hole caches negative responses (NXDOMAIN)
   - **Always restart pihole-FTL on both instances**

4. **❌ Testing from wrong DNS server**
   - Testing `dig @10.10.10.4` works but client still fails
   - Client might be using different DNS server
   - **Always test from actual client machines**

5. **❌ Wrong zone file location**
   - Using `/etc/bind/db.lan` instead of `/etc/bind/zones/db.lan`
   - Changes appear to work but don't persist
   - **Always use full path: `/etc/bind/zones/db.lan`**

---

## DNS Record Format Reference

The A record format is:
```
HOSTNAME    IN      A       IP_ADDRESS
```

**Field meanings:**
- `HOSTNAME`: The name clients use (e.g., "ansible", "plex", "checkmk")
- `IN`: Internet class (always this for .lan)
- `A`: Address record type (IPv4)
- `IP_ADDRESS`: The IPv4 address (e.g., "10.10.10.30")

**Spacing note:** Use tabs or spaces to align, but ensure at least one whitespace between fields.

---

## Integration with Other Systems

- **Checkmk monitoring**: Add hostname to hosts.mk and DNS together
- **Pi-hole ad-blocking**: Hostnames added to DNS are automatically available
- **DHCP**: Firewalla DHCP can assign to these hostnames
- **Reverse DNS (PTR)**: See `db.10.10.10` file for reverse lookups

---

## Key Decisions for Deckard

1. **Always update serial number** - Zone synchronization depends on it
2. **Always restart both Pi-hole instances** - Both are active and both cache
3. **Test from clients, not from BIND9** - Clients use Pi-hole, not BIND9 directly
4. **Verify connectivity before DNS** - Ensure IP address is reachable
5. **Document additions** - Keep track of which hosts added when and why

---

## Zone File Location Reference

| Server | Zone File | Purpose |
|--------|-----------|---------|
| BIND9 Primary (10.10.10.4) | `/etc/bind/zones/db.lan` | Main .lan domain authority |
| BIND9 Primary (10.10.10.4) | `/etc/bind/zones/db.10.10.10` | Reverse DNS (PTR records) |
| Pi-hole Primary (10.10.10.22) | `/etc/dnsmasq.d/03-lan-bind9.conf` | Forwarding config (don't edit) |
| Pi-hole Secondary (10.10.10.23) | `/etc/dnsmasq.d/03-lan-bind9.conf` | Forwarding config (don't edit) |

---

**Last Updated:** November 14, 2025
**Status:** Complete - Tested and Working
**Lesson Learned:** Pi-hole DNS cache clearing is critical - many issues are caused by stale caches

