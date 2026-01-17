#!/usr/bin/env python3
"""
Tech Article Monitor with AI Screening
Posts only relevant articles to Discord after AI evaluation.
Monitors XDA Developers and How-To Geek RSS feeds.
Uses Groq API (primary) with local Ollama fallback.
"""
import urllib.request
import os
import json
import re
import time
from datetime import datetime
from html import unescape

# Configuration
DISCORD_WEBHOOK = "DISCORD_WEBHOOK_REDACTED"
RSS_FEEDS = [
    ("XDA", "https://www.xda-developers.com/feed/"),
    ("How-To Geek", "https://www.howtogeek.com/feed/"),
]
POSTED_FILE = "/var/lib/xda_discord/posted_articles.txt"
LOG_FILE = "/var/log/xda_discord.log"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

# Ollama configuration - Jarvis host (primary)
OLLAMA_URL = "http://10.10.10.49:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

# Groq configuration (fallback when Jarvis is offline)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

# Brian's interests for filtering
SYSTEM_PROMPT = """You are an article screener for a Linux power user and homelab enthusiast. APPROVE articles that would interest someone who:
- Runs a Linux homelab (Proxmox, LXCs, Docker, VMs)
- Builds and upgrades PCs and servers
- Cares about PC hardware (CPUs, GPUs, motherboards, RAM, storage, networking)
- Uses Synology NAS and self-hosted services (Jellyfin, Plex, n8n, Nginx, etc.)
- Runs Home Assistant for home automation
- Uses Linux desktop (Mint, Pop!_OS, etc.)
- Uses Obsidian for note-taking and knowledge management
- Interested in AI, LLMs, local AI models, and AI-powered tools
- Values productivity tools and power-user software

APPROVE these topics:
- PC hardware news (GPUs, CPUs, motherboards, RAM, SSDs, networking gear)
- Mini PCs, small form factor builds, NUCs
- Linux distro news and software
- Self-hosting, Docker, server builds
- Home automation and smart home
- Networking (routers, switches, 2.5GbE, 10GbE)
- NAS and storage solutions
- AI and LLM news (ChatGPT, Claude, Ollama, local models, AI tools)
- Obsidian, note-taking apps, knowledge management, PKM
- Productivity tools that work on Linux
- Privacy and security tools
- Raspberry Pi and SBC projects
- Automation tools (n8n, Home Assistant, Ansible, scripting, infrastructure as code)
- Media servers (Jellyfin, Plex, *arr apps)
- Steam, Steam Deck, Proton/Linux gaming
- These specific games (ALWAYS APPROVE): Valheim, Enshrouded, Hytale
- Survival and crafting games
- Apple ecosystem (iPhone, iPad, Apple Watch, Apple TV, macOS)
- Smartwatches, especially Apple Watch
- Streaming services the user subscribes to (ALWAYS APPROVE news about): Netflix, Disney+, ESPN, Hulu, Apple TV+

REJECT these topics:
- Android phones and Android tablets
- Video games NOT in the approved list (e.g., Call of Duty, FIFA, Fortnite, Sims)
- Gaming industry drama and esports news
- Console gaming (PlayStation, Xbox, Nintendo)
- Earbuds and headphones reviews
- Social media platform news (Twitter/X, Facebook, TikTok, Instagram)
- Celebrity tech news

Respond with ONLY "APPROVE" or "REJECT" followed by a one-sentence reason."""


def log(message):
    timestamp = datetime.now().strftime("%c")
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp}: {message}\n")


def clean_html(text):
    """Remove HTML tags and clean up text."""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_article_content(url):
    """Fetch and extract article content from URL."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        response = urllib.request.urlopen(req, timeout=15)
        html = response.read().decode('utf-8', errors='ignore')

        # Try to extract article content (XDA uses article tags)
        article_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
        if article_match:
            content = clean_html(article_match.group(1))
        else:
            # Fallback: grab paragraphs
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
            content = ' '.join(clean_html(p) for p in paragraphs[:10])

        # Limit content length for LLM
        return content[:3000] if content else ""
    except Exception as e:
        log(f"Failed to fetch content: {url} - {e}")
        return ""


def check_ollama_available():
    """Check if Jarvis Ollama is responding."""
    try:
        req = urllib.request.Request(
            "http://10.10.10.49:11434/api/tags",
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req, timeout=5)
        return response.status == 200
    except Exception:
        return False


def evaluate_with_ollama(title, content):
    """Use local Ollama on Jarvis to evaluate article."""
    prompt = f"""{SYSTEM_PROMPT}

