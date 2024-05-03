import csv
from . import defs
import json
import logging
import os
import random
from datetime import date, datetime
from dotenv import load_dotenv
from .postGeneration.generate_posts import PostProps, initiate_post_generation
from .postGeneration.holiday_post import get_special_holiday

load_dotenv()
DALLE_KEY = os.getenv("DALLE_KEY")
GenerationAttempts = 1

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
    selected_date = get_starting_date(use_today=False, specific_date='') # specific_date used for debugging #6-18-2024 / Abrahamic
    holiday = get_special_holiday(selected_date)
    
    chosen_post_type: defs.PostType = defs.PostType.HOLIDAY if holiday else None
    attempts = 0
    successful_generation = False # Set this to True when we successfully generate Twitter post content.
    
    while True:
        attempts += 1

        if (chosen_post_type != defs.PostType.HOLIDAY):
            # Select a post type at random with weights.
            population = [defs.PostType.RANDOM, defs.PostType.WEATHER, defs.PostType.SPORTS]
            weights = [0.8, 0.1, 0.1]
            chosen_post_type = random.choices(population, weights, k=1)[0]
        
        post_props = PostProps(type=chosen_post_type, holiday=holiday)
        initiate_post_generation(post_props)
        
        if (successful_generation or attempts >= GenerationAttempts):
            break
        else:
            chosen_post_type = None
    
    ## base_prompt = build_base_prompt(holiday)
    ## print(base_prompt['chatgpt'])
    ## print(base_prompt['dalle'])
    

    ''' 
    supported_countries = cc.convert(names=list(holidays.list_supported_countries().keys()), to='name_short')
    
    with open('./wordList/demonyms.csv', mode='r', encoding="utf8") as infile:
        reader = csv.reader(infile)
        with open('./demonym_dict.json', mode='w', encoding="utf8") as outfile:
            whole_dict = dict(('{}'.format(rows[1]),rows[0]) for rows in reader)
            partial_dict = dict()
            for country in supported_countries:
                try:
                    new_entry = (country, whole_dict[country])
                    partial_dict.update([new_entry])
                except KeyError:
                    continue
            outfile.write(str(partial_dict))
    '''
    
    
# HOLIDAY GENERATING TIPS
# 'Generate Hatsune Miku celebrating X in Y in traditional clothing. Do not include any weaponry or political propaganda.'

# Miku giving a weather report for a very specific town.
# Miku posting photos at a previous sporting event.
# Miku follows Elon Musk's flight location.