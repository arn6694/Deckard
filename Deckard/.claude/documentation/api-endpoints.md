# API Endpoints Reference

This file documents all API endpoints available in the homelab infrastructure.

---

## Checkmk API

### Basics
- **Host**: 10.10.10.5
- **URL**: https://checkmk.ratlm.com/monitoring/live
- **Protocol**: REST API via livestatus protocol
- **Authentication**: API token required (stored in ~/.env as CHECKMK_TOKEN)
- **TLS**: HTTPS (self-signed or certificate)

### API Format

The Checkmk livestatus API uses a simple text protocol:

```
GET <table>
Columns: <column1> <column2> ...
Filter: <column> <operator> <value>
And: <additional conditions>
```

### Common Tables

#### GET hosts
Returns all monitored hosts and their current state.

**Columns Available**:
- `name` - Host name
- `state` - Host state (0=UP, 1=DOWN, 2=UNREACHABLE)
- `last_check` - Timestamp of last check
- `check_type` - Check method (active/passive)
- `plugin_output` - Status message
- `perf_data` - Performance data
- `acknowledged` - Alert acknowledged status
- `custom_variables` - Custom host variables

**Example Query**:
```bash
curl -s "https://checkmk.ratlm.com/monitoring/live" \
  -H "Accept: application/json" \
  --data "GET hosts
Columns: name state plugin_output last_check
Filter: state != 0"
```

#### GET services
Returns services for monitored hosts.

**Columns Available**:
- `host_name` - Host the service runs on
- `service_description` - Service name
- `state` - Service state (0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN)
- `plugin_output` - Status message
- `perf_data` - Performance metrics
- `last_check` - Timestamp of last check
- `check_period` - Maintenance window info
- `is_flapping` - Service is flapping
- `acknowledged` - Alert acknowledged

**Example Query**:
```bash
curl -s "https://checkmk.ratlm.com/monitoring/live" \
  --data "GET services
Columns: host_name service_description state plugin_output
Filter: state != 0"
```

#### GET hostgroups
Returns host group membership.

**Columns Available**:
- `name` - Host group name
- `members` - Hosts in group (comma-separated)
- `description` - Host group description

#### GET servicegroups
Returns service group membership.

**Columns Available**:
- `name` - Service group name
- `members` - Services in group
- `description` - Service group description

### Advanced Operations

#### Acknowledge Alert
```bash
COMMAND [timestamp] ACKNOWLEDGE_HOST_PROBLEM;hostname;sticky;notify;user;comment
```

#### Get Metrics
Include `perf_data` in columns to get performance metrics, then parse:
```
metric_name=value[unit];warn;crit;min;max
```

### Authentication
Store API token in `~/.env`:
```
CHECKMK_TOKEN=your-api-token-here
```

Use in curl with header (if required):
```bash
curl -H "Authorization: Bearer $CHECKMK_TOKEN" ...
```

---

## BIND9 DNS Management

### Primary Server (10.10.10.4)

**SSH Access**: `brian@10.10.10.4`

**Zone Files Location**: `/etc/bind/zones/`

**Configuration**: `/etc/bind/named.conf`, `/etc/bind/named.conf.local`

### Common Operations

#### Check Zone Syntax
```bash
named-checkzone <zone-name> <zone-file-path>
```

Example:
```bash
named-checkzone ratlm.com /etc/bind/zones/db.ratlm.com
```

#### Reload All Zones
```bash
sudo rndc reload
```

#### Reload Specific Zone
```bash
sudo rndc reload <zone-name>
```

#### Get Zone Status
```bash
sudo rndc zonestatus <zone-name>
```

#### Flush Cache (if applicable)
```bash
sudo rndc flush
```

#### View Current Zones
```bash
sudo rndc status
```

### Zone File Format

Standard BIND9 zone file format:

```
$TTL 3600
@   IN  SOA ns1.ratlm.com. admin.ratlm.com. (
                2025111301  ; Serial
                3600        ; Refresh
                1800        ; Retry
                604800      ; Expire
                86400 )     ; Minimum TTL
    IN  NS  ns1.ratlm.com.
    IN  NS  ns2.ratlm.com.

ns1     IN  A   10.10.10.4
ns2     IN  A   10.10.10.2
host    IN  A   10.10.10.50
service IN  CNAME host.ratlm.com.
mail    IN  A   10.10.10.51
        IN  MX  10  mail.ratlm.com.
```

### Verification

Test DNS resolution:
```bash
dig @10.10.10.4 hostname.ratlm.com +short
```

Test DNS secondary:
```bash
dig @10.10.10.2 hostname.ratlm.com +short
```

### Secondary Server (10.10.10.2)

**SSH Access**: `brian@10.10.10.2`

**Receives**: Automatic zone transfers from primary

**Operations**: Same rndc commands work on secondary

---

## Pi-hole API

### Primary Instance (10.10.10.22)

**Base URL**: `http://10.10.10.22/admin/api.php`

**Authentication**: Optional API token (configurable in Pi-hole settings)

**Secondary**: `http://10.10.10.23/admin/api.php`

### Common Endpoints

#### Get Summary Stats
```bash
curl -s "http://10.10.10.22/admin/api.php?summary"
```

Returns:
- `domains_being_blocked` - Active adlists
- `dns_queries_today` - Query count
- `ads_blocked_today` - Blocked count
- `ads_percentage_today` - Block percentage
- `unique_domains` - Unique domains queried

#### Get Query Statistics
```bash
curl -s "http://10.10.10.22/admin/api.php?stats=10m"
```

Returns: Queries in last 10 minutes aggregated

Options: `10m`, `1h`, `24h`

