<div align="center">
<h1>SOCMED - Social Media Link Finder</h1>
</div>

<div align="center">
<img src="img/icon.png" width="200">
</div>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0-blue.svg?style=for-the-badge">
  <img src="https://img.shields.io/badge/python-3.6+-green.svg?style=for-the-badge">
  <img src="https://img.shields.io/badge/license-MIT-red.svg?style=for-the-badge">
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20windows-lightgrey?style=for-the-badge">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge">
</p>

<p align="center">
  <b>Advanced Social Media Link Discovery & Broken Link Hijacking Detection Tool</b><br>
  <i>Find, verify, and analyze social media links across 15+ platforms with automatic vulnerability detection</i>
</p>

---

## Table of Contents

- [Overview](#overview)
- [What is Broken Link Hijacking?](#what-is-broken-link-hijacking)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Broken Link Detection](#broken-link-detection)
- [Database & History](#database--history)
- [Proxy Support](#proxy-support)
- [Custom Rules](#custom-rules)
- [Color Support](#color-support)
- [Results & Interpretation](#results--interpretation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [Resources](#resources)
- [Acknowledgments](#acknowledgments)

---

## Overview

**SOCMED v2.0** is an advanced tool for discovering, verifying, and analyzing social media links on websites. It is specifically designed to help cybersecurity professionals identify potential **Broken Link Hijacking** vulnerabilities through automated validation.

### What is Broken Link Hijacking?

**Broken Link Hijacking** is an exploitation technique where an attacker takes advantage of social media links that are no longer active (broken/dead links). When a website has links to a social media account that has been deleted or deactivated:

- An attacker can re-register that username
- Hijack the website's visitor traffic
- Carry out phishing or further attacks
- Damage the company's reputation and brand trust

### Use Cases

- Security auditing & penetration testing
- OSINT (Open Source Intelligence) gathering
- Brand protection monitoring
- Vulnerability assessment
- Digital footprint analysis
- Compliance checking

---

## Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Multi-Platform** | Supports 15+ social media platforms | Yes |
| **Broken Link Detection** | Automatically identifies broken/dead links | Yes |
| **Database Storage** | SQLite database for scan history | Yes |
| **Proxy Support** | HTTP/HTTPS proxy with authentication | Yes |
| **Rate Limiting** | Automatic rate limiting to avoid detection | Yes |
| **User-Agent Rotation** | Random User-Agent for each request | Yes |
| **Hex Color Support** | True Color & 256 color terminal display | Yes |
| **Concurrent Processing** | Multi-threaded for maximum speed | Yes |
| **Custom Rules** | YAML-based custom search rules | Yes |
| **Multiple Export Formats** | JSON, CSV, TXT, and SQLite | Yes |
| **Progress Bar** | Real-time visual progress indicator | Yes |
| **Redirect Handling** | Automatic redirect following | Yes |
| **Selective Scanning** | Choose specific platforms or scan all | Yes |
| **Verbose Mode** | Detailed debugging information | Yes |
| **Scan History** | View and analyze past scans | Yes |

---

## Installation

### Prerequisites

```bash
# Python 3.6 or later
python --version

# Install pip
pip --version
```

Clone Repository

```bash
# Clone the repository
git clone https://github.com/CayberMods/SocMed.git
cd SocMed
```

Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```
---

## Configuration

config/config.yaml

Create a config/config.yaml file for advanced configuration:

```yaml
general:
  timeout: 10
  workers: 20
  verbose: false
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

platforms:
  instagram: true
  telegram: true
  youtube: true
  tiktok: true
  twitter: true
  facebook: false
  linkedin: false
  github: false
  reddit: false
  discord: false
  spotify: false
  medium: false
  twitch: false

proxy:
  enabled: false
  type: "http"  # http, https, socks5
  host: "127.0.0.1"
  port: 8080
  username: ""
  password: ""

output:
  format: "txt"  # txt, json, csv
  save_results: true
  filename: "results"

database:
  enabled: false
  type: "sqlite"  # sqlite, postgresql, mysql
  path: "scans.db"

rate_limit:
  enabled: true
  max_requests: 50
  time_window: 60  # seconds
  auto_adjust: true

user_agents:
  - "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  - "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
  - "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
```

Using Config

```bash
python socmed.py -l domains.txt -config config/config.yaml -all
```

---

## Usage

Basic Usage

```bash
python socmed.py -l <domains.txt> [OPTIONS]
```

Usage Examples

Scan All Platforms

```bash
python socmed.py -l domains.txt -all
```

Scan Specific Platforms

```bash
# Scan Instagram & Telegram only
python socmed.py -l domains.txt -ig -tele

# Scan Instagram, YouTube, Twitter
python socmed.py -l domains.txt -ig -yt -tw
```

With Custom Rules

```bash
python socmed.py -l domains.txt -custom custom_rules.yaml -v
```

With Proxy

```bash
python socmed.py -l domains.txt -all --proxy http://user:pass@127.0.0.1:8080
```

Export Results

```bash
# JSON export
python socmed.py -l domains.txt -all --json -o results

# CSV export
python socmed.py -l domains.txt -all --csv -o results

# Save to database
python socmed.py -l domains.txt -all --db
```

View History

```bash
python socmed.py --history
```

Test Color Support

```bash
python socmed.py --test-colors
```

Full Parameter List

Parameter Shorthand Description Default
--list -l Domain list file (required) 
--output -o Output results file 
--timeout -t Request timeout (seconds) 10
--workers -w Number of concurrent workers 20
--verbose -v Verbose mode False
--test-colors  Test color support 
--json  Export results to JSON False
--csv  Export results to CSV False
--db  Save results to database False
--history  Show scan history False
--proxy  Proxy URL 
--config  Configuration file (YAML) 
--instagram -ig Scan Instagram False
--telegram -tele Scan Telegram False
--youtube -yt Scan YouTube False
--tiktok -tt Scan TikTok False
--twitter -tw Scan Twitter/X False
--facebook -fb Scan Facebook False
--linkedin -in Scan LinkedIn False
--github -gh Scan GitHub False
--reddit -rd Scan Reddit False
--discord -dc Scan Discord False
--spotify -sp Scan Spotify False
--medium -md Scan Medium False
--twitch -tc Scan Twitch False
--all -all Scan all platforms False
--custom-method -custom Custom rules YAML file 

Supported Platforms

Platform Flag Detection Pattern Broken Detection
Instagram -ig instagram.com/[username] Yes
Telegram -tele t.me/[username] Yes
YouTube -yt youtube.com/@[channel] Yes
TikTok -tt tiktok.com/@[username] Yes
Twitter/X -tw twitter.com/[username] Yes
Facebook -fb facebook.com/[username] Yes
LinkedIn -in linkedin.com/in/[username] Yes
GitHub -gh github.com/[username] Yes
Reddit -rd reddit.com/user/[username] Yes
Discord -dc discord.gg/[invite] Yes
Spotify -sp open.spotify.com/[id] Yes
Medium -md medium.com/@[username] Yes
Twitch -tc twitch.tv/[username] Yes

---

## Broken Link Detection

How It Works

SOCMED v2.0 uses intelligent detection algorithms to verify if social media links are active or broken:

1. HTTP Status Code Check - Detects 404, 410, and other error codes
2. Content Analysis - Parses HTML for error messages and patterns
3. Title Verification - Checks for "Page Not Found" and similar titles
4. Meta Tag Inspection - Analyzes OG tags for error indicators
5. Element Detection - Searches for error-specific HTML elements

Detection Methods by Platform

Platform Detection Methods
Instagram Status code, title check, meta tags, error keywords
Twitter/X Status code, title check, error keywords
YouTube Status code, title check, iframe detection
Facebook Status code, title check, meta tags, error keywords
LinkedIn Status code, title check, H1 tags, error keywords
GitHub Status code, title check, error keywords
Discord Status code, title check, invite validation
TikTok Status code, title check, content analysis
Telegram Status code, title check, content analysis

Real Output Example

```
[BROKEN-INSTAGRAM] https://instagram.com/deleteduser -> https://site.com - HTTP 404
[ACTIVE-INSTAGRAM] https://instagram.com/activeuser -> https://site.com
[BROKEN-TWITTER] https://twitter.com/suspendedaccount -> https://site.com - Content Check: Error keywords found
[ACTIVE-TWITTER] https://twitter.com/realuser -> https://site.com
[BROKEN-YOUTUBE] https://youtube.com/@deletedchannel -> https://site.com - HTTP 404
```

---

## Database & History

Database Features

· SQLite Storage - Lightweight, portable database
· Scan History - Track all past scans
· Timestamps - Record when each link was found
· Metadata - Store status, platform, response times
· Query Support - View and filter historical data

View History

```bash
# Show recent scans
python socmed.py --history

# Output example:
# 2026-07-07 10:30:45 | example.com | instagram | https://instagram.com/user
# 2026-07-07 10:30:46 | example.com | twitter | https://twitter.com/user
```

Database Schema

```sql
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    domain TEXT,
    status INTEGER,
    platform TEXT,
    link TEXT,
    server TEXT,
    response_time REAL
);
```

---

## Proxy Support

Proxy Configuration

SOCMED supports HTTP/HTTPS proxies with authentication:

```bash
# Basic proxy
python socmed.py -l domains.txt -all --proxy http://127.0.0.1:8080

# Authenticated proxy
python socmed.py -l domains.txt -all --proxy http://user:pass@127.0.0.1:8080

# HTTPS proxy
python socmed.py -l domains.txt -all --proxy https://127.0.0.1:8080
```

Proxy Configuration in config/config.yaml

```yaml
proxy:
  enabled: true
  type: http
  host: 127.0.0.1
  port: 8080
  username: "username"
  password: "password"
```

---

## Custom Rules 

YAML File Format

```yaml
- name: platform_name
  description: Optional description
  creator: YourName
  color: '#HEXCODE'
  regex:
    - 'regex_pattern_1'
    - 'regex_pattern_2'
```

Example custom_rules.yaml

```yaml
# Custom rules for additional platforms
- name: instagram
  description: Find Instagram profiles
  creator: CayberMods
  color: '#E4405F'
  regex:
    - 'instagram\.com\/([a-zA-Z0-9_\.]+)'
    - 'instagr\.am\/([a-zA-Z0-9_\.]+)'

- name: twitter
  description: Find Twitter profiles
  creator: CayberMods
  color: '#1DA1F2'
  regex:
    - 'twitter\.com\/([a-zA-Z0-9_]+)'
    - 'x\.com\/([a-zA-Z0-9_]+)'

- name: threads
  description: Find Threads profiles
  creator: CayberMods
  color: '#FF0080'
  regex:
    - 'threads\.net\/(@[a-zA-Z0-9_\.]+)'

- name: bluesky
  description: Find Bluesky profiles
  creator: CayberMods
  color: '#1185FE'
  regex:
    - 'bsky\.app\/profile\/([a-zA-Z0-9_\.]+)'
```

Using Custom Rules

```bash
# Scan with custom rules
python socmed.py -l domains.txt -custom custom_rules.yaml -all

# Verbose for debugging
python socmed.py -l domains.txt -custom custom_rules.yaml -v
```

---

## Color Support

True Color (24-bit)

Supported terminals:

· iTerm2
· VS Code Terminal
· Windows Terminal
· GNOME Terminal
· Konsole
· Kitty
· Alacritty
· WezTerm

256 Color Mode

Fallback for terminals that don't support True Color:

· xterm-256color
· Most SSH clients
· Legacy terminals

Test Color Support

```bash
python socmed.py --test-colors
```

Output:

```
Testing color support...
True color supported

Testing hex colors:
████ #FF0000 RGB(255, 0, 0)
████ #00FF00 RGB(0, 255, 0)
████ #0000FF RGB(0, 0, 255)
████ #FF00FF RGB(255, 0, 255)
████ #FFFF00 RGB(255, 255, 0)
████ #00FFFF RGB(0, 255, 255)
████ #FF6B6B RGB(255, 107, 107)
████ #4ECDC4 RGB(78, 205, 196)
```

---

## Results & Interpretation

Status Codes

Code Description
200 Website active, link found
301-302 Redirect, followed automatically
303 See Other redirect
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
500 Internal Server Error
502 Bad Gateway
503 Service Unavailable

---

## Troubleshooting

Connection Issues

```bash
# Increase timeout
python socmed.py -l domains.txt -all -t 30

# Reduce workers
python socmed.py -l domains.txt -all -w 5

# Use proxy
python socmed.py -l domains.txt -all --proxy http://127.0.0.1:8080
```

Color Issues

```bash
# Test color support
python socmed.py --test-colors

# Force 256 colors
export TERM=xterm-256color
python socmed.py -l domains.txt -all

# Disable colors
export NO_COLOR=1
python socmed.py -l domains.txt -all
```

YAML Issues

```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('custom_rules.yaml'))"

# Verbose mode for debugging
python socmed.py -l domains.txt -custom custom_rules.yaml -v
```

Rate Limiting

```bash
# Disable rate limiting
# Edit config/config.yaml: rate_limit.enabled: false

# Adjust rate limits
# Edit config/config.yaml: rate_limit.max_requests: 20
```

Database Issues

```bash
# Reset database
rm scans.db
python socmed.py -l domains.txt -all --db

# Check database
sqlite3 scans.db "SELECT * FROM scans;"
```

---

## Contributing

We warmly welcome contributions from the community!

How to Contribute

1. Fork the repository
2. Create a new branch: git checkout -b feature/AmazingFeature
3. Commit your changes: git commit -m 'Add AmazingFeature'
4. Push to the branch: git push origin feature/AmazingFeature
5. Open a Pull Request

Areas That Need Contribution

· Bug fixes & issue reporting
· New features & enhancements
· Documentation & tutorials
· UI/UX improvements
· Performance optimization
· Security improvements
· New platform support

---

## Disclaimer

```
IMPORTANT: This tool was created for EDUCATIONAL purposes and ETHICAL SECURITY TESTING.
```

Use of this tool:

Permitted:

· On websites you have permission to test
· For legitimate purposes such as security auditing
· Must comply with applicable laws

Prohibited:

· For illegal or malicious activity
· For disrupting website operations
· For unauthorized access

The author is not responsible for:

· Use of this tool for illegal purposes
· Any damage or loss incurred
· Legal violations committed by users

By using this tool, you agree to:

· Take full responsibility for your use of the tool
· Comply with all applicable laws and regulations
· Use this tool ethically and responsibly

---

## Resources

Official Documentation

· Python Official Docs
· Requests Library
· Colorama Docs
· YAML Specification

Security Resources

· OWASP Broken Link Hijacking
· HackerOne Reports
· Bug Bounty Tips

---

## Acknowledgments

· Python Community - For an amazing programming language
· Requests Team - For a powerful HTTP library
· Colorama Developers - For terminal color support
· Security Researchers - For sharing knowledge and best practices
· Open Source Community - For tools and inspiration

---

Version History

Version Date Changes
2.0 2026-07-07 Major update: Database, Proxy, Broken Link Detection, Export formats
1.0 2026-01-01 Initial release with basic features

What's New in v2.0

· SQLite database for scan history
· Proxy support with authentication
· Advanced broken link detection
· JSON, CSV export formats
· Rate limiting
· User-Agent rotation
· Progress bar
· Enhanced color support
· Comprehensive logging
· Config file support

---

<p align="center">
  <b>Made with love for the cybersecurity community</b><br>
  <i>Stay safe, stay secure, stay ethical!</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Keep%20Calm-Code%20On-blue?style=flat-square">
  <img src="https://img.shields.io/badge/Stay%20Ethical-Hack%20Responsibly-green?style=flat-square">
</p>