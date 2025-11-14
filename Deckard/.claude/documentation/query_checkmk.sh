#!/bin/bash
# Query Checkmk via livestatus socket over SSH
# Usage: query_checkmk.sh 'GET hosts' 'name state'

if [ -z "$1" ]; then
    echo "Usage: $0 '<GET|COMMAND>' '<column1> <column2> ...'"
    echo ""
    echo "Examples:"
    echo "  $0 'GET hosts' 'name state'"
    echo "  $0 'GET services' 'host_name service_description state'"
    exit 1
fi

GET_CMD="$1"
COLUMNS="$2"

ssh brian@10.10.10.5 "sudo su - monitoring -c 'python3 << 'PYEOF'
import socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(\"/omd/sites/monitoring/tmp/run/live\")
query = \"${GET_CMD}\\nColumns: ${COLUMNS}\\n\\n\"
sock.sendall(query.encode())
print(sock.recv(65536).decode())
sock.close()
PYEOF
'" 2>&1 | tail -n +7  # Skip the container banner lines
