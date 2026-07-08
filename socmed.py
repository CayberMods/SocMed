#!/usr/bin/env python3
"""
SOCMED - By CayberMods V2.0
"""
import requests
import re
import sys
import argparse
import time
import yaml
import os
import json
import csv
import sqlite3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style, Back
import threading
from urllib.parse import urlparse
import random
from modular.banner import print_banner
from modular.broken_checker import check_broken_link, PLATFORM_CHECKERS

init(autoreset=True)

print_lock = threading.Lock()

def safe_print(message):
    with print_lock:
        print(message)

class LoadingAnimation:
    
    @staticmethod
    def loading_bar(iteration, total, prefix='', suffix='', length=40, fill='█'):
        percent = 100 * (iteration / float(total))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        return f'\r{prefix} |{bar}| {percent:.1f}% {suffix}'
    
    @staticmethod
    def spinner():
        symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        for symbol in symbols:
            yield symbol

class ColorUtils:
    @staticmethod
    def hex_to_ansi(hex_color, is_background=False):
        if not hex_color or not hex_color.startswith('#'):
            return None
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            if ColorUtils.supports_true_color():
                if is_background:
                    return f"\033[48;2;{r};{g};{b}m"
                else:
                    return f"\033[38;2;{r};{g};{b}m"
            else:
                return ColorUtils.rgb_to_256(r, g, b, is_background)
        except:
            return None
    
    @staticmethod
    def rgb_to_256(r, g, b, is_background=False):
        if r == g == b:
            gray = round(r / 255 * 23)
            if is_background:
                return f"\033[48;5;{232 + gray}m"
            return f"\033[38;5;{232 + gray}m"
        r6 = round(r / 255 * 5)
        g6 = round(g / 255 * 5)
        b6 = round(b / 255 * 5)
        color_index = 16 + (r6 * 36) + (g6 * 6) + b6
        if is_background:
            return f"\033[48;5;{color_index}m"
        return f"\033[38;5;{color_index}m"
    
    @staticmethod
    def supports_true_color():
        term = os.environ.get('TERM', '')
        colorterm = os.environ.get('COLORTERM', '')
        if 'truecolor' in colorterm.lower() or '24bit' in colorterm.lower():
            return True
        if '256' in term:
            return True
        terminal_indicators = ['VSCODE_PID', 'TERM_PROGRAM', 'WT_SESSION', 'KONSOLE_VERSION', 'GNOME_TERMINAL_SCREEN', 'TMUX', 'KITTY', 'ALACRITTY']
        for indicator in terminal_indicators:
            if indicator in os.environ:
                return True
        return False

    @staticmethod
    def hex_to_rgb(hex_color):
        if not hex_color or not hex_color.startswith('#'):
            return None
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except:
            return None