ARTICLE TITLE: {title}

ARTICLE EXCERPT:
{content[:2000]}

Your verdict:"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 100
        }
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    response = urllib.request.urlopen(req, timeout=60)
    result = json.loads(response.read().decode('utf-8'))
    return result.get('response', 'REJECT: No response')


def evaluate_with_groq(title, content):
    """Use Groq API as fallback when Jarvis is offline."""
    user_prompt = f"""ARTICLE TITLE: {title}

ARTICLE EXCERPT:
{content[:2000]}

Your verdict:"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 100
    }

    req = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {GROQ_API_KEY}',
            'User-Agent': USER_AGENT
        }
    )
    response = urllib.request.urlopen(req, timeout=30)
    result = json.loads(response.read().decode('utf-8'))
    return result['choices'][0]['message']['content']


def evaluate_article(title, content):
    """Evaluate article - try Groq first (smarter 8B), fall back to local Ollama."""
    # Try Groq first - it's free and the 8B model is smarter than local 3B
    try:
        return evaluate_with_groq(title, content), "groq"
    except Exception as e:
        log(f"Groq failed, trying Ollama: {e}")

    # Fallback to local Ollama
    if check_ollama_available():
        try:
            log("Using Ollama (Jarvis) as fallback")
            return evaluate_with_ollama(title, content), "ollama"
        except Exception as e:
            log(f"Ollama also failed: {e}")

    return "REJECT: All LLMs unavailable", "none"


def post_to_discord(title, link, reason, provider, source="XDA"):
    """Post approved article to Discord."""
    provider_tag = "local" if provider == "ollama" else "groq"
    payload = {
        "content": f"**New {source} Article (AI Approved via {provider_tag}):**\n**{title}**\n{link}\n\n*Why:* {reason}"
    }
    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT
        }
    )
    urllib.request.urlopen(req, timeout=10)


try:
    # Load posted articles
    try:
        with open(POSTED_FILE, 'r') as f:
            posted = set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        posted = set()

    approved_count = 0
    rejected_count = 0
    ollama_used = 0
    groq_used = 0

    # Process each RSS feed
    for source_name, feed_url in RSS_FEEDS:
        try:
            req = urllib.request.Request(feed_url, headers={'User-Agent': USER_AGENT})
            response = urllib.request.urlopen(req, timeout=10)
            rss_data = response.read().decode('utf-8')
        except Exception as e:
            log(f"Failed to fetch {source_name} feed: {e}")
            continue

        # Extract items
        items = re.findall(r'<item>(.*?)</item>', rss_data, re.DOTALL)

        for item in items:
            # Handle both CDATA-wrapped and plain titles
            title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
            if not title_match:
                title_match = re.search(r'<title>(.*?)</title>', item)
            title = clean_html(title_match.group(1)) if title_match else ""

            link_match = re.search(r'<link>(.*?)</link>', item)
            link = link_match.group(1).strip() if link_match else ""

            if not title or not link or link in posted:
                continue

            # Mark as processed
            posted.add(link)

            # Fetch article content
            content = fetch_article_content(link)

            # Evaluate with AI (Ollama or Groq fallback)
            verdict, provider = evaluate_article(title, content)

            if provider == "ollama":
                ollama_used += 1
            elif provider == "groq":
                groq_used += 1

            if verdict.upper().startswith('APPROVE'):
                reason = verdict.replace('APPROVE', '').strip(': ')
                try:
                    post_to_discord(title, link, reason, provider, source_name)
                    approved_count += 1
                    log(f"✓ APPROVED [{source_name}][{provider}]: {title}")
                    time.sleep(1)
                except Exception as e:
                    log(f"✗ Discord failed [{source_name}]: {title} - {e}")
            else:
                rejected_count += 1
                log(f"✗ REJECTED [{source_name}][{provider}]: {title} - {verdict}")

    # Save posted (last 200)
    with open(POSTED_FILE, 'w') as f:
        for link in list(posted)[-200:]:
            f.write(link + '\n')

    if approved_count > 0 or rejected_count > 0:
        log(f"Summary: {approved_count} approved, {rejected_count} rejected (Ollama: {ollama_used}, Groq: {groq_used})")
    else:
        log("No new articles")

except Exception as e:
    log(f"ERROR: {str(e)}")
    raise
