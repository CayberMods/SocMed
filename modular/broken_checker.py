import requests
from bs4 import BeautifulSoup

def cek_instagram_broken(url): #Instagram
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }    
    try:
        response = requests.get(url, headers=headers, timeout=10)        
        if response.status_code == 404:
            return "BROKEN", "HTTP 404"        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ""        
        if title and title.strip() == "Instagram":
            return "BROKEN", "Title Check: Instagram"        
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            content = meta_title['content']
            if "Instagram" in content and "@" not in content:
                return "BROKEN", "Meta Check: No username"       
        page_text = soup.get_text().lower()
        error_keywords = ['sorry', 'unavailable', 'not found', "couldn't find"]        
        if any(keyword in page_text for keyword in error_keywords):
            if "instagram" in title.lower():
                return "BROKEN", "Content Check: Error keywords found"        
        return "ACTIVE", "OK"        
    except Exception as e:
        return "ERROR", str(e)
def cek_twitter_broken(url): #X/Twitter
    headers = {        
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }    
    try:
        response = requests.get(url, headers=headers, timeout=10)        
        if response.status_code == 404:
            return "BROKEN", "HTTP 404"        
        soup = BeautifulSoup(response.text, 'html.parser')              
        title = soup.title.string if soup.title else ""
        if title and title.strip() == "Profile / X":
            return "BROKEN", "Title Check: Generic X Profile"        
        page_text = soup.get_text().lower()
        error_keywords = [
            "we're unable to show this account", 
            "the account may be private, deleted, or only available on the app", 
            "this account doesn't exist", 
            "account suspended" 
        ]       
        if any(keyword in page_text for keyword in error_keywords):
            return "BROKEN", "Content Check: Error keywords found"        
        return "ACTIVE", "OK"        
    except Exception as e:
        return "ERROR", str(e)        
def cek_youtube_broken(url): #Youtube
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }    
    try:
        response = requests.get(url, headers=headers, timeout=10)        
        if response.status_code == 404:
            return "BROKEN", "HTTP 404"        
        soup = BeautifulSoup(response.text, 'html.parser')        
        if soup.title and "404 Not Found" in soup.title.string:
            return "BROKEN", "Title: 404 Not Found"           
        iframe = soup.find('iframe')
        if iframe and iframe.get('src'):
            if "/error?src=404" in iframe['src']:
                return "BROKEN", "Iframe: Error detected"        
        return "ACTIVE", "OK"        
    except Exception as e:
        return "ERROR", str(e)        
def cek_github_broken(url): #Github
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }    
    try:
        response = requests.get(url, headers=headers, timeout=10)        
        if response.status_code == 404:
            return "BROKEN", "HTTP 404 - Not Found"        
        soup = BeautifulSoup(response.text, 'html.parser')        
        title = soup.title.string if soup.title else ""
        if "not found" in title.lower():
            return "BROKEN", "Title Check: Page Not Found"            
        page_text = soup.get_text().lower()
        error_keywords = ['page not found', 'doesn’t exist', 'is not available']       
        if any(keyword in page_text for keyword in error_keywords):
            return "BROKEN", "Content Check: Error keywords found"        
        return "ACTIVE", "OK"        
    except Exception as e:
        return "ERROR", str(e)
def cek_discord_invite_broken(url): #Discord
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code == 404:
            return "BROKEN", "HTTP 404 Not Found"
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else ""
        meta_title = soup.find('meta', property='og:title')
        meta_content = meta_title['content'] if meta_title else ""
        page_text = soup.get_text().lower()
        error_keywords = [
            'invite invalid',
            'invite expired',
            'invite has expired',
            'unable to accept invite',
            'this invite may be expired',
            'could not find the server',
            'the invite has been revoked',
            'the user who created this invite'
        ]
        error_elements = soup.find_all(['div', 'p', 'span'])
        for element in error_elements:
            text = element.get_text().lower()
            if any(keyword in text for keyword in ['invite invalid', 'invite expired', 'this invite may be expired']):
                return "BROKEN", "Content Check: Invite invalid/expired found"
        if meta_content and "Discord" in meta_content:
            if "join" not in page_text and any(kw in page_text for kw in error_keywords):
                return "BROKEN", "Meta Check: Discord meta without join context and error keywords found"
        if any(keyword in page_text for keyword in error_keywords):
            return "BROKEN", "Content Check: Error keywords found"
        if title.lower() == "discord" and "join" not in page_text:
            return "BROKEN", "Title Check: Discord without join context"
        return "ACTIVE", "OK"
    except Exception as e:
        return "ERROR", str(e)                
