from . import defs
from . import twitter
from .postGeneration.generate_posts import initiate_post_generation
from .postGeneration.holiday_post import get_special_holiday
from datetime import date, datetime
from dotenv import load_dotenv
from pathlib import Path
import itertools
import logging
import logging.config
import os
import random
import re
import shutil
import sys
import time
import uuid

load_dotenv()
DALLE_KEY = os.getenv("DALLE_KEY")
GenerationAttempts = 1

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def date_to_filename(date: str):
    """Converts a date string in the 'mm-dd-YYYY' format into the 'YYYY-mm-dd' format, which is used for directory/file naming.

    Args:
        date (str): A date in the 'mm-dd-YYYY' format to be converted.

    Returns:
        str: A string in the 'YYYY-mm-dd' format.
    """
    date_array = re.split(r'[\s|-]', date) # Expecting MM-DD-YYYY
    try:
        assert len(date_array) == 3
        return '{year}-{month}-{day}'.format(year=date_array[2], month=date_array[0], day=date_array[1])
    except AssertionError:
        logging.error('Error while converting date to filename form.')
        print('Error while converting date to filename form.')
        
###################################
#:::::::::::::::::::::::::::::::::#
###################################
    
def filename_to_date(filename: str):
    """Converts a date string in the 'YYYY-mm-dd' format into the 'mm-dd-YYYY' format, which is used in most date processing.

    Args:
        filename (str): A date in the 'YYYY-mm-dd' format to be converted.

    Returns:
        str: A string in the 'mm-dd-YYYY' format.
    """
    filename_array = re.split(r'[\s|-]', filename) # Expecting YYYY-MM-DD
    try:
        assert len(filename_array) == 3
        return '{month}-{day}-{year}'.format(month=filename_array[1], day=filename_array[2], year=filename_array[0])
    except AssertionError:
        logging.error('Error while converting filename to date form.')
        print('Error while converting filename to date form.')

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def generate_random_date(seed: int):
    """Generates a random date based off the input 'seed' parameter.

    Args:
        seed (int): A number to influence the random date that is picked.

    Returns:
        str: A random date in the format of 'mm-dd-YYYY'.
    """
    random.seed(seed)
    d = random.randint(1, seed)
    random_date = datetime.fromtimestamp(d).strftime('%m-%d-') + '2024'
    print('Random Date: {rDate}'.format(rDate=random_date))
    return random_date

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def get_starting_date(use_today: bool, specific_date=''):
    """Gets a date. This date should be in the form of 'mm-dd-YYYY'.
       If 'use_today' is set to True, the current real date is returned.
       If 'use_today' is set to False, a date will be generated based on a random seed.
       If 'specific_date' is set, this function will return the exact string passed in. [Mainly for debugging - Date format is not validated]

    Args:
        use_today (bool): Determines whether Today's date is used or if a random date should be picked.
        specific_date (str, optional): A debug parameter for testing against a specific date. Defaults to ''.

    Returns:
        str: A date in the form of 'mm-dd-YYYY'.
    """
    if specific_date != '':
        print('Specific Date: {sDate}'.format(sDate=specific_date))
        return specific_date
    else:
        return generate_random_date(int(datetime.now().strftime('%m%d%H%M%S'))) if use_today == False else date.today().strftime('%m-%d-%Y')
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def get_image_files(folder: str):
    """Gets a list of full paths for all image files that end with '.jpeg' and '.png' within the 'folder' parameter.

    Args:
        folder (str): A full path to a folder to search for image files within.
    """
    if (os.path.isdir(folder)):
        files = os.listdir(folder)
        for file in files:
            if file.endswith(".jpeg") or file.endswith(".png"):
                #print(file)
                ''''''
                
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def create_folder_if_needed(location: str):
    """Checks to see if 'location' exists. If it does not, it will create a directory there.

    Args:
        location (str): A path to check for/create a directory at.
    """
    if not os.path.exists(location):
        os.makedirs(location)

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def find_folders_with_substring(search_path: str, substr: str):
    """Finds and returns the full path of all folders within 'search_path' that match the 'substr' parameter.

    Args:
        search_path (str): The directory to search in.
        substr (str): The substring to look for in the name of each child directory.

    Returns:
        list[str]: A list of directory paths that contain the 'substr' substring.
    """
    all_matching_folders: list[str] = []
    for root, dirs, files in os.walk(search_path):
        for name in dirs:
            if substr in name:
                all_matching_folders.append(name)
    return all_matching_folders

###################################
#:::::::::::::::::::::::::::::::::#
###################################

async def post_to_twitter():
    """TODO: Under development
    """
    # At this point, we must determine if the folder we want to post has all the necessary items to post to twitter.
    # If it does not, do we try generating one more time? Probably not
    print('post to twitter')

