# Homelab Infrastructure Topology

## Network Overview

**Network**: 10.10.10.0/24 (255 hosts, locally managed)
**Gateway**: 10.10.10.1 (Firewalla firewall)
**Management**: Proxmox 10.10.10.17

---

## Core Components

### Monitoring & Observability

#### Checkmk
- **IP**: 10.10.10.5
- **Role**: Enterprise monitoring and alerting
- **Version**: Checkmk 2.4
- **Web UI**: https://checkmk.ratlm.com
- **API Endpoint**: https://checkmk.ratlm.com/monitoring/live
- **Capabilities**:
  - Real-time host and service status
  - Performance metrics collection
  - Alert generation and acknowledgement
  - Custom checks and diagnostics
  - Historical trend analysis
- **Monitored Systems**: All infrastructure hosts via Checkmk agents
- **Access Method**: SSH to host + API calls for queries

---

### DNS Infrastructure

#### BIND9 Primary (Authoritative)
- **IP**: 10.10.10.4
- **Hosted On**: Proxmox LXC 119
- **OS**: Debian Linux
- **Role**: Primary DNS server, zone authority
- **Zone Files**: `/etc/bind/zones/`
- **Main Zone**: `ratlm.com` and local network zones
- **Zone Transfer**: Sends zone updates to secondary (10.10.10.2)
- **Management Commands**:
  - Check syntax: `named-checkzone <zone> /etc/bind/zones/db.<zone>`
  - Reload zones: `sudo rndc reload`
  - Zone status: `sudo rndc zonestatus <zone>`
  - View config: `/etc/bind/named.conf`
- **SSH Access**: `brian@10.10.10.4`

#### BIND9 Secondary (Slave)
- **IP**: 10.10.10.2
- **Hosted On**: Zeus Docker (external system)
- **Role**: Secondary DNS server for redundancy
- **Receives**: Zone transfers from primary (10.10.10.4)
- **Update Method**: Automatic zone transfer from primary
- **Failover**: Takes over if primary becomes unavailable
- **SSH Access**: `brian@10.10.10.2`

---

### DNS Filtering & Ad-Blocking

#### Pi-hole Primary
- **IP**: 10.10.10.22
- **Hosted On**: Proxmox LXC 105
- **Role**: DNS filtering, ad-blocking, DNS caching
- **Web UI**: http://10.10.10.22/admin
- **API Endpoint**: http://10.10.10.22/admin/api.php
- **Capabilities**:
  - Query logging and statistics
  - Whitelist/blacklist management (gravity)
  - Adlist management
  - DHCP server (optional)
  - Network-wide DNS resolution
- **Replication**: Settings sync to secondary (10.10.10.23)
- **Default Upstream DNS**: Can fall back to public DNS if needed

#### Pi-hole Secondary
- **IP**: 10.10.10.25
- **Hosted On**: pi5 (Raspberry Pi 5)
- **Role**: Redundant Pi-hole instance, secondary DNS filtering
- **OS**: Debian 13 (Trixie) aarch64
- **Web UI**: http://10.10.10.25/admin/
- **Configuration**: Synchronized from primary
- **Failover**: Provides DNS filtering if primary (10.10.10.22) is down
- **Status**: Operational as of November 14, 2025

---

### Reverse Proxy & SSL/TLS

#### Nginx Proxy Manager
- **IP**: 10.10.10.3
- **Role**: Reverse proxy for external access, SSL/TLS termination
- **Web UI**: https://10.10.10.3 (admin interface)
- **Managed Domains**:
  - `checkmk.ratlm.com` → proxies to Checkmk (10.10.10.5)
  - Other services as configured
