from datetime import datetime
import logging
import os
import time
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote import webelement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .. import defs
from .. import keys as envkey

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def get_edge_driver_options():
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    options.add_argument("start-maximized")
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-features=msEdgeEnableNurturingFramework')
    options.add_experimental_option("prefs", {"user_experience_metrics": {"personalization_data_consent_enabled": True}})
    return options

###################################
#:::::::::::::::::::::::::::::::::#
###################################

# Function to convert current time to seconds since the Epoch
def current_seconds_since_epoch():
    return int(datetime.now().timestamp())

###################################
#:::::::::::::::::::::::::::::::::#
###################################

async def logout_if_needed(driver):
    try:
        id_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'id_button'))
        )
        id_button.click()
        
        sign_out_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.LINK_TEXT, 'Sign out'))
        )
        sign_out_button.click()
        
    except TimeoutException:
        logging.info('Not seeing a user logged in... proceeding.')
        return

###################################
#:::::::::::::::::::::::::::::::::#
###################################

async def login_to_bing(driver):
    ## Process validated 5/15/2024 - may break if bing changes
    driver.get('https://www.bing.com/')
    
    await logout_if_needed(driver)
    
    ## Click on the user icon at the top of the page.
    sign_in_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'id_button'))
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
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

async def start_bing_generation(driver, props: defs.PostProps, prompt: str, output_image: str):
    ## Process validated 5/15/2024 - may break if bing changes
    driver.get('https://www.bing.com/images/create?')
    
    prompt_textbox = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'b_searchbox'))
    )
    prompt_textbox.send_keys(prompt)
    prompt_textbox.send_keys(Keys.ENTER)
    
    ## In cases where we must wait extra long for image generation, bing may not auto redirect us.
    ## If this happens, we must occasionally refresh to keep checking for the images.
    refresh_interval = 20
    giveup_timeout = 300
    start_time = time.time()
    image_container = None
    while True:
        try:
            image_container = WebDriverWait(driver, refresh_interval).until(
                EC.visibility_of_element_located((By.ID, 'giric'))
            )
            break
        except TimeoutException:
            if time.time() - start_time < giveup_timeout:
                print('Refreshing to check for image generation...')
                logging.info('Refreshing to check for image generation...')
                driver.refresh()
            else:
                print('Image generation container has not been found within the giveup timeout period.')
                logging.warn('Image generation container has not been found within the giveup timeout period.')
                break
        except Exception as e:
            logging.error('An error has occurred while waiting for Bing Image Generation... {error}'.format(error=e))
            break

    def retrieve_hrefs(element):
        return element.get_attribute('href')
    if image_container == None:
        # Check to make sure image_container was properly set up above, otherwise end early.
        logging.error('Could not find the image container during Bing Image Generation.')
        return
    a_elements = image_container.find_elements(By.TAG_NAME, 'a')
    img_links = list(map(retrieve_hrefs, a_elements))
    if len(img_links) >= 1:
        del img_links[-1] # Removal of an extra element that we don't want.
    for index, link in enumerate(img_links):
        image_num = index + 1
        driver.get(link)
        try:
            main_window = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.ID, 'mainImageWindow'))
            )
            current_image_container = WebDriverWait(main_window, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'curimgonview'))
            )
            new_image = WebDriverWait(current_image_container, 20).until(
                EC.visibility_of_element_located((By.TAG_NAME, 'img'))
            )
            img_src = new_image.get_attribute('src')
            if img_src:
                response = requests.get(img_src)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    location = os.path.join(props.folderName, '{fileName}_{imageNum}.jpeg'.format(fileName=output_image, imageNum=image_num))
                    image.save(location)
        
        except Exception as e:
            logging.error("Failed to find and download image {imageNum} for generation '{uuid}'. Error: {error}".format(imageNum=image_num, uuid=props.uuid, error=e))
        finally:
            driver.back()
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

async def bing_image_create(props: defs.PostProps, prompt: str, output_image: str):
    driver = webdriver.Edge(get_edge_driver_options())
    try:
        await login_to_bing(driver)
        await start_bing_generation(driver, props, prompt, output_image)
    except Exception as error:
        logging.error('Encountered a problem during Bing Image Creation: {}'.format(error))
    finally:
        driver.close()