import os
from webdriver_manager.chrome import ChromeDriverManager
import webdriver_manager.chrome
from webdriver_manager.firefox import GeckoDriverManager

import asyncio
from src import miku

def download_drivers():
    # Set the environment variable to store drivers locally in your project
    os.environ['WDM_LOCAL'] = '1'
    chrome_driver_path = ChromeDriverManager().install()
    print(f"ChromeDriver is installed at: {chrome_driver_path}")

    firefox_driver_path = GeckoDriverManager().install()
    print(f"GeckoDriver is installed at: {firefox_driver_path}")

download_drivers()
asyncio.run(miku.start_time_loop())