class DatabaseManager:
    
    def __init__(self, db_path="scans.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                domain TEXT,
                status TEXT,
                platform TEXT,
                link TEXT,
                server TEXT,
                response_time REAL
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_scan(self, results):
        if not results:
            return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        for result in results:
            if result.get('link') and result['link'] not in ['Not Found', 'Error']:
                try:
                    cursor.execute('''
                        INSERT INTO scans (timestamp, domain, status, platform, link, server, response_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        timestamp,
                        result.get('website', ''),
                        str(result.get('status', '0')),
                        result.get('platform', ''),
                        result.get('link', ''),
                        result.get('server', ''),
                        result.get('response_time', 0)
                    ))
                except Exception as e:
                    print(f"[DEBUG] Save error: {e}")
        
        conn.commit()
        conn.close()
    
    def get_history(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, domain, platform, link, status
            FROM scans
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

class ProxyManager:
     
    def __init__(self, config=None):
        self.config = config or {}
        self.proxies = {}
        self.enabled = self.config.get('enabled', False)
        
        if self.enabled:
            proxy_type = self.config.get('type', 'http')
            host = self.config.get('host', '127.0.0.1')
            port = self.config.get('port', 8080)
            username = self.config.get('username', '')
            password = self.config.get('password', '')
            
            proxy_url = f"{proxy_type}://"
            if username and password:
                proxy_url += f"{username}:{password}@"
            proxy_url += f"{host}:{port}"
            
            self.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
    
    def get_proxies(self):
        return self.proxies if self.enabled else None

class SocMedChecker:
    def __init__(self, timeout=10, max_workers=20, verbose=False, quiet=False, config=None):
        self.timeout = timeout
        self.max_workers = max_workers
        self.verbose = verbose
        self.quiet = quiet
        self.config = config or {}
        self.results = []
        self.total_found = 0
        self.stats = {}
        self.lock = threading.Lock()
        self.custom_rules = []
        self.platforms = {}
        self.color_cache = {}
        self.broken_links = []
        self.active_links = []
        self.completed_count = 0
        self.total_domains = 0
        self.error_count = 0
        
        self.session = requests.Session()
        proxy_manager = ProxyManager(self.config.get('proxy', {}))
        if proxy_manager.enabled:
            self.session.proxies.update(proxy_manager.get_proxies())
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[INF] Proxy enabled: {self.config['proxy']['type']}://{self.config['proxy']['host']}:{self.config['proxy']['port']}{Fore.RESET}{Style.RESET_ALL}")
        
        self.user_agents = self.config.get('user_agents', [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ])
        
        self.rate_limit = self.config.get('rate_limit', {})
        self.request_count = 0
        self.rate_limit_start = time.time()
        self.auto_adjust = self.rate_limit.get('auto_adjust', True)
        self.rate_limit_warning_shown = False
        
        self.db = DatabaseManager('scans.db')
        
        self.color_map = {
            'instagram': Fore.MAGENTA,
            'telegram': Fore.CYAN,
            'youtube': Fore.RED,
            'tiktok': Fore.MAGENTA,
            'twitter': Fore.BLUE,
            'facebook': Fore.BLUE,
            'linkedin': Fore.BLUE,
            'github': Fore.WHITE,
            'reddit': Fore.CYAN,
            'discord': Fore.MAGENTA,
            'spotify': Fore.GREEN,
            'medium': Fore.WHITE,
            'twitch': Fore.MAGENTA,
            'threads': Fore.CYAN,
            'pinterest': Fore.RED,
            'snapchat': Fore.YELLOW,
            'onlyfans': Fore.RED
        }
        
        self.platform_patterns = {
            'instagram': [
                r'(?:https?:)?\/\/(?:www\.)?instagram\.com\/([a-zA-Z0-9_\.]+)',
                r'instagram\.com\/([a-zA-Z0-9_\.]+)',
                r'instagr\.am\/([a-zA-Z0-9_\.]+)',
            ],
            'telegram': [
                r'(?:https?:)?\/\/(?:t\.me|telegram\.org)\/([a-zA-Z0-9_\.]+)',
                r't\.me\/([a-zA-Z0-9_\.]+)',
            ],
            'youtube': [
                r'(?:https?:)?\/\/(?:www\.)?youtube\.com\/(?:c|channel|user|@)([a-zA-Z0-9_\.\-]+)',
                r'youtube\.com\/(?:c|channel|user|@)([a-zA-Z0-9_\.\-]+)',
                r'youtu\.be\/([a-zA-Z0-9_\-]+)',
            ],
            'tiktok': [
                r'(?:https?:)?\/\/(?:www\.)?tiktok\.com\/(?:@)([a-zA-Z0-9_\.]+)',
                r'tiktok\.com\/(?:@)([a-zA-Z0-9_\.]+)',
                r'vm\.tiktok\.com\/([a-zA-Z0-9]+)',
            ],
            'twitter': [
                r'(?:https?:)?\/\/(?:www\.)?(?:twitter\.com|x\.com)\/([a-zA-Z0-9_]+)',
                r'twitter\.com\/([a-zA-Z0-9_]+)',
                r'x\.com\/([a-zA-Z0-9_]+)',
            ],
            'facebook': [
                r'(?:https?:)?\/\/(?:www\.)?facebook\.com\/([a-zA-Z0-9_\.]+)',
                r'facebook\.com\/([a-zA-Z0-9_\.]+)',
                r'fb\.com\/([a-zA-Z0-9_\.]+)',
            ],
            'linkedin': [
                r'(?:https?:)?\/\/(?:www\.)?linkedin\.com\/(?:in|company)\/([a-zA-Z0-9_\-]+)',
                r'linkedin\.com\/(?:in|company)\/([a-zA-Z0-9_\-]+)',
            ],
            'github': [
                r'(?:https?:)?\/\/(?:www\.)?github\.com\/([a-zA-Z0-9_\-]+)',
                r'github\.com\/([a-zA-Z0-9_\-]+)',
            ],
            'reddit': [
                r'(?:https?:)?\/\/(?:www\.)?reddit\.com\/(?:user|r)\/([a-zA-Z0-9_\-]+)',
                r'reddit\.com\/(?:user|r)\/([a-zA-Z0-9_\-]+)',
            ],
            'discord': [
                r'(?:https?:)?\/\/(?:www\.)?discord\.(?:com|gg)\/(?:invite\/)?([a-zA-Z0-9_\-]+)',
                r'discord\.(?:com|gg)\/(?:invite\/)?([a-zA-Z0-9_\-]+)',
            ],
            'spotify': [
                r'(?:https?:)?\/\/(?:open\.)?spotify\.com\/(?:artist|album|playlist|track)\/([a-zA-Z0-9]+)',
                r'spotify\.com\/(?:artist|album|playlist|track)\/([a-zA-Z0-9]+)',
            ],
            'medium': [
                r'(?:https?:)?\/\/(?:www\.)?medium\.com\/(?:@)?([a-zA-Z0-9_\-\.]+)',
                r'medium\.com\/(?:@)?([a-zA-Z0-9_\-\.]+)',
            ],
            'twitch': [
                r'(?:https?:)?\/\/(?:www\.)?twitch\.tv\/([a-zA-Z0-9_]+)',
                r'twitch\.tv\/([a-zA-Z0-9_]+)',
            ],
        }
        
        self.platform_shortcuts = {
            'ig': 'instagram',
            'tele': 'telegram',
            'yt': 'youtube',
            'tt': 'tiktok',
            'tw': 'twitter',
            'fb': 'facebook',
            'in': 'linkedin',
            'gh': 'github',
            'rd': 'reddit',
            'dc': 'discord',
            'sp': 'spotify',
            'md': 'medium',
            'tc': 'twitch'
        }
        
    def load_config(self, config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config:
                    self.config.update(config)
                    return True
        except Exception as e:
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] Loading config: {e}{Fore.RESET}{Style.RESET_ALL}")
        return False
    
    def load_custom_rules(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
                if isinstance(rules, list):
                    self.custom_rules = rules
                else:
                    self.custom_rules = [rules]
                return True
        except Exception as e:
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] Loading custom rules: {e}{Style.RESET_ALL}")
            return False
    
    def check_rate_limit(self):
        if not self.rate_limit.get('enabled', True):
            return True
        
        current_time = time.time()
        time_window = self.rate_limit.get('time_window', 60)
        max_requests = self.rate_limit.get('max_requests', 50)
        
        if current_time - self.rate_limit_start > time_window:
            self.request_count = 0
            self.rate_limit_start = current_time
        
        if self.request_count >= max_requests:
            wait_time = time_window - (current_time - self.rate_limit_start)
            if wait_time > 0 and not self.rate_limit_warning_shown:
                self.rate_limit_warning_shown = True
                sys.stdout.write('\r' + ' ' * 80 + '\r')
                sys.stdout.flush()
                if not self.quiet:
                    safe_print(f"\n{Style.BRIGHT}{Fore.YELLOW}[WRN] Rate limit reached, waiting {wait_time:.1f}s{Fore.RESET}{Style.RESET_ALL}")
                time.sleep(wait_time)
                self.request_count = 0
                self.rate_limit_start = time.time()
                self.rate_limit_warning_shown = False
                self.update_progress()
            return True
        
        self.request_count += 1
        return True
    
    def update_progress(self):
        if self.total_domains > 0:
            bar = LoadingAnimation.loading_bar(
                self.completed_count, 
                self.total_domains,
                prefix=f'{Style.BRIGHT}{Fore.CYAN}Progress{Fore.RESET}{Style.RESET_ALL}',
                suffix=f'{Style.BRIGHT}{Fore.GREEN}{self.completed_count}/{self.total_domains}\n{Fore.RESET}{Style.RESET_ALL}'
            )
            sys.stdout.write('\r' + bar)
            sys.stdout.flush()
    
    def get_platform_color(self, platform, is_background=False):
        cache_key = f"{platform}_{is_background}"
        if cache_key in self.color_cache:
            return self.color_cache[cache_key]
        
        color = self.color_map.get(platform.lower(), Fore.GREEN if not is_background else Back.GREEN)
        self.color_cache[cache_key] = color
        return color
    
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def find_social_links(self, html, domain):
        links = {}
        
        for platform, patterns in self.platform_patterns.items():
            if not self.platforms.get('all', False) and not self.platforms.get(platform, False):
                continue
            
            found = set()
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    username = match.split('/')[0].split('?')[0].split('#')[0]
                    if username and len(username) > 1:
                        link = self.build_platform_link(platform, username)
                        if link:
                            found.add(link)
            
            if found:
                links[platform] = list(found)
        
        for rule in self.custom_rules:
            platform = rule.get('name', '').lower()
            if not platform:
                continue
            
            if platform in self.platforms and not self.platforms.get(platform, True) and not self.platforms.get('all', False):
                continue
            
            found = set()
            for pattern in rule.get('regex', []):
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match else ''
                    username = str(match).split('/')[0].split('?')[0].split('#')[0]
                    if username and len(username) > 1:
                        if '://' in username or username.startswith('http'):
                            link = username
                        else:
                            link = f"https://{platform}.com/{username}"
                        found.add(link)
            
            if found:
                links[platform] = list(found)
        
        return links
    
    def build_platform_link(self, platform, username):
        platform_map = {
            'instagram': f"https://instagram.com/{username}",
            'telegram': f"https://t.me/{username}",
            'youtube': f"https://youtube.com/@{username}" if not username.startswith('@') else f"https://youtube.com/{username}",
            'tiktok': f"https://tiktok.com/@{username}",
            'twitter': f"https://twitter.com/{username}",
            'facebook': f"https://facebook.com/{username}",
            'linkedin': f"https://linkedin.com/in/{username}",
            'github': f"https://github.com/{username}",
            'reddit': f"https://reddit.com/user/{username}",
            'discord': f"https://discord.gg/{username}",
            'spotify': f"https://open.spotify.com/playlist/{username}",
            'medium': f"https://medium.com/@{username}",
            'twitch': f"https://twitch.tv/{username}"
        }
        return platform_map.get(platform)
    
    def check_domain(self, domain):
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
        
        if not self.check_rate_limit():
            return
        
        try:
            start_time = time.time()
            
            self.session.headers.update({
                'User-Agent': self.get_random_user_agent()
            })
            
            response = self.session.get(domain, timeout=self.timeout, allow_redirects=True)
            status_code = response.status_code
            response_time = time.time() - start_time
            
            server = response.headers.get('Server', 'Unknown')
            
            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.flush()
            
            if status_code == 200:
                if not self.quiet:
                    safe_print(f"{Style.BRIGHT}{Fore.GREEN}[{status_code}] {Fore.CYAN}{domain}{Fore.RESET} | {server} | {response_time:.2f}s{Style.RESET_ALL}")
                
                if self.verbose:
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', response.text, re.IGNORECASE)
                    title = title_match.group(1).strip() if title_match else 'No Title'
                    if not self.quiet:
                        safe_print(f"{Style.BRIGHT}{Fore.WHITE}    Title: {title}{Fore.RESET}{Style.RESET_ALL}")
                
                social_links = self.find_social_links(response.text, domain)
                
                with self.lock:
                    if social_links:
                        for platform, links in social_links.items():
                            for link in links:
                                result = {
                                    'status': status_code,
                                    'website': domain,
                                    'platform': platform,
                                    'link': link,
                                    'server': server,
                                    'response_time': response_time
                                }
                                self.results.append(result)
                                self.total_found += 1
                                self.stats[platform] = self.stats.get(platform, 0) + 1
                                
                                if not self.quiet:
                                    platform_color = self.get_platform_color(platform)
                                    safe_print(f"{Style.BRIGHT}{platform_color}    [{platform.upper()}] {link}{Fore.RESET}{Style.RESET_ALL}")
                    else:
                        result = {
                            'status': status_code,
                            'website': domain,
                            'platform': 'none',
                            'link': 'Not Found',
                            'server': server,
                            'response_time': response_time
                        }
                        self.results.append(result)
                        
            elif 300 <= status_code < 400:
                location = response.headers.get('Location', '')
                if not self.quiet:
                    safe_print(f"{Style.BRIGHT}{Fore.YELLOW}[{status_code}] {Fore.CYAN}{domain}{Fore.RESET} -> {location} | {response_time:.2f}s{Style.RESET_ALL}")
                
                if location:
                    try:
                        redirect_resp = self.session.get(location, timeout=self.timeout)
                        if redirect_resp.status_code == 200:
                            social_links = self.find_social_links(redirect_resp.text, domain)
                            with self.lock:
                                for platform, links in social_links.items():
                                    for link in links:
                                        result = {
                                            'status': 200,
                                            'website': domain,
                                            'platform': platform,
                                            'link': link
                                        }
                                        self.results.append(result)
                                        self.total_found += 1
                                        self.stats[platform] = self.stats.get(platform, 0) + 1
                                        if not self.quiet:
                                            platform_color = self.get_platform_color(platform)
                                            safe_print(f"{Style.BRIGHT}{platform_color}    [{platform.upper()}] {link}{Fore.RESET}{Style.RESET_ALL}")
                    except:
                        pass
            else:
                if not self.quiet:
                    safe_print(f"{Style.BRIGHT}{Fore.RED}[{status_code}] {Fore.CYAN}{domain}{Fore.RESET} | {server} | {response_time:.2f}s{Style.RESET_ALL}")
                with self.lock:
                    result = {
                        'status': status_code,
                        'website': domain,
                        'platform': 'error',
                        'link': 'Error',
                        'server': server,
                        'response_time': response_time
                    }
                    self.results.append(result)
                    
        except requests.exceptions.Timeout:
            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.flush()
            if self.verbose and not self.quiet:
                safe_print(f"{Style.DIM}{Fore.YELLOW}[!] Timeout: {domain}{Fore.RESET}{Style.RESET_ALL}")
            with self.lock:
                self.error_count += 1
                result = {
                    'status': 'Timeout',
                    'website': domain,
                    'platform': 'error',
                    'link': 'Error',
                    'server': 'Unknown',
                    'response_time': self.timeout
                }
                self.results.append(result)
            
        except requests.exceptions.ConnectionError:
            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.flush()
            if self.verbose and not self.quiet:
                safe_print(f"{Style.DIM}{Fore.RED}[!] Connection Error: {domain}{Fore.RESET}{Style.RESET_ALL}")
            with self.lock:
                self.error_count += 1
                result = {
                    'status': 'Connection Error',
                    'website': domain,
                    'platform': 'error',
                    'link': 'Error',
                    'server': 'Unknown',
                    'response_time': 0
                }
                self.results.append(result)
            
        except Exception as e:
            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.flush()
            if self.verbose and not self.quiet:
                safe_print(f"{Style.DIM}{Fore.RED}[!] Error: {domain} - {str(e)}{Fore.RESET}{Style.RESET_ALL}")
            with self.lock:
                self.error_count += 1
                result = {
                    'status': 'Error',
                    'website': domain,
                    'platform': 'error',
                    'link': 'Error',
                    'server': 'Unknown',
                    'response_time': 0
                }
                self.results.append(result)
        
        with self.lock:
            self.completed_count += 1
            self.update_progress()
    
    def process_domains(self, domains):
        self.total_domains = len(domains)
        if not self.quiet:
            safe_print(f"\n{Style.BRIGHT}{Fore.CYAN}[INF] Processing {len(domains)} domains with {self.max_workers} workers{Fore.RESET}{Style.RESET_ALL}")
            safe_print("")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.check_domain, domain): domain for domain in domains}
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass
        
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        sys.stdout.flush()
        if not self.quiet:
            safe_print("")
        
        self.print_error_summary()
        self.check_broken_links()
        self.export_broken_links("broken_links.txt")
    
    def print_error_summary(self):
        if self.error_count > 0 and not self.quiet:
            safe_print(f"\n{Style.BRIGHT}{Fore.YELLOW}[!] {self.error_count} domains failed{Fore.RESET}{Style.RESET_ALL}")
            if self.verbose:
                errors = [r for r in self.results if r.get('status') in ['Timeout', 'Connection Error', 'Error']]
                for error in errors[:5]:
                    safe_print(f"{Style.DIM}  - {error['website']} ({error['status']}){Fore.RESET}{Style.RESET_ALL}")
                if len(errors) > 5:
                    safe_print(f"{Style.DIM}  ... and {len(errors)-5} more{Fore.RESET}{Style.RESET_ALL}")
    
    def check_broken_links(self):       
        broken_links = []
        active_links = []
        results = [r for r in self.results if r.get('link') and r['link'] not in ['Not Found', 'Error']]
        
        if not results:
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.YELLOW}[WRN] No links to check for broken status{Fore.RESET}{Style.RESET_ALL}")
            return [], []
        
        if not self.quiet:
            safe_print(f"\n{Style.BRIGHT}{Fore.CYAN}[INF] Checking {len(results)} links for broken status...{Fore.RESET}{Style.RESET_ALL}")
        
        for result in results:
            platform = result.get('platform', '').lower()
            url = result['link']        
            status, detail = check_broken_link(platform, url)
            
            if status == "BROKEN":
                broken_links.append({
                    'platform': platform,
                    'url': url,
                    'source': result.get('website', ''),
                    'detail': detail
                })
                if not self.quiet:
                    safe_print(f"{Style.BRIGHT}{Fore.RED}[BROKEN-{platform.upper()}] {url} -> {result.get('website', '')} - {detail}{Fore.RESET}{Style.RESET_ALL}")
            elif status == "ACTIVE":
                active_links.append({
                    'platform': platform,
                    'url': url,
                    'source': result.get('website', '')
                })
                if not self.quiet:
                    safe_print(f"{Style.BRIGHT}{Fore.GREEN}[ACTIVE-{platform.upper()}] {url} -> {result.get('website', '')}{Fore.RESET}{Style.RESET_ALL}")
            else:
                if not self.quiet:
                    safe_print(f"{Style.BRIGHT}{Fore.YELLOW}[ERROR-{platform.upper()}] {url} -> {result.get('website', '')} - {detail}{Fore.RESET}{Style.RESET_ALL}")
            
            time.sleep(0.3)
        
        if not self.quiet:
            safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[INF] Active links: {len(active_links)}{Fore.RESET}{Style.RESET_ALL}")
            safe_print(f"{Style.BRIGHT}{Fore.RED}[INF] Broken links: {len(broken_links)}{Fore.RESET}{Style.RESET_ALL}")
        
        self.broken_links = broken_links
        self.active_links = active_links
        
        return broken_links, active_links

    def export_broken_links(self, filename="broken_links.txt"):       
        if not hasattr(self, 'broken_links'):
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.YELLOW}[WRN] No broken links data. Run check_broken_links() first.{Fore.RESET}{Style.RESET_ALL}")
            return
        
        if not self.broken_links:
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[INF] No broken links found{Fore.RESET}{Style.RESET_ALL}")
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("BROKEN SOCIAL MEDIA LINKS REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*70 + "\n\n")
                f.write(f"Total broken links: {len(self.broken_links)}\n\n")
                
                platform_groups = {}
                for link in self.broken_links:
                    platform = link['platform'].upper()
                    if platform not in platform_groups:
                        platform_groups[platform] = []
                    platform_groups[platform].append(link)
                
                for platform, links in sorted(platform_groups.items()):
                    f.write(f"\n[{platform}] ({len(links)} broken links)\n")
                    f.write("-"*50 + "\n")
                    for link in links:
                        f.write(f"  URL: {link['url']}\n")
                        f.write(f"  Source: {link['source']}\n")
                        f.write(f"  Reason: {link['detail']}\n\n")
            
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[INF] Broken links saved to: {filename}{Fore.RESET}{Style.RESET_ALL}")
            
        except Exception as e:
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] Export broken links: {e}{Fore.RESET}{Style.RESET_ALL}")
    
    def export_json(self, filename):
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'total_domains': len(self.results),
                'total_found': self.total_found,
                'stats': self.stats,
                'results': self.results,
                'broken_links': self.broken_links if hasattr(self, 'broken_links') else [],
                'active_links': self.active_links if hasattr(self, 'active_links') else []
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[INF] Exported to JSON: {filename}{Fore.RESET}{Style.RESET_ALL}")
            return True
        except Exception as e:
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] Export JSON: {e}{Fore.RESET}{Style.RESET_ALL}")
            return False
    
    def export_csv(self, filename):
        try:
            found_links = [r for r in self.results if r.get('link') and r['link'] not in ['Not Found', 'Error']]
            
            if not found_links:
                if not self.quiet:
                    safe_print(f"\n{Style.BRIGHT}{Fore.YELLOW}[WRN] No links to export to CSV{Fore.RESET}{Style.RESET_ALL}")
                return False
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Status', 'Website', 'Platform', 'Link', 'Server', 'Response Time', 'Broken Status'])
                
                for result in found_links:
                    broken_status = 'BROKEN' if any(b['url'] == result['link'] for b in self.broken_links) else 'ACTIVE'
                    writer.writerow([
                        result.get('status', ''),
                        result.get('website', ''),
                        result.get('platform', ''),
                        result.get('link', ''),
                        result.get('server', ''),
                        f"{result.get('response_time', 0):.2f}s",
                        broken_status
                    ])
            
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[INF] Exported to CSV: {filename}{Fore.RESET}{Style.RESET_ALL}")
            return True
        except Exception as e:
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] Export CSV: {e}{Fore.RESET}{Style.RESET_ALL}")
            return False
    
    def save_to_database(self):
        try:
            self.db.save_scan(self.results)
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[INF] Saved to database{Fore.RESET}{Style.RESET_ALL}")
        except Exception as e:
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] Save to database: {e}{Fore.RESET}{Style.RESET_ALL}")
    
    def print_summary(self):
        if self.quiet:
            return
        
        safe_print(f"\n{Style.BRIGHT}{Fore.CYAN}[INF] Summary Report{Fore.RESET}{Style.RESET_ALL}")
        safe_print(f"{Style.BRIGHT}{Fore.CYAN}[INF] Total Domains: {len(self.results)}{Fore.RESET}{Style.RESET_ALL}")
        safe_print(f"{Style.BRIGHT}{Fore.CYAN}[INF] Total Links Found: {self.total_found}{Fore.RESET}{Style.RESET_ALL}")
        
        if self.stats:
            safe_print(f"{Style.BRIGHT}{Fore.CYAN}[INF] Platform Statistics:{Fore.RESET}{Style.RESET_ALL}")
            for platform, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
                platform_color = self.get_platform_color(platform)
                safe_print(f"{Style.BRIGHT}{platform_color}       {platform.upper()}: {count}{Fore.RESET}{Style.RESET_ALL}")
        
        found_links = [r for r in self.results if r.get('link') and r['link'] not in ['Not Found', 'Error']]
        
        if found_links:
            safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[RES] Found Links:{Fore.RESET}{Style.RESET_ALL}")
            for result in found_links:
                platform_color = self.get_platform_color(result.get('platform', ''))
                is_broken = any(b['url'] == result['link'] for b in self.broken_links) if hasattr(self, 'broken_links') else False 
                
                if is_broken:
                    safe_print(f"{Style.BRIGHT}{platform_color}[BROKEN-{result.get('platform', '').upper()}] {result['link']} -> {result['website']} [{result['status']}]{Fore.RESET}{Style.RESET_ALL}")
                else:
                    safe_print(f"{Style.BRIGHT}{platform_color}[ACTIVE-{result.get('platform', '').upper()}] {result['link']} -> {result['website']} [{result['status']}]{Fore.RESET}{Style.RESET_ALL}")
        else:
            safe_print(f"\n{Style.BRIGHT}{Fore.YELLOW}[WRN] No social media links found{Fore.RESET}{Style.RESET_ALL}")
    
    def save_results(self, filename="results.txt"):
        if not self.results:
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.YELLOW}[!] No results to save{Fore.RESET}{Style.RESET_ALL}")
            return
        
        try:
            found_links = [r for r in self.results if r.get('link') and r['link'] not in ['Not Found', 'Error']]
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# SOCMED Checker Results\n")
                f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# " + "="*60 + "\n\n")
                f.write(f"Total Domains Checked: {len(self.results)}\n")
                f.write(f"Total Links Found: {len(found_links)}\n")
                
                if self.stats:
                    f.write("\nPlatform Statistics:\n")
                    for platform, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
                        f.write(f"  {platform.upper()}: {count}\n")
                
                f.write("\n" + "-"*60 + "\n\n")
                
                if found_links:
                    f.write("FOUND SOCIAL MEDIA LINKS:\n")
                    f.write("-"*40 + "\n")
                    for result in found_links:
                        is_broken = any(b['url'] == result['link'] for b in self.broken_links) if hasattr(self, 'broken_links') else False
                        status = "BROKEN" if is_broken else "ACTIVE"
                        f.write(f"[{result['status']}] {result['website']} [{result.get('platform', '').upper()}] {result['link']} [{status}]\n")
                    f.write(f"\n# Total found: {len(found_links)}\n")
                    
                    if hasattr(self, 'broken_links') and self.broken_links:
                        f.write(f"\n# Broken links: {len(self.broken_links)}\n")
                        for link in self.broken_links:
                            f.write(f"#   {link['url']} - {link['detail']}\n")
                else:
                    f.write("# No social media links found\n")
            
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[INF] Results saved to: {filename}{Fore.RESET}{Style.RESET_ALL}")
            
            self.save_to_database()
            
        except Exception as e:
            if not self.quiet:
                safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] Saving results: {e}{Fore.RESET}{Style.RESET_ALL}")

def load_domains(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return domains
    except FileNotFoundError:
        safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] File {filename} not found!{Fore.RESET}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] Loading file: {e}{Fore.RESET}{Style.RESET_ALL}")
        sys.exit(1)

def test_colors():
    safe_print(f"\n{Style.BRIGHT}{Fore.CYAN}Testing color support...{Style.RESET_ALL}")
    
    if ColorUtils.supports_true_color():
        safe_print(f"{Style.BRIGHT}{Fore.GREEN}✓ True color supported{Style.RESET_ALL}")
        
        test_colors = ['#FF0000', '#00FF00', '#0000FF', '#FF00FF', '#FFFF00', '#00FFFF', '#FF6B6B', '#4ECDC4']
        safe_print(f"{Style.BRIGHT}{Fore.CYAN}Testing hex colors:{Style.RESET_ALL}")
        for hex_color in test_colors:
            ansi = ColorUtils.hex_to_ansi(hex_color)
            if ansi:
                rgb = ColorUtils.hex_to_rgb(hex_color)
                safe_print(f"{ansi}████ {hex_color} RGB{rgb}{Style.RESET_ALL}")
    else:
        safe_print(f"{Style.BRIGHT}{Fore.YELLOW}⚠ True color not supported, using 256 color mode{Style.RESET_ALL}")
        
    try:
        import subprocess
        result = subprocess.run(['tput', 'colors'], capture_output=True, text=True)
        if result.returncode == 0:
            colors = int(result.stdout.strip())
            safe_print(f"{Style.BRIGHT}{Fore.GREEN}✓ {colors} colors available{Style.RESET_ALL}")
    except:
        pass

def main():
    parser = argparse.ArgumentParser(
        description='SOCMED - Social Media Link Finder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python socmed.py -l domains.txt -all
  python socmed.py -l domains.txt -ig -tele -yt -v
  python socmed.py -l domains.txt -custom custom.yaml -o results.json --json
  python socmed.py -l domains.txt -config config.yaml -all
  python socmed.py -l domains.txt --history

Platforms:
  -ig    Instagram    -tele  Telegram    -yt    YouTube
  -tt    TikTok       -tw    Twitter     -fb    Facebook
  -in    LinkedIn     -gh    GitHub      -rd    Reddit
  -dc    Discord      -sp    Spotify     -md    Medium
  -tc    Twitch       -all   All Platforms
        """
    )
    parser.add_argument('-l', '--list', help='File containing list of domains/subdomains')
    parser.add_argument('-o', '--output', help='Output file for results')
    parser.add_argument('-config', '--config', help='Configuration file (YAML)')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='Request timeout in seconds')
    parser.add_argument('-w', '--workers', type=int, default=20, help='Number of concurrent workers')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    parser.add_argument('--quiet', action='store_true', help='Quiet mode - hide errors and progress')
    parser.add_argument('--test-colors', action='store_true', help='Test terminal color support')
    
    parser.add_argument('--json', action='store_true', help='Export results to JSON')
    parser.add_argument('--csv', action='store_true', help='Export results to CSV')
    parser.add_argument('--db', action='store_true', help='Save results to database')
    parser.add_argument('--history', action='store_true', help='Show scan history')
    
    platform_group = parser.add_argument_group('Platforms')
    platform_group.add_argument('-ig', '--instagram', action='store_true', help='Check Instagram')
    platform_group.add_argument('-tele', '--telegram', action='store_true', help='Check Telegram')
    platform_group.add_argument('-yt', '--youtube', action='store_true', help='Check YouTube')
    platform_group.add_argument('-tt', '--tiktok', action='store_true', help='Check TikTok')
    platform_group.add_argument('-tw', '--twitter', action='store_true', help='Check Twitter/X')
    platform_group.add_argument('-fb', '--facebook', action='store_true', help='Check Facebook')
    platform_group.add_argument('-in', '--linkedin', action='store_true', help='Check LinkedIn')
    platform_group.add_argument('-gh', '--github', action='store_true', help='Check GitHub')
    platform_group.add_argument('-rd', '--reddit', action='store_true', help='Check Reddit')
    platform_group.add_argument('-dc', '--discord', action='store_true', help='Check Discord')
    platform_group.add_argument('-sp', '--spotify', action='store_true', help='Check Spotify')
    platform_group.add_argument('-md', '--medium', action='store_true', help='Check Medium')
    platform_group.add_argument('-tc', '--twitch', action='store_true', help='Check Twitch')
    platform_group.add_argument('-all', '--all', action='store_true', help='Check all platforms')
    
    parser.add_argument('-custom', '--custom-method', help='Custom YAML file with rules')
    parser.add_argument('--proxy', help='Proxy URL (e.g., http://user:pass@host:port)')
    
    args = parser.parse_args()
    
    if args.config:
        if not os.path.exists(args.config):
            safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] Config file not found: {args.config}{Fore.RESET}{Style.RESET_ALL}")
            sys.exit(1)
    
    if args.history:
        db = DatabaseManager('scans.db')
        history = db.get_history(50)
        safe_print(f"\n{Style.BRIGHT}{Fore.CYAN}Scan History:{Fore.RESET}{Style.RESET_ALL}")
        safe_print("-" * 80)
        if history:
            for entry in history:
                safe_print(f"{Style.BRIGHT}{Fore.GREEN}{entry[0]}{Fore.RESET} | {entry[1]} | {entry[2]} | {entry[3]} | {entry[4]}{Style.RESET_ALL}")
        else:
            safe_print(f"{Style.BRIGHT}{Fore.YELLOW}No history found. Run a scan first with -all option.{Fore.RESET}{Style.RESET_ALL}")
        return
    
    if args.test_colors:
        test_colors()
        return
    
    print_banner()
    
    platform_flags = [
        args.instagram, args.telegram, args.youtube, args.tiktok, 
        args.twitter, args.facebook, args.linkedin, args.github,
        args.reddit, args.discord, args.spotify, args.medium,
        args.twitch, args.all
    ]
    
    if not any(platform_flags):
        if not args.quiet:
            safe_print(f"\n{Style.BRIGHT}{Fore.YELLOW}[WRN] No platform specified. Auto-enabling -all mode{Fore.RESET}{Style.RESET_ALL}")
        args.all = True
    
    platforms = {'all': args.all}
    platform_names = ['instagram', 'telegram', 'youtube', 'tiktok', 'twitter', 
                     'facebook', 'linkedin', 'github', 'reddit', 'discord',
                     'spotify', 'medium', 'twitch']
    
    if args.all:
        for p in platform_names:
            platforms[p] = True
    else:
        for p in platform_names:
            platforms[p] = getattr(args, p, False)
    
    if not args.list:
        safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] No domain list provided. Use -l option{Fore.RESET}{Style.RESET_ALL}")
        sys.exit(1)
    
    domains = load_domains(args.list)
    if not args.quiet:
        safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[INF] Loaded {len(domains)} domains from {args.list}{Fore.RESET}{Style.RESET_ALL}")
    
    checker = SocMedChecker(
        timeout=args.timeout,
        max_workers=args.workers,
        verbose=args.verbose,
        quiet=args.quiet
    )
    
    if args.config:
        if checker.load_config(args.config):
            if not args.quiet:
                safe_print(f"{Style.BRIGHT}{Fore.GREEN}[INF] Loaded config from {args.config}{Fore.RESET}{Style.RESET_ALL}")
    
    checker.platforms = platforms
    
    if args.custom_method:
        if checker.load_custom_rules(args.custom_method):
            if not args.quiet:
                safe_print(f"{Style.BRIGHT}{Fore.GREEN}[INF] Loaded custom rules from {args.custom_method}{Fore.RESET}{Style.RESET_ALL}")
            for rule in checker.custom_rules:
                platform = rule.get('name', '').lower()
                if platform:
                    platforms[platform] = True
                    color = rule.get('color', '')
                    if color and color.startswith('#') and not args.quiet:
                        rgb = ColorUtils.hex_to_rgb(color)
                        if rgb:
                            color_ansi = ColorUtils.hex_to_ansi(color)
                            safe_print(f"{Style.BRIGHT}{Fore.CYAN}[INF] Custom platform '{platform}' using color {color_ansi}████{Style.RESET_ALL} {color} RGB{rgb}{Style.RESET_ALL}")
    
    if args.proxy:
        checker.session.proxies.update({
            'http': args.proxy,
            'https': args.proxy
        })
        if not args.quiet:
            safe_print(f"{Style.BRIGHT}{Fore.GREEN}[INF] Using proxy: {args.proxy}{Fore.RESET}{Style.RESET_ALL}")
    
    if not args.quiet:
        enabled = [p for p, v in platforms.items() if v and p != 'all']
        if enabled:
            safe_print(f"{Style.BRIGHT}{Fore.CYAN}[INF] Platforms: {', '.join(enabled)}{Fore.RESET}{Style.RESET_ALL}")
        if args.all:
            safe_print(f"{Style.BRIGHT}{Fore.CYAN}[INF] Platforms: ALL{Fore.RESET}{Style.RESET_ALL}")
    
    start_time = time.time()
    checker.process_domains(domains)
    
    checker.print_summary()
    
    if args.output:
        base_name = os.path.splitext(args.output)[0]
        
        if args.json:
            checker.export_json(f"{base_name}.json")
        elif args.csv:
            checker.export_csv(f"{base_name}.csv")
        else:
            checker.save_results(args.output)
    else:
        checker.save_results("url_results.txt")
    
    if args.json:
        checker.export_json("results.json")
    if args.csv:
        checker.export_csv("results.csv")
    if args.db:
        checker.save_to_database()
    
    elapsed = time.time() - start_time
    if not args.quiet:
        safe_print(f"\n{Style.BRIGHT}{Fore.GREEN}[INF] Completed in {elapsed:.2f}s{Fore.RESET}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        safe_print(f"\n{Style.BRIGHT}{Fore.YELLOW}[!] Process interrupted by user{Fore.RESET}{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        safe_print(f"\n{Style.BRIGHT}{Fore.RED}[ERR] {e}{Fore.RESET}{Style.RESET_ALL}")
        sys.exit(1)
