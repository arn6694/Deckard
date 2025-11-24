# NetBox Installation Guide for Oracle Linux

**Last Updated:** 2025-11-24
**Tested On:** Oracle Linux 8 with NetBox v3.7.8
**Status:** Production-ready, all issues resolved

This guide provides **complete, tested** step-by-step instructions for installing NetBox on Oracle Linux 8 or 9. This guide was created after resolving all real-world installation issues on Elliott's infrastructure.

---

## Important Notes Before Starting

⚠️ **Corporate Network Users:** If you're behind a corporate proxy, you'll need proxy configuration (covered in Step 2).

⚠️ **Version Matching is Critical:** This guide addresses the "perfect storm" of version dependencies between Oracle Linux, PostgreSQL, Python, and NetBox.

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [System Preparation & Proxy Configuration](#2-system-preparation--proxy-configuration)
3. [PostgreSQL Database Setup](#3-postgresql-database-setup)
4. [Redis Setup](#4-redis-setup)
5. [NetBox Application Setup](#5-netbox-application-setup)
6. [Service Configuration](#6-service-configuration)
7. [Nginx Web Server Setup](#7-nginx-web-server-setup)
8. [SELinux & Firewall Configuration](#8-selinux--firewall-configuration)
9. [Final Steps & Verification](#9-final-steps--verification)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. System Requirements

### Hardware Requirements

*   **CPU:** 2+ Cores
*   **RAM:** 4+ GB
*   **Disk:** 20+ GB
*   **Internet Access:** Required (or configured corporate proxy)

### Software Version Requirements

| Component | NetBox v3.7.8 (OL8) | NetBox v4.4.6+ (OL9) |
|-----------|---------------------|----------------------|
| **OS** | Oracle Linux 8 | Oracle Linux 9 |
| **Python** | 3.9 | 3.11 or 3.12 |
| **PostgreSQL** | 12+ (recommend 13 or 15) | 14+ (recommend 15) |
| **Redis** | 4.0+ | 4.0+ |

### Oracle Linux Version Decision Matrix

**Oracle Linux 8:**
- Maximum Python version: 3.9 (via dnf modules)
- PostgreSQL versions: 10 (default ❌), 12, 13, 15 (via modules)
- Compatible NetBox: v3.7.8 (last version supporting Python 3.9)
- **Use Case:** Existing OL8 infrastructure, tested and stable

**Oracle Linux 9:**
- Python versions: 3.9, 3.11, 3.12 (via dnf modules)
- PostgreSQL versions: 13 (default), 15, 16 (via modules)
- Compatible NetBox: v4.0+ (latest features)
- **Use Case:** New installations, latest NetBox features
- **Recommended for greenfield deployments**

### Critical Version Dependencies

| NetBox Version | Min Python | Min PostgreSQL | Notes |
|----------------|-----------|----------------|-------|
| v3.7.8 | 3.8 | 12 | Last version for Python 3.9 |
| v4.0+ | 3.10 | 14 | Requires OL9 for Python 3.10+ |

---

## 2. System Preparation & Proxy Configuration

### Step 2.1: Verify Your Oracle Linux Version

```bash
# Check Oracle Linux version
cat /etc/oracle-release

# Expected output examples:
# Oracle Linux Server release 8.x
# Oracle Linux Server release 9.x
```

### Step 2.2: Update The System

```bash
sudo dnf update -y
```

### Step 2.3: Configure Corporate Proxy (If Required)

**Skip this section if you have direct internet access.**

If you're on a corporate network (like Elliott) with a proxy, configure it **before** installing packages:

#### Test if you need a proxy:

```bash
# Test internet connectivity
ping -c 3 8.8.8.8

# Test DNS resolution
ping -c 3 pypi.org

# If DNS fails, you likely need proxy configuration
```

#### Configure proxy for your environment:

```bash
# Replace proxyhost:1081 with your actual proxy server and port
export http_proxy="http://proxyhost:1081"
export https_proxy="http://proxyhost:1081"
export HTTP_PROXY="http://proxyhost:1081"
export HTTPS_PROXY="http://proxyhost:1081"
export no_proxy="localhost,127.0.0.1"

# Make proxy persistent for current user
cat >> ~/.bashrc <<EOF
export http_proxy="http://proxyhost:1081"
export https_proxy="http://proxyhost:1081"
export HTTP_PROXY="http://proxyhost:1081"
export HTTPS_PROXY="http://proxyhost:1081"
export no_proxy="localhost,127.0.0.1"
EOF

# Configure pip to use proxy (for your user)
mkdir -p ~/.config/pip
cat > ~/.config/pip/pip.conf <<EOF
[global]
proxy = http://proxyhost:1081
trusted-host = pypi.org
               pypi.python.org
               files.pythonhosted.org
EOF

# Configure pip for root user (needed for NetBox installation)
sudo mkdir -p /root/.config/pip
sudo tee /root/.config/pip/pip.conf > /dev/null <<EOF
[global]
proxy = http://proxyhost:1081
trusted-host = pypi.org
               pypi.python.org
               files.pythonhosted.org
EOF
```

### Step 2.4: Install Python

#### For Oracle Linux 8 (NetBox v3.7.8):

```bash
# List available Python versions
sudo dnf module list python*

# Enable Python 3.9 module
sudo dnf module enable python39 -y

# Install Python 3.9 and development packages
sudo dnf install -y python39 python39-devel

# Verify installation
python3.9 --version
# Expected: Python 3.9.x
```

#### For Oracle Linux 9 (NetBox v4.4.6+):

```bash
# List available Python versions
sudo dnf module list python*

# Enable Python 3.11 module (recommended)
sudo dnf module enable python311 -y

# Install Python 3.11 and development packages
sudo dnf install -y python3.11 python3.11-devel

# Verify installation
python3.11 --version
# Expected: Python 3.11.x
```

### Step 2.5: Install Base Packages

```bash
sudo dnf install -y git gcc libxml2-devel libxslt-devel libffi-devel \
    libpq-devel openssl-devel redis nginx policycoreutils-python-utils
```

**Note:** PostgreSQL will be installed in the next section with specific version selection.

---

## 3. PostgreSQL Database Setup

### Step 3.1: Install PostgreSQL with Correct Version

⚠️ **CRITICAL:** The default PostgreSQL on OL8 is version 10, which is **too old** for NetBox. You must explicitly select version 12 or higher.

#### For Oracle Linux 8 (NetBox v3.7.8):

```bash
# List available PostgreSQL versions
sudo dnf module list postgresql

# You'll see: postgresql 10 [d] (default), 12, 13, 15
# We need 12+ for NetBox 3.7.8

# Reset any existing PostgreSQL module
sudo dnf module reset postgresql -y

# Enable PostgreSQL 15 (recommended for best compatibility)
sudo dnf module enable postgresql:15 -y

# Install PostgreSQL server
sudo dnf install -y postgresql-server postgresql-contrib

# Verify version
psql --version
# Expected: psql (PostgreSQL) 15.x
```

#### For Oracle Linux 9 (NetBox v4.4.6+):

```bash
# List available PostgreSQL versions
sudo dnf module list postgresql

# Enable PostgreSQL 15 (recommended)
sudo dnf module enable postgresql:15 -y

# Install PostgreSQL server
sudo dnf install -y postgresql-server postgresql-contrib

# Verify version
psql --version
# Expected: psql (PostgreSQL) 15.x or higher
```

### Step 3.2: Initialize PostgreSQL Database

```bash
# Initialize the database cluster
sudo /usr/bin/postgresql-setup --initdb

# Start and enable the PostgreSQL service
sudo systemctl enable --now postgresql

# Verify service is running
sudo systemctl status postgresql
```

### Step 3.3: Configure PostgreSQL Authentication

⚠️ **CRITICAL:** PostgreSQL's default authentication method (`ident`) will not work for NetBox. You must change it to password-based authentication.

```bash
# Backup the original configuration
sudo cp /var/lib/pgsql/data/pg_hba.conf /var/lib/pgsql/data/pg_hba.conf.backup

# Edit the authentication configuration
sudo vim /var/lib/pgsql/data/pg_hba.conf
```

**Find these lines:**
```
# IPv4 local connections:
host    all             all             127.0.0.1/32            ident
# IPv6 local connections:
host    all             all             ::1/128                 ident
```

**Change to:**
```
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
```

**Alternative using sed:**
```bash
sudo sed -i 's/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            md5/' /var/lib/pgsql/data/pg_hba.conf
sudo sed -i 's/host    all             all             ::1\/128                 ident/host    all             all             ::1\/128                 md5/' /var/lib/pgsql/data/pg_hba.conf
```

**Reload PostgreSQL to apply changes:**
```bash
sudo systemctl reload postgresql
```

### Step 3.4: Create NetBox Database and User

```bash
# Connect to PostgreSQL as postgres user
sudo -u postgres psql
```

**Inside the PostgreSQL prompt, run these commands:**

⚠️ **Important:** Remember to add semicolons (`;`) at the end of each SQL statement!

```sql
-- Create the database for NetBox
CREATE DATABASE netbox;

-- Create a user for NetBox and assign the password
-- Replace 'YourSecurePassword' with a strong password
CREATE USER netbox WITH PASSWORD 'YourSecurePassword';

-- Grant all privileges on the netbox database to the netbox user
GRANT ALL PRIVILEGES ON DATABASE netbox TO netbox;

-- For PostgreSQL 15+, also run this additional grant:
\connect netbox
GRANT CREATE ON SCHEMA public TO netbox;

-- Exit PostgreSQL
\q
```

**Watch the PostgreSQL prompt to ensure commands are executed:**
- `postgres=#` - Ready for new command ✅
- `postgres-#` - Waiting to complete statement (you forgot the semicolon!) ❌

### Step 3.5: Test Database Connection

```bash
# Test connection with the netbox user
psql -h 127.0.0.1 -U netbox -d netbox -W

# Enter the password you created
# You should see: netbox=>

# Exit the test connection
\q
```

If the connection works, PostgreSQL is properly configured!

---

## 4. Redis Setup

Redis is used by NetBox for caching and background task queuing.

```bash
# Start and enable Redis
sudo systemctl enable --now redis

# Verify Redis is running
sudo systemctl status redis

# Test Redis connectivity
redis-cli ping
# Expected output: PONG
```

---

## 5. NetBox Application Setup

### Step 5.1: Clone NetBox Repository

#### For Oracle Linux 8 (NetBox v3.7.8):

```bash
sudo git clone -b v3.7.8 --depth 1 https://github.com/netbox-community/netbox.git /opt/netbox
```

#### For Oracle Linux 9 (NetBox v4.4.6+):

```bash
# Check latest version at: https://github.com/netbox-community/netbox/releases
sudo git clone -b v4.4.6 --depth 1 https://github.com/netbox-community/netbox.git /opt/netbox
```

### Step 5.2: Create NetBox System User

```bash
# Create system user with no login shell
sudo useradd -r -s /sbin/nologin -d /opt/netbox netbox

# Set ownership of NetBox directory
sudo chown -R netbox:netbox /opt/netbox
```

### Step 5.3: Create NetBox Configuration File

```bash
# Navigate to configuration directory
cd /opt/netbox/netbox/netbox/

# Copy example configuration
sudo cp configuration.example.py configuration.py

# Edit the configuration
sudo vim configuration.py
```

### Step 5.4: Configure NetBox Settings

Edit `/opt/netbox/netbox/netbox/configuration.py` and configure these **required** settings:

#### 1. ALLOWED_HOSTS

⚠️ **CRITICAL:** IP addresses and hostnames MUST be quoted strings in Python!

```python
# WRONG - This will cause a syntax error:
# ALLOWED_HOSTS = [128.1.9.232]

# CORRECT - IP addresses as strings:
ALLOWED_HOSTS = ['128.1.9.232', 'localhost', '127.0.0.1']

# If you have a hostname, add it too:
ALLOWED_HOSTS = ['128.1.9.232', 'netbox.elliott-group.info', 'localhost', '127.0.0.1']
```

#### 2. DATABASE Configuration

```python
DATABASE = {
    'NAME': 'netbox',
    'USER': 'netbox',
    'PASSWORD': 'YourSecurePassword',  # Use the password you created earlier
    'HOST': 'localhost',
    'PORT': '',
}
```

#### 3. REDIS Configuration

⚠️ **CRITICAL Oracle Linux 8 Issue:** OL8 maps `localhost` to IPv6 (`::1`), but Redis listens on IPv4 (`127.0.0.1`). This causes NetBox background workers to crash.

**Change `localhost` to `127.0.0.1` in BOTH Redis sections:**

```python
REDIS = {
    'tasks': {
        'HOST': '127.0.0.1',  # Changed from 'localhost'
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 0,
        'SSL': False,
    },
    'caching': {
        'HOST': '127.0.0.1',  # Changed from 'localhost'
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 1,
        'SSL': False,
    }
}
```

#### 4. SECRET_KEY

Generate a secret key:

```bash
# For Oracle Linux 8 (Python 3.9):
python3.9 /opt/netbox/netbox/generate_secret_key.py

# For Oracle Linux 9 (Python 3.11):
python3.11 /opt/netbox/netbox/generate_secret_key.py
```

Copy the output and paste it into your configuration:

```python
SECRET_KEY = 'paste_the_generated_key_here_between_quotes'
```

### Step 5.5: Validate Configuration Syntax

```bash
# For Oracle Linux 8:
python3.9 -m py_compile /opt/netbox/netbox/netbox/configuration.py

# For Oracle Linux 9:
python3.11 -m py_compile /opt/netbox/netbox/netbox/configuration.py

# No output = success!
# Syntax errors will be displayed if there are any
```

### Step 5.6: Fix NetBox upgrade.sh Script (OL8 Only)

⚠️ **Oracle Linux 8 / NetBox 3.7.8 Issue:** The upgrade script will fail due to a documentation build dependency bug.

```bash
# Backup the original upgrade script
sudo cp /opt/netbox/upgrade.sh /opt/netbox/upgrade.sh.backup

# Comment out the mkdocs build line
sudo sed -i 's/^\(\$PYTHON -m mkdocs build\)/# \1/' /opt/netbox/upgrade.sh

# Verify the change
grep "mkdocs" /opt/netbox/upgrade.sh
# Should show: # $PYTHON -m mkdocs build
```

**Oracle Linux 9 / NetBox 4.x users can skip this step.**

### Step 5.7: Run NetBox Installation Script

```bash
cd /opt/netbox

# Set Python version and proxy (if needed)
export http_proxy="http://proxyhost:1081"  # Only if using proxy
export https_proxy="http://proxyhost:1081" # Only if using proxy

# For Oracle Linux 8:
export PYTHON=/usr/bin/python3.9
sudo -E ./upgrade.sh

# For Oracle Linux 9:
export PYTHON=/usr/bin/python3.11
sudo -E ./upgrade.sh
```

**The script will:**
- Create a Python virtual environment
- Install all Python dependencies (via your proxy if configured)
- Run database migrations
- Collect static files
- **Prompt you to create a superuser** (do this!)

**Create the superuser when prompted:**
- Username: (your choice)
- Email: (your email)
- Password: (create a strong password)

### Step 5.8: Fix Permissions

⚠️ **CRITICAL:** The upgrade script runs as root, creating files owned by root. We must change ownership to the netbox user.

```bash
sudo chown -R netbox:netbox /opt/netbox
```

---

## 6. Service Configuration

NetBox requires two systemd services:
1. **netbox.service** - Main web application (Gunicorn)
2. **netbox-rq.service** - Background task worker (Redis Queue)

### Step 6.1: Copy Service Files

```bash
# Copy service files from contrib to systemd directory
sudo cp /opt/netbox/contrib/netbox.service /etc/systemd/system/
sudo cp /opt/netbox/contrib/netbox-rq.service /etc/systemd/system/

# Verify files were copied
ls -la /etc/systemd/system/netbox*
```

### Step 6.2: Copy Gunicorn Configuration

```bash
# Copy Gunicorn config to NetBox root directory
sudo cp /opt/netbox/contrib/gunicorn.py /opt/netbox/

# Verify file was copied
ls -la /opt/netbox/gunicorn.py
```

### Step 6.3: Reload systemd

```bash
sudo systemctl daemon-reload
```

**Don't start services yet - we need to configure Nginx and SELinux first.**

---

## 7. Nginx Web Server Setup

### Step 7.1: Remove Default Nginx Configuration

⚠️ **CRITICAL:** The default Nginx `server {}` block will conflict with NetBox. We must remove it.

```bash
# Backup original nginx.conf
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Edit nginx.conf
sudo vim /etc/nginx/nginx.conf
```

**Find and remove or comment out the default `server {}` block:**

Look for this section in the `http {}` block:
```nginx
server {
    listen       80;
    listen       [::]:80;
    server_name  _;
    root         /usr/share/nginx/html;
    ...
}
```

**Either delete the entire `server {}` block, or comment it out:**
```nginx
# server {
#     listen       80;
#     listen       [::]:80;
#     server_name  _;
#     root         /usr/share/nginx/html;
#     ...
# }
```

### Step 7.2: Create NetBox Nginx Configuration

```bash
sudo tee /etc/nginx/conf.d/netbox.conf > /dev/null <<'EOF'
server {
    listen 80;
    server_name 128.1.9.232;  # Replace with your IP or hostname
    client_max_body_size 25m;

    location /static/ {
        alias /opt/netbox/netbox/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header X-Forwarded-Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }
}
EOF
```

**Customize the configuration:**
- Replace `128.1.9.232` with your server's IP address or hostname
- Update `server_name` to match your `ALLOWED_HOSTS` from Step 5.4

### Step 7.3: Test Nginx Configuration

```bash
sudo nginx -t
# Expected: nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

## 8. SELinux & Firewall Configuration

### Step 8.1: Configure Firewall

```bash
# Open HTTP and HTTPS ports
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --add-service=https --permanent

# Reload firewall
sudo firewall-cmd --reload

# Verify rules
sudo firewall-cmd --list-services
# Should include: http https
```

### Step 8.2: Configure SELinux Network Policy

⚠️ **CRITICAL:** SELinux blocks Nginx from connecting to Gunicorn on port 8001 by default.

```bash
# Allow Nginx to make network connections
sudo setsebool -P httpd_can_network_connect 1

# Verify the setting
getsebool httpd_can_network_connect
# Expected: httpd_can_network_connect --> on
```

### Step 8.3: Configure SELinux File Contexts

⚠️ **CRITICAL:** SELinux blocks Nginx from reading NetBox static files (CSS, JavaScript, images). This causes broken styling even if NetBox loads.

```bash
# Set correct SELinux context for static files
sudo semanage fcontext -a -t httpd_sys_content_t "/opt/netbox/netbox/static(/.*)?"

# Apply the context
sudo restorecon -R -v /opt/netbox/netbox/static

# Verify the context
ls -lZ /opt/netbox/netbox/static/
# Should show: httpd_sys_content_t
```

---

## 9. Final Steps & Verification

### Step 9.1: Start All Services

```bash
# Start NetBox application services
sudo systemctl enable --now netbox
sudo systemctl enable --now netbox-rq

# Start Nginx
sudo systemctl enable --now nginx
```

### Step 9.2: Verify Services are Running

```bash
# Check NetBox web service
sudo systemctl status netbox

# Check NetBox background worker
sudo systemctl status netbox-rq

# Check Nginx
sudo systemctl status nginx

# All should show: active (running)
```

### Step 9.3: Check Service Logs

If any service fails, check the logs:

```bash
# NetBox application logs
sudo journalctl -u netbox -n 50

# NetBox background worker logs
sudo journalctl -u netbox-rq -n 50

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Step 9.4: Test NetBox Access

**From the command line:**
```bash
# Test HTTP connection
curl -I http://128.1.9.232
# Expected: HTTP/1.1 200 OK

# Test that you get NetBox content
curl http://128.1.9.232 | grep NetBox
```

**From a web browser:**
1. Navigate to `http://128.1.9.232` (or your server IP/hostname)
2. You should see the NetBox login page with proper styling
3. Log in with the superuser credentials you created in Step 5.7

**If you see:**
- ✅ NetBox login page with proper styling → **Success!**
- ❌ "502 Bad Gateway" → Check Step 8.2 (SELinux network policy)
- ❌ Page loads but CSS/styling is broken → Check Step 8.3 (SELinux file contexts)
- ❌ "Connection refused" → Check that all services are running (Step 9.2)

---

## 10. Troubleshooting

### PostgreSQL Issues

#### Problem: `/usr/bin/postgresql-setup: No such file or directory`

**Cause:** PostgreSQL server package not installed.

**Solution:**
```bash
sudo dnf install -y postgresql-server postgresql-contrib
```

#### Problem: `ERROR: role "netbox" does not exist`

**Cause:** You forgot the semicolon (`;`) at the end of a SQL statement. PostgreSQL is waiting for more input.

**How to identify:** The prompt shows `postgres-#` instead of `postgres=#`.

**Solution:**
```sql
-- Type a semicolon to end the incomplete statement
;

-- Or cancel the statement
\c

-- Then run commands correctly with semicolons
CREATE USER netbox WITH PASSWORD 'YourSecurePassword';
GRANT ALL PRIVILEGES ON DATABASE netbox TO netbox;
```

#### Problem: NetBox can't connect to database - "authentication failed"

**Cause:** PostgreSQL authentication method is still set to `ident` instead of `md5`.

**Solution:** See Step 3.3 - Configure PostgreSQL Authentication

#### Problem: Wrong PostgreSQL version (version 10 installed)

**Cause:** Didn't explicitly select PostgreSQL module version.

**Solution:**
```bash
# Remove PostgreSQL 10
sudo dnf remove postgresql-server postgresql-contrib

# Reset module
sudo dnf module reset postgresql -y

# Enable correct version
sudo dnf module enable postgresql:15 -y

# Reinstall
sudo dnf install -y postgresql-server postgresql-contrib

# Reinitialize
sudo /usr/bin/postgresql-setup --initdb
sudo systemctl restart postgresql

# Reconfigure authentication (Step 3.3)
# Recreate database and user (Step 3.4)
```

---

### Network & Proxy Issues

#### Problem: `Failed to establish a new connection: Network is unreachable`

**Cause:** Corporate proxy not configured, or pip can't reach PyPI.

**Solution:** See Step 2.3 - Configure Corporate Proxy

**Test connectivity:**
```bash
# Test basic internet
ping -c 3 8.8.8.8

# Test DNS
ping -c 3 pypi.org

# Test pip with proxy
pip3.9 --proxy=http://proxyhost:1081 install --dry-run wheel
```

---

### NetBox Configuration Issues

#### Problem: `SyntaxError: invalid syntax` on `ALLOWED_HOSTS` line

**Cause:** IP addresses in `ALLOWED_HOSTS` are not quoted.

**Wrong:**
```python
ALLOWED_HOSTS = [128.1.9.232]  # ❌ Syntax error
```

**Correct:**
```python
ALLOWED_HOSTS = ['128.1.9.232']  # ✅ Works
```

**Solution:**
```bash
# Edit configuration
sudo vim /opt/netbox/netbox/netbox/configuration.py

# Fix the ALLOWED_HOSTS line (add quotes around IPs)

# Validate syntax
python3.9 -m py_compile /opt/netbox/netbox/netbox/configuration.py
```

#### Problem: NetBox upgrade script fails with mkdocs error

**Cause:** NetBox 3.7.8 has outdated documentation dependencies.

**Solution:** See Step 5.6 - Comment out mkdocs line in upgrade.sh

---

### Service Issues

#### Problem: `netbox.service: Failed with result 'exit-code'`

**Cause:** Missing service files or wrong permissions.

**Solution:**
```bash
# Copy service files
sudo cp /opt/netbox/contrib/netbox.service /etc/systemd/system/
sudo cp /opt/netbox/contrib/netbox-rq.service /etc/systemd/system/
sudo cp /opt/netbox/contrib/gunicorn.py /opt/netbox/

# Fix permissions
sudo chown -R netbox:netbox /opt/netbox

# Reload systemd
sudo systemctl daemon-reload

# Restart services
sudo systemctl restart netbox netbox-rq
```

#### Problem: `netbox-rq` service keeps crashing

**Cause:** Redis IPv6/IPv4 mismatch. Oracle Linux 8 maps `localhost` to IPv6, but Redis listens on IPv4.

**Solution:** See Step 5.4 - Change Redis HOST from `'localhost'` to `'127.0.0.1'` in configuration.py

**Verify Redis is reachable:**
```bash
redis-cli -h 127.0.0.1 ping
# Expected: PONG
```

---

### Web Server Issues

#### Problem: Nginx shows default page instead of NetBox

**Cause:** Default Nginx `server {}` block is interfering.

**Solution:** See Step 7.1 - Remove default server block from nginx.conf

#### Problem: "502 Bad Gateway"

**Possible causes and solutions:**

**1. Gunicorn (netbox service) not running:**
```bash
sudo systemctl status netbox
sudo systemctl start netbox
sudo journalctl -u netbox -n 50
```

**2. SELinux blocking Nginx → Gunicorn connection:**
```bash
sudo setsebool -P httpd_can_network_connect 1
```

**3. Gunicorn not listening on port 8001:**
```bash
sudo ss -tlnp | grep 8001
# Should show gunicorn listening on 127.0.0.1:8001
```

#### Problem: NetBox loads but CSS/styling is broken

**Cause:** SELinux blocking Nginx from reading static files.

**Solution:** See Step 8.3 - Configure SELinux file contexts

```bash
sudo semanage fcontext -a -t httpd_sys_content_t "/opt/netbox/netbox/static(/.*)?"
sudo restorecon -R -v /opt/netbox/netbox/static
sudo systemctl restart nginx
```

**Verify:**
```bash
ls -lZ /opt/netbox/netbox/static/
# Should show: httpd_sys_content_t
```

---

### Permission Issues

#### Problem: Permission denied errors in logs

**Cause:** Files created by root, but netbox user needs to read/write them.

**Solution:**
```bash
sudo chown -R netbox:netbox /opt/netbox
sudo systemctl restart netbox netbox-rq
```

---

## Appendix A: Oracle Linux 9 Differences

If you're installing on **Oracle Linux 9** instead of OL8, the key differences are:

### Python Version
```bash
# OL9 uses Python 3.11 instead of 3.9
sudo dnf module enable python311 -y
sudo dnf install -y python3.11 python3.11-devel
export PYTHON=/usr/bin/python3.11
```

### NetBox Version
```bash
# OL9 supports NetBox 4.x (latest)
sudo git clone -b v4.4.6 --depth 1 https://github.com/netbox-community/netbox.git /opt/netbox
```

### PostgreSQL Version
```bash
# OL9 defaults to PostgreSQL 13, recommend 15
sudo dnf module enable postgresql:15 -y
sudo dnf install -y postgresql-server postgresql-contrib
```

### Skip mkdocs Workaround
**You do NOT need to comment out the mkdocs line on OL9 / NetBox 4.x.** That bug only affects NetBox 3.7.8.

### All other steps remain the same
- PostgreSQL authentication configuration (md5)
- Redis IPv4 fix (127.0.0.1)
- Service file copying
- SELinux configuration
- Nginx setup

---

## Appendix B: Next Steps for Production

This guide gets NetBox running on HTTP. For a production deployment, you should also:

1. **Configure HTTPS/SSL:**
   - Obtain SSL certificates (Let's Encrypt recommended)
   - Update Nginx configuration for SSL
   - Redirect HTTP → HTTPS

2. **Configure Backups:**
   - PostgreSQL database backups
   - NetBox media files
   - Configuration files

3. **Monitoring:**
   - Set up monitoring for services
   - Configure log rotation
   - Set up alerting

4. **Security Hardening:**
   - Review and tighten firewall rules
   - Configure fail2ban
   - Regular security updates

5. **Documentation:**
   - Document your specific configuration
   - Keep backup/restore procedures updated
   - Document any customizations

---

## Appendix C: Quick Reference Commands

### Service Management
```bash
# Check status
sudo systemctl status netbox netbox-rq nginx postgresql redis

# Restart services
sudo systemctl restart netbox netbox-rq nginx

# View logs
sudo journalctl -u netbox -f
sudo journalctl -u netbox-rq -f
sudo tail -f /var/log/nginx/error.log
```

### Database Access
```bash
# Connect to NetBox database
sudo -u postgres psql netbox

# Backup database
sudo -u postgres pg_dump netbox > /backup/netbox_backup_$(date +%Y%m%d).sql

# Restore database
sudo -u postgres psql netbox < /backup/netbox_backup_YYYYMMDD.sql
```

### NetBox Management
```bash
# Run NetBox management commands
sudo -u netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py <command>

# Examples:
# Check for migrations
sudo -u netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py showmigrations

# Create superuser
sudo -u netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py createsuperuser

# Clear cache
sudo -u netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py invalidate all
```

---

## Document History

- **2025-11-24:** Complete rewrite based on real-world Elliott infrastructure deployment
- Fixed all 13+ critical issues discovered during installation
- Added comprehensive troubleshooting based on actual problems encountered
- Tested and verified on Oracle Linux 8 with NetBox v3.7.8

---

**Questions or Issues?**

If you encounter problems not covered in this guide:
1. Check the [official NetBox documentation](https://netboxlabs.com/docs/netbox/)
2. Review the [NetBox GitHub issues](https://github.com/netbox-community/netbox/issues)
3. Consult the troubleshooting section above
4. Check service logs for specific error messages
