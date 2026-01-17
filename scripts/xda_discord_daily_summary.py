#!/usr/bin/env python3
"""
Daily Summary of Rejected Tech Articles
Sends a Discord message with articles that were filtered out in the past 24 hours.
Run daily at 8pm via cron.
"""
import urllib.request
import json
import re
from datetime import datetime, timedelta

# Configuration
DISCORD_WEBHOOK = "DISCORD_WEBHOOK_REDACTED"
LOG_FILE = "/var/log/xda_discord.log"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"


def parse_log_entry(line):
    """Parse a log line and extract timestamp and content."""
    # Format: "Sat Jan 17 09:59:32 2026: ✗ REJECTED [Source][provider]: Title - Reason"
    match = re.match(r'^(\w+ \w+ \d+ \d+:\d+:\d+ \d+): (.+)$', line)
    if match:
        timestamp_str, content = match.groups()
        try:
            timestamp = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Y")
            return timestamp, content
        except ValueError:
            pass
    return None, None


def extract_rejection_info(content):
    """Extract source, title, and reason from rejection log entry."""
    # Format: "✗ REJECTED [Source][provider]: Title - Reason"
    match = re.match(r'✗ REJECTED \[([^\]]+)\]\[([^\]]+)\]: (.+?) - (.+)$', content)
    if match:
        source, provider, title, reason = match.groups()
        return {
            'source': source,
            'provider': provider,
            'title': title.strip(),
            'reason': reason.strip()
        }
    return None


def get_rejections_since(hours=24):
    """Get all rejected articles from the past N hours."""
    cutoff = datetime.now() - timedelta(hours=hours)
    rejections = []

    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if 'REJECTED' not in line:
                    continue

                timestamp, content = parse_log_entry(line)
                if timestamp and timestamp > cutoff:
                    info = extract_rejection_info(content)
                    if info:
                        info['timestamp'] = timestamp
                        rejections.append(info)
    except FileNotFoundError:
        pass

    return rejections


def post_summary_to_discord(rejections):
    """Post the daily rejection summary to Discord."""
    if not rejections:
        return  # Don't post if nothing was rejected

    # Group by source
    by_source = {}
    for r in rejections:
        source = r['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(r)

    # Build message
    lines = ["📋 **Daily Rejected Articles Summary**", ""]
    lines.append("*These articles were filtered out today. Reply if any should be approved:*")
    lines.append("")

    for source, items in by_source.items():
        lines.append(f"**{source}** ({len(items)} rejected):")
        for item in items[:10]:  # Limit to 10 per source
            # Truncate long titles
            title = item['title'][:80] + "..." if len(item['title']) > 80 else item['title']
            lines.append(f"• {title}")
        if len(items) > 10:
            lines.append(f"  *...and {len(items) - 10} more*")
        lines.append("")

    lines.append(f"*Total: {len(rejections)} articles filtered in past 24h*")

    message = "\n".join(lines)

    # Discord message limit is 2000 chars
    if len(message) > 1900:
        message = message[:1900] + "\n\n*[Message truncated]*"

    payload = {"content": message}

    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT
        }
    )
    urllib.request.urlopen(req, timeout=10)


if __name__ == "__main__":
    rejections = get_rejections_since(hours=24)
    if rejections:
        post_summary_to_discord(rejections)
        print(f"Posted summary of {len(rejections)} rejected articles")
    else:
        print("No rejected articles in the past 24 hours")
