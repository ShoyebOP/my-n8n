#!/usr/bin/env python3
"""
Extract Vimeo iframe URL from a webpage using Selenium with cookie authentication.
"""

import argparse
import sys
import os
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup


def parse_netscape_cookies(cookie_file_path, target_domain):
    """
    Parse Netscape-formatted cookie file and return cookies for the target domain.
    
    Args:
        cookie_file_path: Path to the cookie file
        target_domain: Domain to filter cookies for
        
    Returns:
        List of cookie dictionaries
    """
    cookies = []
    
    try:
        with open(cookie_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments (except HttpOnly prefixed lines)
                if not line or (line.startswith('#') and not line.startswith('#HttpOnly_')):
                    continue
                
                # Handle HttpOnly prefix
                if line.startswith('#HttpOnly_'):
                    line = line[len('#HttpOnly_'):]
                
                # Split by tab or multiple spaces
                parts = line.split('\t')
                if len(parts) < 7:
                    # Try splitting by multiple spaces if tab split didn't work
                    parts = [p for p in line.split() if p]
                
                if len(parts) < 7:
                    continue
                
                domain = parts[0]
                flag = parts[1]
                path = parts[2]
                secure = parts[3]
                expiration = parts[4]
                name = parts[5]
                value = ' '.join(parts[6:])  # Join remaining parts for value
                
                # Check if cookie belongs to target domain
                if target_domain.endswith(domain) or domain.endswith(target_domain):
                    cookie = {
                        'name': name,
                        'value': value,
                        'domain': domain,
                        'path': path,
                        'secure': secure.upper() == 'TRUE',
                        'expiry': int(expiration) if expiration.isdigit() else None
                    }
                    cookies.append(cookie)
    
    except FileNotFoundError:
        print(f"ERROR: Cookie file not found: {cookie_file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to parse cookie file: {e}", file=sys.stderr)
        sys.exit(1)
    
    return cookies


def setup_driver():
    """
    Configure and return a Selenium Chrome WebDriver with stealth settings.
    """
    chrome_options = Options()
    
    # Headless mode
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Performance optimizations
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    
    # Stealth settings to avoid bot detection
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set realistic user agent
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Additional preferences
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,  # Disable images
            'plugins': 2,
            'popups': 2,
            'geolocation': 2,
            'notifications': 2,
            'media_stream': 2,
        }
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Execute CDP commands to further hide automation
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except WebDriverException as e:
        print(f"ERROR: Failed to initialize Chrome WebDriver: {e}", file=sys.stderr)
        print("ERROR: Ensure Chromium and ChromeDriver are installed and in PATH", file=sys.stderr)
        sys.exit(1)


def extract_vimeo_url(url, cookie_file):
    """
    Extract Vimeo iframe URL from the given webpage.
    
    Args:
        url: Target webpage URL
        cookie_file: Path to Netscape cookie file
        
    Returns:
        Vimeo iframe src URL or None
    """
    driver = None
    
    try:
        # Parse target domain
        parsed_url = urlparse(url)
        target_domain = parsed_url.netloc
        
        print(f"INFO: Target URL: {url}", file=sys.stderr)
        print(f"INFO: Target domain: {target_domain}", file=sys.stderr)
        
        # Parse cookies
        print(f"INFO: Parsing cookie file: {cookie_file}", file=sys.stderr)
        cookies = parse_netscape_cookies(cookie_file, target_domain)
        
        if not cookies:
            print(f"ERROR: No valid cookies found for domain: {target_domain}", file=sys.stderr)
            sys.exit(1)
        
        print(f"INFO: Loaded {len(cookies)} cookies", file=sys.stderr)
        
        # Setup driver
        print("INFO: Initializing Chrome WebDriver...", file=sys.stderr)
        driver = setup_driver()
        
        # Navigate to a base page first to set cookies
        print(f"INFO: Navigating to {parsed_url.scheme}://{target_domain}", file=sys.stderr)
        driver.get(f"{parsed_url.scheme}://{target_domain}")
        
        # Add cookies
        print("INFO: Adding cookies...", file=sys.stderr)
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"WARNING: Failed to add cookie {cookie['name']}: {e}", file=sys.stderr)
        
        # Navigate to target URL
        print(f"INFO: Navigating to target page...", file=sys.stderr)
        driver.get(url)
        
        # Wait for iframe to load
        print("INFO: Waiting for Vimeo iframe...", file=sys.stderr)
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
        except TimeoutException:
            print("ERROR: Timeout waiting for iframe to load", file=sys.stderr)
            sys.exit(1)
        
        # Parse page source
        print("INFO: Parsing page source...", file=sys.stderr)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find Vimeo iframe
        iframes = soup.find_all('iframe')
        print(f"INFO: Found {len(iframes)} iframe(s) on page", file=sys.stderr)
        
        for iframe in iframes:
            src = iframe.get('src', '')
            if 'player.vimeo.com' in src:
                print("INFO: Successfully found Vimeo iframe", file=sys.stderr)
                return src
        
        print("ERROR: No Vimeo iframe found on page", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
    
    finally:
        if driver:
            driver.quit()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract Vimeo iframe URL from a webpage using cookies'
    )
    parser.add_argument(
        '--url',
        required=True,
        help='Target webpage URL'
    )
    parser.add_argument(
        '--cookies',
        required=True,
        help='Path to Netscape-formatted cookie file'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.isfile(args.cookies):
        print(f"ERROR: Cookie file does not exist: {args.cookies}", file=sys.stderr)
        sys.exit(1)
    
    # Extract Vimeo URL
    vimeo_url = extract_vimeo_url(args.url, args.cookies)
    
    # Print result to stdout
    if vimeo_url:
        print(vimeo_url)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
