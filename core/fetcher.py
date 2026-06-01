import requests
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class Fetcher:
    def __init__(self, logger=None, timeout=10):
        self.session = requests.Session()
        self.timeout = timeout
        self.logger = logger

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }

    def fetch_static(self, url):
        try:
            res = requests.get(url, headers=self.headers)
            res.raise_for_status()

            return {
                "url": url,
                "html": res.text,
                "status_code": res.status_code
            }
        
        except Exception as e:
            print("[Error]", e)
            None

        return 0

    def fetch_headless(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        try:
            print("Loading Page")
            driver.get(url)
            time.sleep(3)
            
            last_h = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

                new_h = driver.execute_script("return document.body.scrollHeight")
                if new_h == last_h:
                    break
                last_h = new_h

            time.sleep(3)

            return driver.page_source
        
        except Exception as e:
            print('[Error]', e)
            return None
        
        finally:
            driver.quit()   

    def fetch_css(self, url):
        '''
        Fetch CSS file content,
        using parsed urls from DOM
        '''
        try:
            res = requests.get(url, headers=self.headers)
            res.raise_for_status()
            return res.text
        
        except Exception as e:
            print("[Error]", e)
            return None
        
    def fetch_images(self):
        try:
            r = requests.get(url, timeout=self.timeout)
            r.raise_for_status()
            return r.content
        except Exception as e:
            print("[IMAGE ERROR]", e)
            return None
        
    def check_dynamic_loading(self, html):
        if not html or len(html) < 5000:
            return True

        if "<img>" not in html:
            return True

        if "__NEXT_DATA__" in html or "react" in html.lower():
            return True

        return False
        
    def fetch(self, url):
        result = self.fetch_static(url)

        if not result:
            return None
        
        html = result["html"]

        if self.check_dynamic_loading(html):
            print("[INFO] Using dynamic fetch")
            html = self.fetch_headless(url)
        else:
            print("[INFO] Using static fetch")

        return html     
    


if __name__ == "__main__":
    check_dynamic = False
    fetcher = Fetcher()
    url = "https://elliotoracle.com/shop/"
    '''
    res = fetcher.fetch_static(url)
    check_dynamic = fetcher.check_dynamic_loading(res)
    if check_dynamic == True:
        res_dynamic = fetcher.fetch_headless(url)
    print(len(res))
    print(len(res_dynamic))
    #print(res)
    '''
    html = fetcher.fetch(url)