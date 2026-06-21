
<div align="center">
<h1>SOCMED - Social Media Link Finder</h1>
</div>
<div align="center">
<img src="img/icon.png">
</div>
<p align="center">
  <img src="https://img.shields.io/badge/version-1.0-blue.svg?style=for-the-badge">
  <img src="https://img.shields.io/badge/python-3.6+-green.svg?style=for-the-badge">
  <img src="https://img.shields.io/badge/license-MIT-red.svg?style=for-the-badge">
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20windows-lightgrey?style=for-the-badge">
</p>

<p align="center">
  <b>Advanced Social Media Link Discovery Tool for Security Research</b><br>
  <i>Find broken links and potential hijacking vulnerabilities across 15+ platforms</i>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Custom Rules](#custom-rules-yaml)
- [Color Support](#color-support)
- [Results & Interpretation](#results--interpretation)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [Resources](#resources)
- [Acknowledgments](#acknowledgments)

---

## Overview

**SOCMED** is an advanced tool for discovering and analyzing social media links on websites. It is specifically designed to help cybersecurity professionals identify potential **Broken Link Hijacking** vulnerabilities.

### What is Broken Link Hijacking?

**Broken Link Hijacking** is an exploitation technique where an attacker takes advantage of social media links that are no longer active (broken/dead links). When a website has links to a social media account that has been deleted or deactivated:

- An attacker can re-register that username
- Hijack the website's visitor traffic
- Carry out phishing or further attacks
- Damage the company's reputation

### Use Cases

- ✓ Security auditing & penetration testing
- ✓ OSINT (Open Source Intelligence) gathering
- ✓ Brand protection monitoring
- ✓ Vulnerability assessment
- ✓ Digital footprint analysis

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Platform** | Supports 15+ social media platforms including Instagram, Telegram, YouTube, TikTok, Twitter/X |
| **Hex Color Support** | Terminal display with custom colors (True Color & 256 color) |
| **Concurrent Processing** | Multi-threaded processing for maximum speed |
| **Custom Rules** | Supports YAML files for custom search rules |
| **Verbose Mode** | Detailed information for debugging and analysis |
| **Export Results** | Save scan results in text format |
| **Redirect Handling** | Automatically follows redirects to find hidden links |
| **Selective Scanning** | Choose specific platforms or scan all |

---

## Installation

### Prerequisites

```bash
# Python 3.6 or later
python --version

# Install pip
pip --version
```

## Install Dependencies

```bash
# Clone repository
git clone https://github.com/CayberMods/SocMed.git
cd SocMed

# Install requirements
pip install -r requirements.txt
```

```bash
python socmed.py -l <domains.txt> [OPTIONS]
```

## Usage Examples

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

Full Options

```bash
python socmed.py -l domains.txt -all -o results.txt -v -t 15 -w 30
```

Full Parameter List
```bash
Parameter Shorthand Description Default
--list -l Domain list file (required)
--output -o Output results file
--timeout -t Request timeout (seconds) 10
--workers -w Number of concurrent workers 20
--verbose -v Verbose mode False
--test-colors - Test color support
--instagram -ig Scan Instagram False
--telegram -tele Scan Telegram False
--youtube -yt Scan YouTube False
--tiktok -tt Scan TikTok False
--twitter -tw Scan Twitter/X False
--all -all Scan all platforms False
--custom-method -custom Custom rules YAML file
```

Supported Platforms
```bash
Platform Flag Detection Pattern
Instagram -ig instagram.com/[username]
Telegram -tele t.me/[username]
YouTube -yt youtube.com/@[channel]
TikTok -tt tiktok.com/@[username]
Twitter/X -tw twitter.com/[username]
Facebook -fb facebook.com/[username]
LinkedIn -in linkedin.com/in/[username]
GitHub -gh github.com/[username]
Reddit -rd reddit.com/user/[username]
Discord -dc discord.gg/[invite]
Spotify -sp open.spotify.com/[id]
Medium -md medium.com/@[username]
Twitch -tc twitch.tv/[username]
```
---

## Custom Rules (YAML)

YAML File Format

```yaml
- name: instagram
  description: Find Instagram profiles # optional
  creator: CayberMods # optional
  color: '#E4405F' # optional
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

- name: youtube
  description: Find YouTube profiles
  creator: CayberMods
  color: '#FF0000'
  regex:
    - 'youtube\.com\/(?:c|channel|user|@)([a-zA-Z0-9_\.\-]+)'
    - 'youtu\.be\/([a-zA-Z0-9_\-]+)'

- name: tiktok
  description: Find TikTok profiles
  creator: CayberMods
  color: '#885630'
  regex:
    - 'tiktok\.com\/(?:@)([a-zA-Z0-9_\.]+)'
    - 'vm\.tiktok\.com\/([a-zA-Z0-9]+)'
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

- ✓ iTerm2
- ✓ VS Code Terminal
- ✓ Windows Terminal
- ✓ GNOME Terminal
- ✓ Konsole
- ✓ Kitty
- ✓ Alacritty

256 Color Mode

Fallback for terminals that don't support True Color:

- ✓ xterm-256color
- ✓ Most SSH clients
- ✓ Legacy terminals

Test Color Support

```bash
python socmed.py -l test.txt --test-colors
```

Output:

```
Testing color support...
✓ True color supported

Testing hex colors:
████ #FF0000 RGB(255, 0, 0)
████ #00FF00 RGB(0, 255, 0)
████ #0000FF RGB(0, 0, 255)
```

---

## Results & Interpretation

Status Codes
```bash
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
```
Output Format

```
[STATUS] WEBSITE [PLATFORM] LINK
```

Real Output Example

```bash
[200] https://example.com [INSTAGRAM] https://instagram.com/companyname
[200] https://example.com [TELEGRAM] https://t.me/companychannel
[301] https://old.example.com -> https://new.example.com [TWITTER] https://twitter.com/company
[200] https://example.com [YOUTUBE] https://youtube.com/@companychannel
[404] https://broken.example.com [LINKEDIN] https://linkedin.com/in/deletedprofile
```

Summary Report

```
[INF] Summary Report
[INF] Total Domains: 150
[INF] Total Links Found: 45

[INF] Platform Statistics:
    INSTAGRAM: 12
    TWITTER: 8
    YOUTUBE: 6
    TELEGRAM: 5
    LINKEDIN: 4
    GITHUB: 3
    FACEBOOK: 3
    TIKTOK: 2
    REDDIT: 2

[RES] Found Links:
[200] https://site.com [INSTAGRAM] https://instagram.com/username
[200] https://site.com [TWITTER] https://twitter.com/username
[404] https://site.com [LINKEDIN] https://linkedin.com/in/deleted
```

---

## Troubleshooting

Connection Issues

```bash
# Increase timeout
python socmed.py -l domains.txt -all -t 30

# Reduce workers
python socmed.py -l domains.txt -all -w 5

# Use a different User-Agent (edit in code)
```

Color Issues

```bash
# Test color support
python socmed.py -l test.txt --test-colors

# Force 256 colors
export TERM=xterm-256color
python socmed.py -l domains.txt -all
```

YAML Issues

```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('custom_rules.yaml'))"

# Verbose mode for debugging
python socmed.py -l domains.txt -custom custom_rules.yaml -v
```

---

## Best Practices

Ethical Usage

1. Get Permission - Only test websites you have permission to test
2. Respect Rate Limits - Avoid aggressive scanning
3. Use Reasonable Timeouts - Avoid overloading the server
4. Verify Manually - All results should be manually verified
5. Document Findings - Record all potential vulnerabilities

Vulnerability Reporting

If you find a broken link that could be exploited:

1. Document it with screenshots
2. Report it to the website owner
3. Recommend a fix
4. Monitor the status for changes

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

- Bug fixes & issue reporting
- New features & enhancements
- Documentation & tutorials
- UI/UX improvements
- Performance optimization
- Security improvements

---

## Disclaimer
```bash
IMPORTANT: This tool was created for EDUCATIONAL purposes and ETHICAL SECURITY TESTING.
```

Use of this tool:

1. ✓ Only on websites you have permission to test
2. ✓ Only for legitimate purposes such as security auditing
3. ✓ Must comply with applicable laws
4. ❌ PROHIBITED for illegal or malicious activity
5. ❌ PROHIBITED for disrupting website operations

The author is not responsible for:

- Use of this tool for illegal purposes
- Any damage or loss incurred
- Legal violations committed by users

By using this tool, you agree to:

- Take full responsibility for your use of the tool
- Comply with all applicable laws and regulations
- Use this tool ethically and responsibly

---
## Resources

- Python Official Docs
- Requests Library
- Colorama Docs
- YAML Specification

---

## Acknowledgments

- Python Community - For an amazing programming language
- Requests Team - For a powerful HTTP library
- Colorama Developers - For terminal color support
- Security Researchers - For sharing knowledge and best practices

---

<p align="center">
  <b>Made with ❤️ for the cybersecurity community</b><br>
  <i>Stay safe, stay secure, stay ethical!</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Keep%20Calm-Code%20On-blue?style=flat-square">
  <img src="https://img.shields.io/badge/Stay%20Ethical-Hack%20Responsibly-green?style=flat-square">
</p>