- **Features**:
  - Automatic SSL certificate management (Let's Encrypt)
  - Access logs for troubleshooting
  - Proxy host configuration
  - Custom headers and redirects
- **Certificates**: Stored and renewed via Let's Encrypt
- **SSH Access**: Available for advanced configuration

---

### Virtualization Platform

#### Proxmox
- **IP**: 10.10.10.17
- **Role**: Hypervisor for virtual machines and LXC containers
- **Web UI**: https://10.10.10.17:8006
- **Managed Systems**:
  - LXC 119: BIND9 Primary DNS (10.10.10.4)
  - LXC 105: Pi-hole Primary (10.10.10.22)
  - Other VMs and containers as configured
- **Features**:
  - VM and LXC lifecycle management
  - Resource allocation and monitoring
  - Backup management
  - Storage management (local and networked)
- **SSH Access**: Available for management and troubleshooting

---

### Local AI Backend

#### Jarvis (Ollama + OpenWebUI)
- **IP**: 10.10.10.49
- **OS**: Ubuntu 24.04 LTS
- **Hardware**:
  - GPU: NVIDIA RTX 3050 (6GB VRAM)
  - RAM: 23GB
  - Storage: 98GB
- **Services**:
  - **Ollama**: Local LLM inference engine
    - Port: 11434 (API)
    - Models: Mistral 7B (4.4GB), Qwen2.5 7B (4.7GB)
    - Purpose: Local model inference without external API dependency
  - **OpenWebUI**: Web chat interface
    - Port: 3000
    - URL: http://10.10.10.49:3000
    - Purpose: Interactive chat with local models
- **Integration with Deckard**: Provides local LLM capabilities for offline-first operation

---

### Home Automation

#### Home Assistant
- **IP**: 10.10.10.6
- **Role**: Home automation hub and integration platform
- **Integration**: Monitored via Checkmk for operational status
- **Capabilities**: Automation scripts, device control, sensor data collection

---

## Network Services Summary

| Service | IP | Role | Primary Tool |
|---------|----|----|---|
| Firewalla | 10.10.10.1 | Gateway/Firewall | Web UI |
| BIND9 Secondary | 10.10.10.2 | DNS Failover | SSH/rndc |
| Nginx PM | 10.10.10.3 | Reverse Proxy | Web UI/SSH |
| BIND9 Primary | 10.10.10.4 | DNS Authority | SSH/rndc |
| Checkmk | 10.10.10.5 | Monitoring | Web UI/API |
| Home Assistant | 10.10.10.6 | Automation | Web UI |
| Proxmox | 10.10.10.17 | Hypervisor | Web UI/SSH |
| Pi-hole Primary | 10.10.10.22 | DNS Filter | API/Web UI |
| **Pi-hole Secondary** | **10.10.10.25** | **DNS Filter (Failover)** | **Web UI/SSH (pi5)** |
| Jarvis | 10.10.10.49 | AI Backend | API/OpenWebUI |

---

## Communication Flows

### Infrastructure Monitoring Flow
```
Checkmk (10.10.10.5)
  ├─ Queries host status via agents
  ├─ Collects metrics periodically
  └─ Generates alerts on thresholds
```

### DNS Resolution Flow
```
Client Query
  ├─ Pi-hole Filter (10.10.10.22/23)
  │   ├─ Filters ads/malware
  │   └─ Caches results
  └─ BIND9 Primary (10.10.10.4)
      ├─ Resolves from zones
      └─ Falls back to upstream if needed
```

### External Access Flow
```
Internet Request → Nginx PM (10.10.10.3)
  └─ SSL Termination
  └─ Route to backend service
    └─ Checkmk UI (10.10.10.5)
    └─ Other services as configured
```

### Virtualization Management
```
Proxmox (10.10.10.17)
  ├─ Manages LXC 119 (BIND9)
  ├─ Manages LXC 105 (Pi-hole)
  └─ Resource allocation & monitoring
```

---

## Access Methods

### SSH Access
- **Primary Gateway**: brian@10.10.10.4 (BIND9 Primary)
- **Secondary DNS**: brian@10.10.10.2 (BIND9 Secondary)
- **Proxmox**: brian@10.10.10.17
- **Jarvis**: brian@10.10.10.49

### Web Interfaces
- **Checkmk**: https://checkmk.ratlm.com
- **Nginx PM**: https://10.10.10.3
- **Proxmox**: https://10.10.10.17:8006
- **Pi-hole**: http://10.10.10.22/admin
- **OpenWebUI**: http://10.10.10.49:3000

### API Endpoints
- **Checkmk API**: https://checkmk.ratlm.com/monitoring/live
- **Ollama API**: http://10.10.10.49:11434
- **Pi-hole API**: http://10.10.10.22/admin/api.php

---

## Redundancy & Failover

### DNS Redundancy
- BIND9 Primary (10.10.10.4) → Secondary (10.10.10.2) via zone transfer
- If primary fails, secondary serves zones
- Firewall rules direct queries to secondary automatically

### DNS Filtering Redundancy
- Pi-hole Primary (10.10.10.22) → Secondary (10.10.10.23) config sync
- If primary fails, secondary continues filtering
- Network can fall back to BIND9 directly if both Pi-holes fail

### Monitoring Continuity
- Checkmk runs on primary system
- If Checkmk fails, manual troubleshooting needed
- Historical data preserved in Checkmk database

### Service Dependencies
```
Critical Chain:
  Network (Firewalla)
    └─ DNS (BIND9 + Pi-hole)
      └─ Other services
```

---

## Performance Characteristics

### Network Bandwidth
- DNS queries: <1ms latency (local network)
- API calls: <100ms typical
- Checkmk queries: <500ms typical
- Ollama inference: Depends on model (local, variable)

### Storage
- Checkmk metrics: ~1-5GB per week (depends on monitored systems)
- BIND9 zones: <1MB typical
- Pi-hole logs: Configurable retention
- Proxmox VMs/LXCs: Varies by workload

### CPU/Memory
- Checkmk: Monitor via Proxmox
- BIND9: Minimal (<100MB)
- Pi-hole: ~200-500MB depending on query load
- Jarvis Ollama: GPU usage when processing

---

## Notes & Considerations

1. **Single Point of Failure**: Checkmk has no redundancy - if it fails, monitoring goes down
2. **DNS Criticality**: DNS is critical - both BIND9 and Pi-hole have redundancy
3. **Local LLM**: Jarvis provides local inference - privacy and reliability advantage
4. **Oracle Linux 7**: Some servers may have older Linux versions requiring older commands
5. **Proxmox Management**: LXCs and VMs managed centrally, but have independent IP addresses

---

## Recent Updates

- **November 14, 2025**: Pi-hole Secondary (pihole2) migrated from Zeus Docker (10.10.10.23) to pi5 (10.10.10.25)
  - New hardware: Raspberry Pi 5 with Debian 13 (aarch64)
  - Web UI now at http://10.10.10.25/admin/
  - DNS fully operational on port 53 with all local configurations
  - Provides DNS failover if primary pihole (10.10.10.22) becomes unavailable

---

**Last Updated**: November 14, 2025
**Status**: Phase 1 Complete - pihole2 migration complete