#### Get Gravity (Adlists)
```bash
curl -s "http://10.10.10.22/admin/api.php?gravity"
```

Returns: List of all enabled adlists

#### Add Whitelist Entry
```bash
curl -s "http://10.10.10.22/admin/api.php?whitelist=add&domain=example.com"
```

#### Add Blacklist Entry
```bash
curl -s "http://10.10.10.22/admin/api.php?blacklist=add&domain=badsite.com"
```

#### Get Client List
```bash
curl -s "http://10.10.10.22/admin/api.php?getClient"
```

#### Enable/Disable DNS
```bash
# Disable (requires token)
curl -s "http://10.10.10.22/admin/api.php?disable&auth=$PIHOLE_TOKEN"

# Enable (requires token)
curl -s "http://10.10.10.22/admin/api.php?enable&auth=$PIHOLE_TOKEN"
```

#### Get Gravity ID
```bash
curl -s "http://10.10.10.22/admin/api.php?getGravity"
```

### Authentication
If Pi-hole has API token enabled:
```
curl -s "http://10.10.10.22/admin/api.php?summary&auth=$PIHOLE_TOKEN"
```

Store token in `~/.env`:
```
PIHOLE_TOKEN=your-token-here
```

### Replication Status
Check if secondary is synchronized:
```bash
curl -s "http://10.10.10.23/admin/api.php?summary"
```

Compare `gravity` output between primary and secondary.

---

## Nginx Proxy Manager API

### URL
`https://10.10.10.3/api/`

### Authentication
Username/password or token-based (check Nginx PM settings)

### Common Endpoints

#### List Proxy Hosts
```bash
GET /api/nginx/proxy-hosts
```

#### Get Proxy Host Details
```bash
GET /api/nginx/proxy-hosts/{id}
```

#### Create Proxy Host
```bash
POST /api/nginx/proxy-hosts
```

#### Update Proxy Host
```bash
PUT /api/nginx/proxy-hosts/{id}
```

#### Delete Proxy Host
```bash
DELETE /api/nginx/proxy-hosts/{id}
```

#### List SSL Certificates
```bash
GET /api/ssl/certificates
```

#### Renew Certificate
```bash
PUT /api/ssl/certificates/{id}/renew
```

#### View Access Log
```bash
GET /api/nginx/logs
```

### Web UI
Access directly at: `https://10.10.10.3`

---

## Proxmox API

### URL
`https://10.10.10.17:8006/api2/json/`

### Authentication
Ticket-based or token-based authentication

### Common Endpoints

#### List Nodes
```bash
GET /nodes
```

#### List VMs
```bash
GET /nodes/{node}/qemu
```

#### List LXCs
```bash
GET /nodes/{node}/lxc
```

#### Get Container Status
```bash
GET /nodes/{node}/lxc/{vmid}/status/current
```

#### Start Container
```bash
POST /nodes/{node}/lxc/{vmid}/status/start
```

#### Stop Container
```bash
POST /nodes/{node}/lxc/{vmid}/status/stop
```

#### Get Container Details
```bash
GET /nodes/{node}/lxc/{vmid}/config
```

### Web UI
Access at: `https://10.10.10.17:8006`

### Authentication
Create API token in Proxmox → Permissions → API Tokens

Store in `~/.env`:
```
PROXMOX_USER=user@pam
PROXMOX_TOKEN_ID=token-id
PROXMOX_TOKEN_SECRET=token-secret
```

---

## Ollama API (Jarvis Local LLM)

### URL
`http://10.10.10.49:11434`

### Common Endpoints

#### Generate (Streaming)
```bash
POST /api/generate
```

Request:
```json
{
  "model": "mistral",
  "prompt": "What is the status of the system?",
  "stream": true
}
```

#### Generate (Non-streaming)
Same endpoint with `"stream": false`

#### List Models
```bash
GET /api/tags
```

Response: List of available models

#### Show Model Info
```bash
POST /api/show
```

Request:
```json
{
  "name": "mistral"
}
```

#### Pull Model
```bash
POST /api/pull
```

Request:
```json
{
  "name": "mistral:latest"
}
```

### Models Available
- `mistral` (Mistral 7B)
- `qwen2.5` (Qwen2.5 7B)

### Web Interface
Access at: `http://10.10.10.49:3000` (OpenWebUI)

---

## Testing APIs

### Checkmk API Test
```bash
curl -s "https://checkmk.ratlm.com/monitoring/live" \
  -H "Accept: application/json" \
  -k \
  --data "GET hosts
Columns: name state" | head -20
```

### BIND9 Test
```bash
dig @10.10.10.4 localhost +short
dig @10.10.10.2 localhost +short
```

### Pi-hole Test
```bash
curl -s "http://10.10.10.22/admin/api.php?summary" | jq '.'
```

### Ollama Test
```bash
curl -s "http://10.10.10.49:11434/api/tags" | jq '.'
```

---

## Credential Storage

Store all API tokens and credentials in `~/.env`:

```bash
# Checkmk
CHECKMK_TOKEN=your-token

# Pi-hole
PIHOLE_TOKEN=your-token

# Proxmox
PROXMOX_USER=user@pam
PROXMOX_TOKEN_ID=id
PROXMOX_TOKEN_SECRET=secret

# Nginx PM
NGINX_PM_USER=admin
NGINX_PM_PASSWORD=password

# Ollama (if authentication required)
OLLAMA_API_KEY=your-key
```

**IMPORTANT**: Never commit `~/.env` to version control. Add to `.gitignore`.

---

**Last Updated**: November 13, 2025
**Status**: Phase 1 Documentation Complete
