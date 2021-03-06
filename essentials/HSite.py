from cmath import exp
import site
from urllib.parse import urlparse
from xml.dom import InvalidAccessErr

try:
    import undetected_chromedriver as uc

except:
    print("-Required packages not installed, installing now...")
    os.system("pip install selenium")
    os.system("pip install msedge-selenium-tools")

    os.system("pip install undetected-chromedriver==2.1.1")
    time.sleep(1)
    import undetected_chromedriver as uc

finally:
    import pickle, base64
    import json
    import time
    import random, string, time, os, socket, threading
    import os, sys
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from datetime import timezone
    import datetime
    from pathlib import Path

STDOUT = True
DEBUG = False
DUMMY = False
cookie_path = os.path.join(os.getcwd(),".browser","cookies.pkl")
session_path = os.path.join(os.getcwd(),".browser","session.pkl")
cache_path = os.path.join(os.getcwd(),".browser")
Path(cache_path).mkdir(parents=True, exist_ok=True) 


DISCONNECTED_MSG = 'Unable to evaluate script: disconnected: not connected to DevTools\n'


def de_print(text):
    if DEBUG:
        print(text)
    
def norm_print(text):
    if STDOUT or DEBUG:
        print(text)


def chromepath():
    with open('path.json','r') as f:
        path = json.load(f)
        p_path = path['Drivers']['path']
        f_path = f"{os.getcwd()}{p_path}"
        return f_path
    
class CFBypass(threading.Thread):
    def __init__(self,driver):
        threading.Thread.__init__(self)
        self.daemon = True
        self.driver = driver
        self.endwhendone = False
        self.TARGET_NAME = "Just a moment..."
        self.status = False
        self.run_event = threading.Event()
        self.run_event.set()
        self.exc = None     
        

    def _main_execution(self):
        try:
            while self.driver.title == self.TARGET_NAME:
                if not self.run_event.is_set():
                    break
                norm_print("Waiting for cloudflare...")
                time.sleep(1)
            else:
                de_print(self.driver.title)
                de_print("Done")
                self.savecookies()
                self._other_options()
                self.status = True
        except BaseException as e:
            self.exc = e

    def savecookies(self):
        de_print('saving cookie')
        pickle.dump(self.driver.execute_script("return navigator.userAgent;"), open(session_path,"wb"))
        if DEBUG and DUMMY:
            de_print("DUMMY COOKIE")
            dummy = [{'domain': 'nhentai.net', 'httpOnly': False, 'name': 'cf_chl_2', 'path': '/', 'secure': False, 'value': 'a869f45975727b'}, {'domain': 'nhentai.net', 'httpOnly': False, 'name': 'cf_chl_prog', 'path': '/', 'secure': False, 'value': 'x15'}, {'domain': '.nhentai.net', 'httpOnly': True, 'name': 'cf_clearance', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': ''}, {'domain': 'nhentai.net', 'expiry': 1659394067, 'httpOnly': False, 'name': 'csrftoken', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': ''}]
            pickle.dump(dummy , open(cookie_path,"wb"))
        else:
            pickle.dump(self.driver.get_cookies() , open(cookie_path,"wb"))
            de_print("Cookies Saved")
    
    def loadcookies(self):
        de_print("Loading Cookie")
        try:
            cookies = pickle.load(open(cookie_path,"rb"))
        except FileNotFoundError:
            norm_print("Cookie not found")
            return False
        self.driver.execute_cdp_cmd('Network.enable', {})

        # Iterate through pickle dict and add all the cookies
        for cookie in cookies:
            # Set the actual cookie
            self.driver.execute_cdp_cmd('Network.setCookie', cookie)

        # Disable network tracking
        self.driver.execute_cdp_cmd('Network.disable', {})

        de_print("cookie loaded")
        return True

     
    def _other_options(self):
        if self.endwhendone == True:
            self.driver.close()

    def run(self):
        self.running_thread = True
        self._main_execution()

    def err(self):
        if self.exc:
            self.running_thread = False
            return True
        return False

    

class SiteCFBypass(threading.Thread):
    def __init__(self, link_destination):
        threading.Thread.__init__(self)
        self.daemon = True
        self.link = link_destination
        self.proc_done = False
        self.isheadless = False
        self.exc = None
        self.page_source = None

    def quitproto(self):
        self.driver.quit()
        self.proc_done = True
        sys.exit()
    
    def initialize_chromedriver(self):
        options= uc.ChromeOptions() 
        options.use_chromium=True
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        
    
       
        # options.add_argument(f"--user-data-dir=C:\\Users\\ADMIN\\AppData\\Local\\Google\\Chrome\\User Data")

        # session1 = SessionManager()
        # if session1.activeSession:
        #     session1.load_session()
        #     executor_url = session1.executor_url
        #     session_id = session1.session_id
        #     driver =  uc.Remote
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "eager"
        driver =  uc.Chrome(desired_capabilities=caps,options=options)
        self.driver = driver
        self.cloudflare = CFBypass(self.driver)
        iscookieloaded = self.cloudflare.loadcookies()
        self.driver.minimize_window()
        # driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"})
        self.driver.get(self.link) 
        norm_print("Bypassing Cloudflare")
        self.cloudflare.start()
    
    def main(self):
        # check_driver(chromepath())
        try:
            code = self.initialize_chromedriver()
            if code == 190:
                sys.exit()
        except Exception as e:
            self.exc = e
            return
       

        while True:
            time.sleep(1)
            if not self.cloudflare.err():
                if self.cloudflare.status:
                    self.page_source = self.driver.page_source
                    self.user_agent = self.driver.execute_script("return navigator.userAgent;")
                    norm_print('Process has finished Successfully')
                    self.quitproto()
            else:
                self.exc = self.cloudflare.exc
                self.quitproto()


    def join(self):
        threading.Thread.join(self)
        if self.exc:
            raise self.exc

                
    def run(self):
        self.main()

    def cookie_available():
        if os.path.exists(cookie_path):
            cookie_verified = False
            cookies = pickle.load(open(cookie_path,"rb"))
            for cookie in cookies:
                expirey = cookie.get("expiry",False)
                if expirey != False:
                    cookie_verified = True
                    expiration = int(expirey)
                else:
                    pass
            if not cookie_verified:    
                return (True, "Token validity unconfirmed")
                

            # epoch_time = int(time.time())
            dt = datetime.datetime.now(timezone.utc)
  
            utc_time = dt.replace(tzinfo=timezone.utc).replace(microsecond=0)
            epoch_time = int(utc_time.timestamp())
            if epoch_time >= expiration:
                return (False, "Token has expired")      
            if not os.path.exists(session_path):
                return (False, "Header is not found")
            return (True, "Available")
        return (False, "No cookie found")

    def delete_cookies():
        try:
            os.remove(cookie_path)
        except OSError:
            pass
    
    


        
        
if DEBUG:
    print("WARNNING DEBUG MODE IS ON. SOME FUNCTIONS MAY BE EXPERIMENTAL AND WORK INCORRECTLY")
    


if __name__ == '__main__':
    from .Errors import exception as cferror
    # Test site
    hcf = SiteCFBypass("https://nowsecure.nl/")
    hcf.start()
    hcf.join()
    print(hcf.page_source)
else:
    from essentials.Errors import exception as cferror
    