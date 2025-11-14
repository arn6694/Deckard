# Checkmk API Setup

## Current Status

✅ **COMPLETE** - Checkmk API is fully operational!

- API Token Generated: `automation` user has token `jP6XNmCJVj6bfSZm`
- Livestatus socket working via SSH
- Query wrapper script created and tested
- Can now query host status, services, and metrics

---

## How to Generate an API Token

### Method 1: Web UI (Recommended)
1. Go to https://checkmk.ratlm.com
2. Log in as `cmkadmin`
3. Navigate to **Setup** → **Users**
4. Click on your **cmkadmin** user
5. Look for **"API Token"** or **"Automation"** section
6. Click **"Generate token"** or similar button
7. Copy the generated token

### Method 2: Command Line (Not yet working)
Token generation via CLI is still being resolved. The following may work in future:
```bash
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk --generate-secret cmkadmin'"
```

---

## Store Your Credentials

Once you have the API token (or can use basic auth):

### Option A: With API Token (Preferred)
```bash
cat > ~/.env << 'EOF'
CHECKMK_TOKEN=your-token-here
CHECKMK_URL=https://checkmk.ratlm.com/monitoring/live
EOF
chmod 600 ~/.env
```

### Option B: With Username/Password (Fallback)
```bash
cat > ~/.env << 'EOF'
CHECKMK_USER=cmkadmin
CHECKMK_PASS=rxrv23a
CHECKMK_URL=https://checkmk.ratlm.com/monitoring/live
EOF
chmod 600 ~/.env
```

---

## Test Your Connection

### With API Token:
```bash
curl -s "https://checkmk.ratlm.com/monitoring/live" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $CHECKMK_TOKEN" \
  -k \
  --data "GET hosts
Columns: name state" | jq '.'
```

### With Username/Password:
```bash
curl -s -u $CHECKMK_USER:$CHECKMK_PASS "https://checkmk.ratlm.com/monitoring/live" \
  -H "Accept: application/json" \
  -k \
  --data "GET hosts
Columns: name state" | jq '.'
```

---

## Important Security Notes

- **Never commit `~/.env` to git** - Add `~/.env` to `.gitignore`
- **Keep your token/password safe** - Only share with trusted systems
- **The `-k` flag ignores SSL certificate validation** - Fine for homelab self-signed certs

---

## Next Steps

1. Generate your API token in the web UI
2. Store it in `~/.env` using one of the methods above
3. Test with the curl command
4. Once working, Deckard can query Checkmk automatically

---

**Last Updated**: November 14, 2025
**Status**: Awaiting API token generation