###################################
#:::::::::::::::::::::::::::::::::#
###################################

async def start():
    """The entry point of the image/text generation process.
    - Creates generation folders if necessary.
    - Checks for a notable holiday being celebrated today, prioritizing specific countries.
    - Launches post generation sequence with the goal of generating 1-4 images and a suitable social media status message. If either of these cannot
      be validated, then the post generation sequence will retry for a number of attempts. A holiday post can only be on attempt 1, otherwise it will
      try a different post type.
    """
    create_folder_if_needed(defs.history_folder)
    create_folder_if_needed(defs.archive_folder)
    selected_date = get_starting_date(use_today=False, specific_date='1-22-2024') # specific_date used for debugging #6-18-2024 / Abrahamic
    date_file_name = date_to_filename(selected_date)
    date_folder_base = os.path.join(defs.history_folder, date_file_name)
    
    holiday = get_special_holiday(selected_date)
    chosen_post_type: defs.PostType = defs.PostType.HOLIDAY if holiday else None
    attempts = 0
    successful_generation = False # Set this to True when we successfully generate Twitter post content.
    
    # twitter.prepare_twitter_post(selected_date)
    
    while True:
        attempts += 1
        current_uuid = uuid.uuid4().hex[:8] # Unique ID to identify this attempt for file management purposes and validating Twitter upload content.
        date_folder = '{base}_{uuid}'.format(base=date_folder_base, uuid=current_uuid)
        
        # If a folder already exists, archive it and remove the original
        existing_dirs = find_folders_with_substring(search_path=defs.history_folder, substr=date_file_name)
        for dir in existing_dirs:
            current_loc = os.path.join(defs.history_folder, dir)
            current_loc_files = [f for f in os.listdir(current_loc) if os.path.isfile(os.path.join(current_loc, f))]
            if len(current_loc_files) <= 1:
                # Remove folder if it has nothing or a single log file.
                shutil.rmtree(current_loc)
            else:
                new_loc = os.path.join(defs.archive_folder, dir)
                shutil.move(current_loc, new_loc)
        
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)
            
        date_logging_file = os.path.join(date_folder, 'miku_output_{uuid}.log'.format(uuid=current_uuid))
        logging.basicConfig(
            filename=date_logging_file,
            level=logging.INFO,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            force=True
        )
        logging.info('Starting attempt {attempt} for date {date}. UUID: {uuid}'.format(attempt=attempts, date=selected_date, uuid=current_uuid))

        if (chosen_post_type != defs.PostType.HOLIDAY):
            # Select a post type at random with weights.
            population = [defs.PostType.RANDOM, defs.PostType.WEATHER, defs.PostType.SPORTS]
            weights = [10.8, 0.1, 0.1]
            chosen_post_type = random.choices(population, weights, k=1)[0]
        
        post_props = defs.PostProps(uuid=current_uuid, type=chosen_post_type, date=selected_date, folderName=date_folder, attempt=attempts, holiday=holiday)
        image_successful = await initiate_post_generation(post_props)

        get_image_files(date_folder)
        if (image_successful):
            print('Image generated successfully on attempt #{}.'.format(attempts))
            successful_generation = True
        else:
            print('Image failed to generate on attempt #{}.'.format(attempts))
        
        if (successful_generation or attempts >= GenerationAttempts):
            break
        else:
            chosen_post_type = None
            
###################################
#:::::::::::::::::::::::::::::::::#
###################################
            
async def start_time_loop():
    """Starts the persistent loop process. This loop will countdown in the console for 10 minutes before processing the current time.
    If the day changes, two processes must be scheduled.
    1. The [AI Prompt building] image/text generation process
    2. The [Twitter / X] upload process
    These two processes will trigger at different times to ensure prior post generation was successful.

    If 'debug' was included as the first runtime argument, the loop will not start. Instead, the post generation process will begin
    and the program will end once completed. The upload process is ignored.
    """
    counter = itertools.count()
    seconds_in_a_minute = 60
    seconds_in_an_hour = 60 * seconds_in_a_minute
    seconds_in_a_day = 24 * seconds_in_an_hour
    end_time = time.time() + 3 * seconds_in_a_day
    
    is_debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'
    if is_debug:
        await start() # Just follow the image logic as usual
    else:
        while time.time() < end_time:
            current_value = next(counter)
            current_time = time.localtime()
            if current_time.tm_min == 0 and current_time.tm_sec == 0:
                print("Time has passed. Current time: {}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            
            time_to_sleep = seconds_in_a_minute * 10
            for i in range(time_to_sleep, 0, -1):
                print(f"  |  {i}  |  ", end="\r", flush=True)
                time.sleep(1)
            print("The time is {time}".format(time=time.strftime("%Y-%m-%d %H:%M:%S")))
    