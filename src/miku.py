import csv
from pathlib import Path
from . import defs
import json
import logging
import logging.config
import os
import random
import re
from datetime import date, datetime
from dotenv import load_dotenv
from .postGeneration.generate_posts import initiate_post_generation
from .postGeneration.holiday_post import get_special_holiday

load_dotenv()
DALLE_KEY = os.getenv("DALLE_KEY")
GenerationAttempts = 1

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def date_to_filename(date: str):
    date_array = re.split(r'[\s|-]', date) # Expecting MM-DD-YYYY
    try:
        assert len(date_array) == 3
        return '{year}-{month}-{day}'.format(year=date_array[2], month=date_array[0], day=date_array[1])
    except AssertionError:
        print('Error while converting date to filename form.')
        
###################################
#:::::::::::::::::::::::::::::::::#
###################################
    

def filename_to_date(filename: str):
    filename_array = re.split(r'[\s|-]', filename) # Expecting YYYY-MM-DD
    try:
        assert len(filename_array) == 3
        return '{month}-{day}-{year}'.format(month=filename_array[1], day=filename_array[2], year=filename_array[0])
    except AssertionError:
        print('Error while converting filename to date form.')
    

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def generate_random_date(seed):
    random.seed(seed)
    d = random.randint(1, seed)
    random_date = datetime.fromtimestamp(d).strftime('%m-%d-') + '2024'
    print('Random Date: {rDate}'.format(rDate=random_date))
    return random_date

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def get_starting_date(use_today: bool, specific_date=''):
    if not (specific_date == ''):
        print('Specific Date: {sDate}'.format(sDate=specific_date))
        return specific_date
    else:
        return generate_random_date(int(datetime.now().strftime('%m%d%H%M%S'))) if use_today == False else date.today().strftime('%m-%d-%Y')
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def start():
    ROOT_DIR = Path(__file__).parent
    history_folder = '{root}\\history'.format(root=ROOT_DIR)
    if not os.path.exists(history_folder):
        os.makedirs(history_folder)
    selected_date = get_starting_date(use_today=False, specific_date='') # specific_date used for debugging #6-18-2024 / Abrahamic
    holiday = get_special_holiday(selected_date)
    
    chosen_post_type: defs.PostType = defs.PostType.HOLIDAY if holiday else None
    attempts = 0
    successful_generation = False # Set this to True when we successfully generate Twitter post content.
    
    while True:
        attempts += 1

        date_file_name = date_to_filename(selected_date)
        date_folder = '{historyFolder}\\{folderName}'.format(historyFolder=history_folder, folderName=date_file_name)
        date_logging_file = '{folder}\\miku_output.log'.format(folder=date_folder)
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)
        logging.basicConfig(
            filename=date_logging_file,
            level=logging.INFO,
            force=True
        )
        logging.info('Starting attempt {attempt} for date {date}.'.format(attempt=attempts, date=selected_date))

        if (chosen_post_type != defs.PostType.HOLIDAY):
            # Select a post type at random with weights.
            population = [defs.PostType.RANDOM, defs.PostType.WEATHER, defs.PostType.SPORTS]
            weights = [0.8, 0.1, 0.1]
            chosen_post_type = random.choices(population, weights, k=1)[0]
        
        post_props = defs.PostProps(type=chosen_post_type, date=selected_date, folderName=date_folder, attempt=attempts, holiday=holiday)
        initiate_post_generation(post_props)
        
        if (successful_generation or attempts >= GenerationAttempts):
            break
        else:
            chosen_post_type = None
    
    ## base_prompt = build_base_prompt(holiday)
    ## print(base_prompt['chatgpt'])
    ## print(base_prompt['dalle'])

# Miku giving a weather report for a very specific town.
# Miku posting photos at a previous sporting event.
# Miku follows Elon Musk's flight location.