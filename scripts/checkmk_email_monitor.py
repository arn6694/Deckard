#!/usr/bin/env python3
"""
Checkmk Email Alert Monitor
Monitors Gmail inbox for Checkmk alerts and triggers remediation actions
"""

import os
import sys
import imaplib
import email
import json
import subprocess
import logging
from email.header import decode_header
from datetime import datetime
from pathlib import Path

# Configuration
GMAIL_ADDRESS = "brian.j.arnett@gmail.com"
GMAIL_APP_PASSWORD = "woli xnol zaqd ecig"  # From .env file
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

# Remediation mappings: subject pattern -> action
# STRATEGY: Prevention-first (thresholds tuned to industry standard)
# If similar alerts still arrive: thresholds need further adjustment
# These actions investigate and escalate, not blindly restart
REMEDIATION_RULES = {
    # NTP alerts - if these persist after threshold adjustment, investigate root cause
    "NTP Time.*CRIT": {
        "description": "NTP CRITICAL - verify threshold adjustment is working",
        "hosts": ["proxmox", "ansible"],
        "actions": [
            "logger -t checkmk_monitor '⚠️  NTP CRITICAL ALERT (threshold should be 50/200ms for proxmox, 100/500ms for ansible)'",
            "logger -t checkmk_monitor 'If this persists, thresholds need further review - check actual offset values'",
            "logger -t checkmk_monitor 'Diagnostics: chronyc tracking (proxmox), chronyd status (ansible)'"
        ]
    },

    # Persistent NTP warnings - indicates threshold may still be too strict
    "NTP Time.*WARN": {
        "description": "NTP WARNING - check threshold tuning",
        "hosts": ["proxmox", "ansible"],
        "actions": [
            "logger -t checkmk_monitor '⚠️  NTP WARNING: Alert received despite threshold adjustment'",
            "logger -t checkmk_monitor 'Verify offset values: should be < 50ms (proxmox) and < 100ms (ansible) normally'"
        ]
    },

    # DNS alerts - escalate to admin if thresholds not helping
    "DNS.*CRIT": {
        "description": "DNS CRITICAL - threshold adjustment may not be helping",
        "hosts": ["bind9-primary"],
        "actions": [
            "logger -t checkmk_monitor '⚠️  DNS CRITICAL: Indicates BIND9 or network issue, not just threshold problem'",
            "logger -t checkmk_monitor 'Manual check: systemctl status bind9 on bind9-primary (10.10.10.4)'"
        ]
    },

    # Memory critical - watch for persistence
    "Memory.*CRIT": {
        "description": "Memory CRITICAL - if recurring, indicates real resource issue",
        "hosts": ["*"],
        "actions": [
            "logger -t checkmk_monitor '⚠️  Memory CRITICAL: If this is recurring, likely a real resource problem, not just threshold'"
        ]
    },

    # Checkmk service critical - something may be wrong with monitoring itself
    "Checkmk.*CRIT": {
        "description": "Checkmk CRITICAL - monitoring system issue",
        "hosts": ["checkmk"],
        "actions": [
            "logger -t checkmk_monitor '⚠️  CHECKMK CRITICAL: Monitoring system itself has an issue'",
            "logger -t checkmk_monitor 'Check: sudo su - monitoring -c \"omd status\" on 10.10.10.5'"
        ]
    },

    # Frequent warning state transitions - threshold may oscillate around edge
    "OK -> WARN": {
        "description": "Service degraded to WARNING",
        "hosts": ["*"],
        "actions": [
            "logger -t checkmk_monitor 'WARNING: Service transitioned to warning state'"
        ]
    },

    # Service flapping after threshold change - indicates threshold too aggressive
    "Flapping": {
        "description": "Service flapping after threshold adjustment",
        "hosts": ["*"],
        "actions": [
            "logger -t checkmk_monitor '⚠️  SERVICE FLAPPING: Threshold may oscillate around edge case'",
            "logger -t checkmk_monitor 'Consider widening threshold band if service is otherwise healthy'"
        ]
    },

    # All CRITICAL alerts - emphasize investigation over auto-fix
    "CRIT": {
        "description": "CRITICAL alert - needs investigation",
        "hosts": ["*"],
        "actions": [
            "logger -t checkmk_monitor '⚠️  CRITICAL: Real issue detected (not threshold-related) - requires investigation'"
        ]
    }
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/checkmk_email_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def connect_gmail():
    """Connect to Gmail via IMAP"""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        logger.info(f"Connected to Gmail as {GMAIL_ADDRESS}")
        return mail
    except Exception as e:
        logger.error(f"Failed to connect to Gmail: {e}")
        return None


def get_sender_name(from_header):
    """Extract sender name from email header"""
    try:
        # Parse the From header
        if '<' in from_header:
            name = from_header.split('<')[0].strip()
        else:
            name = from_header.split('@')[0] if '@' in from_header else from_header
        return name
    except:
        return from_header


def is_checkmk_alert(email_message):
    """Check if email is from Checkmk"""
    from_header = email_message.get('From', '')
    sender_name = get_sender_name(from_header)

    checkmk_indicators = ['checkmk', 'monitoring', 'noreply']
    return any(indicator in sender_name.lower() for indicator in checkmk_indicators)


def get_subject(email_message):
    """Extract and decode email subject"""
    subject = email_message.get('Subject', 'No Subject')
    # Handle encoded subjects
    if isinstance(subject, str):
        try:
            decoded_parts = decode_header(subject)
            subject = ''.join([
                part[0].decode(part[1] or 'utf-8') if isinstance(part[0], bytes) else part[0]
                for part in decoded_parts
            ])
        except:
            pass
    return subject


def get_body(email_message):
    """Extract email body"""
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain':
                try:
                    return part.get_payload(decode=True).decode('utf-8')
                except:
                    return part.get_payload()
    else:
        try:
            return email_message.get_payload(decode=True).decode('utf-8')
        except:
            return email_message.get_payload()
    return ""


def find_matching_rule(subject):
    """Find remediation rule matching the subject"""
    import re
    for pattern, rule in REMEDIATION_RULES.items():
        if re.search(pattern, subject, re.IGNORECASE):
            return rule
    return None


def execute_remediation(rule, subject, body):
    """Execute remediation actions for a matched rule"""
    logger.info(f"Executing remediation: {rule['description']}")
    logger.info(f"Subject: {subject}")

    for action in rule['actions']:
        try:
            logger.info(f"Running: {action}")
            result = subprocess.run(action, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info(f"✓ Action succeeded: {action}")
            else:
                logger.warning(f"⚠ Action returned non-zero: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error(f"✗ Action timed out: {action}")
        except Exception as e:
            logger.error(f"✗ Action failed: {action} - {e}")


def process_email(email_message, mail=None):
    """Process a single email"""
    from_header = email_message.get('From', 'Unknown')
    subject = get_subject(email_message)
    body = get_body(email_message)

    logger.info(f"Processing email: From={from_header}, Subject={subject}")

    if is_checkmk_alert(email_message):
        logger.info("✓ Email is from Checkmk")

        # Find matching remediation rule
        rule = find_matching_rule(subject)

        if rule:
            logger.info(f"✓ Matched rule: {rule['description']}")
            execute_remediation(rule, subject, body)
        else:
            logger.info("No matching remediation rule found")
    else:
        logger.debug(f"Email not from Checkmk: {from_header}")


def check_inbox(limit=10):
    """Check Gmail inbox for new Checkmk alerts"""
    mail = connect_gmail()
    if not mail:
        return False

    try:
        # Select inbox
        mail.select('INBOX')

        # Search for unseen emails
        status, message_ids = mail.search(None, 'UNSEEN')

        if status != 'OK':
            logger.error("Failed to search inbox")
            return False

        message_ids = message_ids[0].split()[-limit:]  # Get last N messages

        if not message_ids:
            logger.debug("No new messages")
            return True

        logger.info(f"Found {len(message_ids)} new messages")

        # Process each message
        for msg_id in message_ids:
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            if status != 'OK':
                logger.warning(f"Failed to fetch message {msg_id}")
                continue

            try:
                email_message = email.message_from_bytes(msg_data[0][1])
                process_email(email_message, mail)

                # Mark as read after processing
                mail.store(msg_id, '+FLAGS', '\\Seen')
            except Exception as e:
                logger.error(f"Error processing message: {e}")

        return True

    except Exception as e:
        logger.error(f"Error checking inbox: {e}")
        return False

    finally:
        try:
            mail.close()
            mail.logout()
        except:
            pass


def main():
    """Main entry point"""
    logger.info("=== Checkmk Email Monitor Started ===")

    # Check if running as a daemon (cron job)
    if len(sys.argv) > 1 and sys.argv[1] == '--daemon':
        logger.info("Running in daemon mode (cron)")
    else:
        logger.info("Running in interactive mode")

    # Check inbox
    success = check_inbox(limit=10)

    if success:
        logger.info("=== Check completed successfully ===")
        return 0
    else:
        logger.error("=== Check failed ===")
        return 1


if __name__ == '__main__':
    sys.exit(main())
