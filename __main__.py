import asyncio
import os
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from src import miku


def download_drivers():
    # Set the environment variable to store drivers locally in your project
    os.environ['WDM_LOCAL'] = '1'
    chrome_driver_path = ChromeDriverManager().install()
    print(f"ChromeDriver is installed at: {chrome_driver_path}")

    firefox_driver_path = GeckoDriverManager().install()
    print(f"GeckoDriver is installed at: {firefox_driver_path}")
    
    edge_driver_path = EdgeChromiumDriverManager().install()
    print(f"MSEdgeDriver is installed at: {edge_driver_path}")
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def get_driver_path():
    base_dir = os.path.dirname(os.path.realpath(__file__))
    drivers_dir = '.wdm'
    full_driver_path = os.path.join(base_dir, drivers_dir)
    return full_driver_path
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def get_driver(fileName: str):
    driver_path = get_driver_path()
    for dirpath, dirnames, filenames in os.walk(driver_path):
        if fileName in filenames:
            return os.path.join(dirpath, fileName)
    return None

###################################
#:::::::::::::::::::::::::::::::::#
###################################

download_drivers()
asyncio.run(miku.start_time_loop(get_driver('chromedriver.exe'), get_driver('geckodriver.exe')))