def cek_facebook_profile_broken(url): #Facebook
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code == 404:
            return "BROKEN", "HTTP 404 Not Found"
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else ""
        if "Halaman Tidak Ditemukan" in title or "Page Not Found" in title or "Content Not Found" in title:
            return "BROKEN", "Title Check: Page not found"
        meta_title = soup.find('meta', property='og:title')
        meta_content = meta_title['content'] if meta_title else ""
        if meta_content and ("Halaman Tidak Ditemukan" in meta_content or "Page Not Found" in meta_content):
            return "BROKEN", "Meta Check: Page not found"
        page_text = soup.get_text().lower()
        error_keywords = ['sorry, this page isn\'t available', 'the link you followed may be broken', 'page not found', 'halaman tidak tersedia', 'konten ini tidak tersedia']
        if any(keyword in page_text for keyword in error_keywords):
            return "BROKEN", "Content Check: Error keywords found"
        if "facebook" in title.lower() and "login" not in page_text and "masuk" not in page_text:
            profile_indicators = ['tentang', 'about', 'tempat tinggal', 'lives in', 'ikuti', 'follow']
            if not any(indicator in page_text for indicator in profile_indicators):
                return "BROKEN", "Title Check: Facebook page without profile indicators"
        return "ACTIVE", "OK"
    except Exception as e:
        return "ERROR", str(e)        
