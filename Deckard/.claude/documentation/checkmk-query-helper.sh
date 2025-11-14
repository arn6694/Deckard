#!/bin/bash
# Checkmk livestatus query helper
# Queries the Checkmk livestatus socket via SSH and returns JSON results

if [ $# -lt 1 ]; then
    echo "Usage: $0 '<livestatus_query>'"
    echo "Example: $0 'GET hosts\nColumns: name state'"
    exit 1
fi

QUERY="$1"

ssh brian@10.10.10.5 "sudo su - monitoring -c 'python3 << \"PYEOF\"
import socket
import json
import sys

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(\"/omd/sites/monitoring/tmp/run/live\")

# Send livestatus query
query = \"$QUERY\\n\\n\"
sock.sendall(query.encode())

# Read response
response = sock.recv(65536).decode()
print(response)
sock.close()
PYEOF
'"
