from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .. import defs
from .. import keys as envkey

###################################
#:::::::::::::::::::::::::::::::::#
###################################

# Function to convert current time to seconds since the Epoch
def current_seconds_since_epoch():
    return int(datetime.now().timestamp())

###################################
#:::::::::::::::::::::::::::::::::#
###################################

async def get_bing_cookies():
    driver = webdriver.Chrome()
    bing_cookies = defs.BingCookies('', '')
    try:
        ## Process validated 5/15/2024 - may break if bing changes
        driver.get('https://www.bing.com/')
        
        ## Click on the user icon at the top of the page.
        sign_in_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="id_s"]'))
        )
        sign_in_link.click()
        
        ## Click on the 'Sign in with a personal account' button.
        accountItem = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'id_accountItem'))
        )
        accountItem.click()
        
        ## Enter username/email
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'loginfmt'))
        )
        email_input.send_keys(envkey.BINGUSER)
        email_input.send_keys(Keys.ENTER)
        
        ## Enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'passwd'))
        )
        password_input.send_keys(envkey.BINGPASS)
        password_input.send_keys(Keys.RETURN)
        
        ## Decline 'stay signed in?' prompt.
        decline_stay_signed_in = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'declineButton'))
        )
        decline_stay_signed_in.send_keys(Keys.ENTER)
        
        ## Confirm we are logged in as Miku - technically this is the first name of the outlook account.
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@title="{}"]'.format(envkey.BINGNAME)))
        )
        
        current_time = current_seconds_since_epoch()
        
        ## Get first mandatory cookie
        cookie_one = driver.get_cookie('_U')
        if cookie_one is None:
            raise defs.FailedGettingCookie("No cookie found with the name '_U'.")
            
        if 'expiry' in cookie_one and cookie_one['expiry'] <= current_time:
            raise defs.FailedGettingCookie("Cookie '_U' has expired.")
        
        if 'value' in cookie_one:
            bing_cookies.set_session(cookie_one['value'])
            
        ## Get second mandatory cookie
        cookie_two = driver.get_cookie('SRCHHPGUSR')
        if cookie_two is None:
            raise defs.FailedGettingCookie("No cookie found with the name 'SRCHHPGUSR'.")
        
        if 'expiry' in cookie_two and cookie_two['expiry'] <= current_time:
            raise defs.FailedGettingCookie("Cookie 'SRCHHPGUSR' has expired.")
        
        if 'value' in cookie_two:
            bing_cookies.set_search(cookie_two['value'])
            
        return bing_cookies
        
    except Exception as error:
        logging.error('Encountered a problem while getting Bing cookies via Selenium: {}'.format(error))
        return bing_cookies
    finally:
        driver.close()