def cek_linkedin_profile_broken(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code == 404:
            return "BROKEN", "HTTP 404 Not Found"
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else ""
        if "Page not found" in title or "Halaman tidak ditemukan" in title:
            return "BROKEN", "Title Check: Page not found"
        meta_title = soup.find('meta', property='og:title')
        meta_content = meta_title['content'] if meta_title else ""
        if meta_content and ("Page not found" in meta_content or "Halaman tidak ditemukan" in meta_content):
            return "BROKEN", "Meta Check: Page not found"
        page_text = soup.get_text().lower()
        error_keywords = ['page not found', 'halaman tidak ditemukan', 'sorry, we couldn\'t find that page', 'maaf, kami tidak dapat menemukan halaman']
        if any(keyword in page_text for keyword in error_keywords):
            return "BROKEN", "Content Check: Error keywords found"
        if "linkedin" in title.lower() and "profile" not in page_text and "profil" not in page_text:
            profile_indicators = ['tentang', 'about', 'pengalaman', 'experience', 'pendidikan', 'education']
            if not any(indicator in page_text for indicator in profile_indicators):
                return "BROKEN", "Title Check: LinkedIn page without profile indicators"
        return "ACTIVE", "OK"
    except Exception as e:
        return "ERROR", str(e)        
def cek_medium_broken(url): #Medium
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'} 
    try:
        response=requests.get(url,headers=headers,timeout=10)
        if response.status_code==404:
            return "BROKEN","HTTP 404"
        soup=BeautifulSoup(response.text,'html.parser')
        title=soup.title.string if soup.title else ""
        if title and "Page not found" in title:
            return "BROKEN","Title Check: Page not found"
        if title and "404" in title:
            return "BROKEN","Title Check: 404"
        meta_title=soup.find('meta',property='og:title')
        if meta_title and meta_title.get('content'):
            content=meta_title['content']
            if "Page not found" in content or "404" in content:
                return "BROKEN","Meta Check: Page not found"
        page_text=soup.get_text().lower()
        error_keywords=['page not found','404','not found',"couldn't find","out of nothing"]
        if any(keyword in page_text for keyword in error_keywords):
            if "medium" in title.lower() or "404" in title:
                return "BROKEN","Content Check: Error keywords found"
        return "ACTIVE","OK"
    except Exception as e:
        return "ERROR",str(e)        
def cek_reddit_broken(url): #Reddit
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response=requests.get(url,headers=headers,timeout=10)
        if response.status_code==404:
            return "BROKEN","HTTP 404"
        soup=BeautifulSoup(response.text,'html.parser')
        title=soup.title.string if soup.title else ""
        if title and "page not found" in title.lower():
            return "BROKEN","Title Check: Page not found"
        if title and "not found" in title.lower():
            return "BROKEN","Title Check: Not found"
        page_text=soup.get_text().lower()
        error_keywords=['page not found','not found',"couldn't find","sorry","unavailable","404"]
        if any(keyword in page_text for keyword in error_keywords):
            return "BROKEN","Content Check: Error keywords found"
        return "ACTIVE","OK"
    except Exception as e:
        return "ERROR",str(e)        
def cek_spotify_broken(url): #Spotify
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response=requests.get(url,headers=headers,timeout=10)
        if response.status_code==404:
            return "BROKEN","HTTP 404"
        soup=BeautifulSoup(response.text,'html.parser')
        title=soup.title.string if soup.title else ""
        if title and "page not found" in title.lower():
            return "BROKEN","Title Check: Page not found"
        if title and "not found" in title.lower():
            return "BROKEN","Title Check: Not found"
        page_text=soup.get_text().lower()
        error_keywords=['page not found',"can't seem to find","not found",'404']
        if any(keyword in page_text for keyword in error_keywords):
            return "BROKEN","Content Check: Error keywords found"
        return "ACTIVE","OK"
    except Exception as e:
        return "ERROR",str(e)        
def cek_telegram_broken(url): #Telegram
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response=requests.get(url,headers=headers,timeout=10,allow_redirects=True)
        if response.status_code==404:
            return "BROKEN","HTTP 404"
        soup=BeautifulSoup(response.text,'html.parser')
        title=soup.title.string if soup.title else ""
        if title and "page not found" in title.lower():
            return "BROKEN","Title Check: Page not found"
        if title and "not found" in title.lower():
            return "BROKEN","Title Check: Not found"
        page_text=soup.get_text().lower()
        error_keywords=['page not found',"can't find","not found",'404']
        if any(keyword in page_text for keyword in error_keywords):
            return "BROKEN","Content Check: Error keywords found"
        return "ACTIVE","OK"
    except Exception as e:
        return "ERROR",str(e)        
def cek_tiktok_broken(url): #Tiktok
    headers={'User-Agent':'Mozilla/5.0 (Linux; Android 12; Mobile; rv:120.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'}
    try:
        response=requests.get(url,headers=headers,timeout=10)
        if response.status_code==404:
            return "BROKEN","HTTP 404"
        soup=BeautifulSoup(response.text,'html.parser')
        title=soup.title.string if soup.title else ""
        if title and "page not found" in title.lower():
            return "BROKEN","Title Check: Page not found"
        if title and "not found" in title.lower():
            return "BROKEN","Title Check: Not found"
        page_text=soup.get_text().lower()
        if "page not available" in page_text or "couldn't find this account" in page_text or "couldn't find this hashtag" in page_text or "couldn't find this sound" in page_text or "video unavailable" in page_text or "this video isn't available" in page_text:
            return "BROKEN","Content Check: Error keywords found"
        return "ACTIVE","OK"
    except Exception as e:
        return "ERROR",str(e)        
def cek_twitch_broken(url): #Twicth
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response=requests.get(url,headers=headers,timeout=10)
        if response.status_code==404:
            return "BROKEN","HTTP 404"
        soup=BeautifulSoup(response.text,'html.parser')
        title=soup.title.string if soup.title else ""
        if title and "page not found" in title.lower():
            return "BROKEN","Title Check: Page not found"
        if title and "not found" in title.lower():
            return "BROKEN","Title Check: Not found"
        page_text=soup.get_text().lower()
        error_keywords=['page not found',"couldn't find","not found",'404','no results found']
        if any(keyword in page_text for keyword in error_keywords):
            return "BROKEN","Content Check: Error keywords found"
        return "ACTIVE","OK"
    except Exception as e:
        return "ERROR",str(e)        
def cek_linkedin_broken(url): #Linkedin
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response=requests.get(url,headers=headers,timeout=10)
        if response.status_code==404:
            return "BROKEN","HTTP 404"
        soup=BeautifulSoup(response.text,'html.parser')
        title=soup.title.string if soup.title else ""
        if title and "page not found" in title.lower():
            return "BROKEN","Title Check: Page not found"
        if title and "not found" in title.lower():
            return "BROKEN","Title Check: Not found"
        page_text=soup.get_text().lower()
        error_keywords=['page not found',"can't seem to find","not found",'404','uh oh']
        if any(keyword in page_text for keyword in error_keywords):
            return "BROKEN","Content Check: Error keywords found"
        h1_tags=soup.find_all('h1')
        for h1 in h1_tags:
            if h1.get_text(strip=True).lower() in ['page not found','404']:
                return "BROKEN","H1 Check: Page not found"
        return "ACTIVE","OK"
    except Exception as e:
        return "ERROR",str(e)
# Custom your broken verification
"""
CUSTOM BROKEN VERIFICATION MODULE

How to add custom platform:

1. Copy this template:
   def cek_custom_broken(url):
       headers={'User-Agent':'Mozilla/5.0...'}
       try:
           response=requests.get(url,headers=headers,timeout=10,allow_redirects=True)
           if response.status_code==404: return "BROKEN","HTTP 404"
           soup=BeautifulSoup(response.text,'html.parser')
           title=soup.title.string.strip() if soup.title else ""
           page_text=soup.get_text().lower()
           # Add your detection logic here
           if "error" in page_text: return "BROKEN","Error detected"
           return "ACTIVE","OK"
       except Exception as e: return "ERROR",str(e)

2. Add your platform keywords:
   - Title checks: if "not found" in title.lower()
   - Content checks: if any(keyword in page_text for keyword in ['error','not found','404'])
   - Element checks: if soup.find('div', class_='error-page')
   - Meta checks: if meta_title and "404" in meta_title

3. Common error keywords by platform:
   - Instagram: sorry, unavailable, not found, couldn't find
   - Facebook: this page isn't available, halaman tidak tersedia
   - LinkedIn: page not found, can't seem to find, uh oh
   - Reddit: page not found, not found, sorry, unavailable
   - TikTok: page not available, couldn't find this account
   - Discord: invite invalid, invite expired, unable to accept
   - YouTube: 404 Not Found, error?src=404

Created by: CayberMods
"""
PLATFORM_CHECKERS = {
    'instagram': cek_instagram_broken,
    'twitter': cek_twitter_broken,
    'youtube': cek_youtube_broken,
    'github': cek_github_broken,
    'discord': cek_discord_invite_broken,
    'facebook': cek_facebook_profile_broken,
    'linkedin': cek_linkedin_profile_broken,
    'medium': cek_medium_broken,
    'reddit': cek_reddit_broken,
    'spotify': cek_spotify_broken,
    'telegram': cek_telegram_broken,
    'tiktok': cek_tiktok_broken,
    'twitch': cek_twitch_broken
}

def check_broken_link(platform, url):
    """
    Check if a social media link is broken
    
    Args:
        platform (str): Platform name (instagram, twitter, etc.)
        url (str): URL to check
    
    Returns:
        tuple: (status, detail) where status is ACTIVE/BROKEN/ERROR
    """
    checker = PLATFORM_CHECKERS.get(platform.lower())
    if checker:
        return checker(url)
    return "ERROR", f"No checker for platform: {platform}"