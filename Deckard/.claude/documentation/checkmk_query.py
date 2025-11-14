#!/usr/bin/env python3
"""
Checkmk Livestatus Query Helper
Queries Checkmk via livestatus socket over SSH
"""

import subprocess
import sys
import json

def query_checkmk(livestatus_query):
    """
    Query Checkmk livestatus via SSH

    Args:
        livestatus_query: Multi-line livestatus query (e.g., "GET hosts\nColumns: name state")

    Returns:
        Raw livestatus response
    """

    # Escape the query for Python
    query_escaped = livestatus_query.replace('"', '\\"').replace('\n', '\\n')

    # Python script to run on Checkmk server
    python_script = f'''
import socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect("/omd/sites/monitoring/tmp/run/live")
query = """{livestatus_query}\\n\\n"""
sock.sendall(query.encode())
response = sock.recv(65536).decode()
print(response)
sock.close()
'''

    # Run via SSH
    cmd = [
        'ssh', 'brian@10.10.10.5',
        'sudo su - monitoring -c \'python3 << "PYEOF"\n' + python_script + '\nPYEOF\''
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Filter out the container banner that SSHv adds
            lines = result.stdout.split('\n')
            # Skip the first few lines (banner)
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('['):
                    return '\n'.join(lines[i:])
            return result.stdout
        else:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return None
    except subprocess.TimeoutExpired:
        print("Error: Query timed out", file=sys.stderr)
        return None

def format_livestatus_response(response):
    """
    Parse livestatus response and return as structured data

    Args:
        response: Raw livestatus response

    Returns:
        List of lists (rows)
    """
    lines = response.strip().split('\n')
    rows = []
    for line in lines:
        if line:
            # Split by semicolons for CSV format response
            rows.append(line.split(';'))
    return rows

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: checkmk_query.py '<livestatus_query>'")
        print("Example: checkmk_query.py 'GET hosts\\nColumns: name state'")
        sys.exit(1)

    query = sys.argv[1]
    response = query_checkmk(query)

    if response:
        print(response)
    else:
        sys.exit(1)
