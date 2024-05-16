from src import miku
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import asyncio
import os

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def download_drivers(chrome = False, firefox = False, edge = False):
    """Downloads Chrome, Firefox, and/or Edge drivers if specified. Resulting drivers will be downloaded to the '.wdm' folder that
       will appear in the root of the project.
    """
    # Set the environment variable to store drivers locally in your project
    os.environ['WDM_LOCAL'] = '1'
    if chrome:
        chrome_driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver is installed at: {chrome_driver_path}")

    if firefox:
        firefox_driver_path = GeckoDriverManager().install()
        print(f"GeckoDriver is installed at: {firefox_driver_path}")
    
    if edge:
        edge_driver_path = EdgeChromiumDriverManager().install()
        print(f"MSEdgeDriver is installed at: {edge_driver_path}")
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def get_driver_path():
    """Gets the full path of the '.wdm' folder, where drivers are downloaded to.

    Returns:
        str: The full path of the '.wdm' folder.
    """
    base_dir = os.path.dirname(os.path.realpath(__file__))
    drivers_dir = '.wdm'
    full_driver_path = os.path.join(base_dir, drivers_dir)
    return full_driver_path
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def get_driver(file_name: str):
    """Gets the full path of a previously downloaded webdriver.

    Args:
        file_name (str): The name of the expected driver, including the file extension (Ex: 'chromedriver.exe').

    Returns:
        str | None: Returns the full path of a requested driver, if it exists, otherwise this will return None.
    """
    driver_path = get_driver_path()
    for dirpath, dirnames, filenames in os.walk(driver_path):
        if file_name in filenames:
            return os.path.join(dirpath, file_name)
    return None

###################################
#:::::::::::::::::::::::::::::::::#
###################################

download_drivers(edge=True)
asyncio.run(miku.start_time_loop())