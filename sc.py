import os, random, json
from multiprocessing import Process
import zipfile
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service 

with open('Config.json', 'r') as openfile:
    # Reading from json file
    json_object = json.load(openfile)


link = json_object['url']
py = json_object['proxy']
port = json_object['port']
user = json_object['user']
passw = json_object['passw']
thread = int(json_object['thread'])


PROXY_HOST = py  
PROXY_PORT = port
PROXY_USER = user
PROXY_PASS = passw


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False):
    s = Service(executable_path=os.path.join(os.curdir,'chromedriver'))
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    chrome_options.add_argument("--log-level=3")
    prefs = {"profile.managed_default_content_settings.images": 1}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
    driver = webdriver.Chrome(service=s,options=chrome_options)
    return driver

def main():
    
    while True:
        li_element = []
        try:
            driver = get_chromedriver(use_proxy=True)
            driver.maximize_window()
            driver.get('https://www.dextools.io/app/bsc')
            driver.implicitly_wait(10)
            try:
                driver.find_element(By.CLASS_NAME,'close').click()
                driver.execute_script("document.querySelector('.close').click();")
            except:
                pass 
       
            driver.find_element(By.CLASS_NAME,'search-pairs').send_keys(link)
            sleep(5)
            driver.execute_script("document.querySelectorAll('.results-container li a')[0].click();")
            sleep(2)
            li_element = driver.find_element(By.CLASS_NAME,"social").find_element(By.CLASS_NAME,'social-icons').find_elements(By.TAG_NAME,"a")
            social_share = driver.find_element(By.CLASS_NAME,"social").find_element(By.TAG_NAME,"a")
            sleep(1)
            
        except Exception as e:
            print(e)
        main_window = driver.current_window_handle

        # click on favorite button 
        try:
            driver.execute_script("document.querySelector('.favorite-button').querySelector('button').click();")
            sleep(2)
        except:
            pass

        # Infinity scrolling
            screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
            i = 1

            while True:
                # scroll one screen height each time
                driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
                i += 1
                sleep(3)
                # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
                scroll_height = driver.execute_script("return document.body.scrollHeight;")  
                # Break the loop when the height we need to scroll to is larger than the total scroll height
            
                if (screen_height) * i > scroll_height:
                    break
                


        #___________________________________________ Click on  website
        for url in li_element:
            try:
                driver.execute_script("arguments[0].click();", url)
                sleep(3)
                new_window = driver.window_handles[1]
                driver.switch_to.window(new_window)
                sleep(3)
                driver.close()
                driver.switch_to.window(main_window)
            except Exception as e:
                pass
        
        
        # _________________________________________share button click and open model window
        try:
            driver.execute_script("arguments[0].click();", social_share)
            sleep(2)
            model_content = driver.find_elements(By.CLASS_NAME,"modal-content")[1]


            # ______________________________________ looping over each social site
            try:
                social_link = model_content.find_elements(By.TAG_NAME,"a")
                # for _ in random.randint(0,2):
                driver.execute_script("arguments[0].click();", social_link[random.randint(0,2)])
                sleep(5)
                new_window = driver.window_handles[1]
                driver.switch_to.window(new_window)
                driver.close()
                driver.switch_to.window(main_window)
            except Exception as e:
                pass
        except Exception as e:
            pass

        # _______________________________________________________ Close model window
        try:
            driver.execute_script("document.querySelectorAll('.modal-content')[1].querySelector('button').click();")
        except Exception as e:
            pass

        driver.delete_all_cookies()
        driver.quit()



if __name__=='__main__':
    for _ in range(thread):
        process_obj = Process(target=main)
        process_obj.start()

    for __ in range(thread):
        process_obj.join()
