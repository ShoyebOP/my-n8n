import argparse
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def main():
    parser = argparse.ArgumentParser(
        description="Extracts an embedded Vimeo URL from a course page.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-u", "--url", required=True, help="The full URL of the course page.")
    parser.add_argument("-c", "--cookies", required=True, help="The path to the cookie file inside the container.")
    
    args = parser.parse_args()
    course_url = args.url
    cookie_file_path = args.cookies

    # Fail-fast check for the cookie file, this is essential
    if not os.path.exists(cookie_file_path):
        print(f"FATAL: Cookie file not found at '{cookie_file_path}'.", file=sys.stderr)
        sys.exit(1)
    
    parsed_uri = urlparse(course_url)
    domain = f"{parsed_uri.scheme}://{parsed_uri.netloc}"
    target_netloc = parsed_uri.netloc
    target_main_domain = '.'.join(target_netloc.split('.')[-2:])

    # --- PERFORMANCE OPTIMIZED CHROME OPTIONS ---
    options = webdriver.ChromeOptions()
    
    # Anti-bot detection options (essential)
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Docker/Headless options (essential)
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Performance-enhancing options
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--log-level=3')
    options.add_argument('--blink-settings=imagesEnabled=false') # Disable images

    driver = webdriver.Chrome(options=options)
    
    # Anti-detection script (essential)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        driver.get(domain)

        cookies_loaded_count = 0
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 7:
                    raw_cookie_domain = parts[0].lstrip('#HttpOnly_')
                    cookie_main_domain = '.'.join(raw_cookie_domain.lstrip('.').split('.')[-2:])
                    
                    if target_main_domain == cookie_main_domain:
                        driver.add_cookie({
                            'domain': raw_cookie_domain, 'name': parts[5], 'value': parts[6],
                            'path': parts[2], 'secure': parts[3] == 'TRUE',
                            'expiry': int(parts[4]) if parts[4] != '0' else None
                        })
                        cookies_loaded_count += 1
        
        if cookies_loaded_count == 0:
            print(f"FATAL: No cookies for '{target_main_domain}' found in file.", file=sys.stderr)
            sys.exit(1)

        driver.get(course_url)

        try:
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'player.vimeo.com')]")))
        except TimeoutException:
            print("FATAL: Timeout while waiting for Vimeo player. Login likely failed.", file=sys.stderr)
            sys.exit(1)
            
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        iframe = soup.find('iframe', src=lambda s: s and 'player.vimeo.com' in s)

        if iframe and iframe.get('src'):
            # This is the only output on success
            print(iframe['src'])
        else:
            print("FATAL: Player iframe was found, but its src could not be extracted.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
