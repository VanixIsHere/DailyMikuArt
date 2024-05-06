from functools import reduce
import random
import country_converter as coco
import json
from .. import defs
from ..gptutils import get_random_visual_art_prompt_intro
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
import logging

import holidays

###################################
#:::::::::::::::::::::::::::::::::#
###################################

HolidayDictionary = Dict[str, list[str]]
HolidayType = tuple[str, list[str], defs.DayType]

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def get_special_holiday(date):
    """
    Gets a list of holidays that are celebrated from a handful of selected countries.
    Returns an object representing either the most commonly celebrated holiday,
    or a specialized holiday in country order priority (how they are ordered in the list),
    or none if there is no holiday.
    """
    most_promising_holiday: HolidayType | None = None

    parsed_date = datetime.strptime(date, "%m-%d-%Y")
    parsed_out_year = '{month}-{day}'.format(month=parsed_date.month, day=parsed_date.day)
    country_code_list = list(holidays.list_supported_countries().keys())
    holiday_list: list[HolidayType] = []
    ## List of holidays that should be should be shown but for some reason is not in the holidays package.
    special_holidays: Dict[str, HolidayType] = {
        '8-31': ['Her Birthday', defs.AllWeightedCountries, defs.DayType.BIRTHDAY], # Miku's birthday -> x99 countries will guarantee it always is chosen
        '10-30': ['Mischief Night', ['US', 'CA', 'IE', 'UK'], defs.DayType.HOLIDAY],
        '10-31': ['Halloween', ['US', 'JP', 'CA', 'IE', 'UK', 'AU', 'NZ'], defs.DayType.HOLIDAY]
    }
    
    logging.info('Searching for holidays that exist on {date}.'.format(date=date))
    
    if (parsed_out_year in special_holidays):
        special_day = special_holidays[parsed_out_year]
        #logging.info('FOUND: {holidayName} with {countryCount} participating: {countries}'.format(holidayName=holiday[0], countryCount=len(holiday[1]), countries=holiday[1]))
        holiday_list.append(special_day)
        ## Adding a special day adds it to the list
    
    def add_to_holiday_list(holiday: str, country_code: str):
        if (holiday):
            holidays_separated = holiday.split(',') # multiple holidays separated by comma
            for unique_holiday in holidays_separated:
                # TODO: determine dayType of holiday here - may add more types i.e. religious
                dayType = defs.DayType.HOLIDAY
                try:
                    def mapToName(n):
                        return n[0]
                    index = list(map(mapToName, holiday_list)).index(unique_holiday)
                    holiday_list[index][1].append(country_code) # Update country list
                except ValueError:
                    holiday_list.append((unique_holiday, [code], dayType))
        
    for code in country_code_list:
        holiday = holidays.country_holidays(code, observed=False).get(date)
        add_to_holiday_list(holiday=holiday, country_code=code)

    # Once the holiday dictionary is created, we must determine a suitable holiday.
    top_country_count = 0
    
    # for holiday in holiday_list:
        # logging.info('FOUND: {holidayName} with {countryCount} participating: {countries}'.format(holidayName=holiday[0], countryCount=len(holiday[1]), countries=holiday[1]))
    
    ordered_holidays = sorted(holiday_list, key=lambda x: len(x[1]), reverse=True)
    if(len(ordered_holidays)):
        # list of tuples
        top_country_count = len(ordered_holidays[0][1])
        primary_countries = defs.MajorCountries
        seconday_countries = defs.MinorCountries
        primary_country_bias_cutoff = .1
        seconday_country_bias_cutoff = .29
        # IE if the most popular holiday is celebrated by 20 countries, we will potentially choose a lesser celebrated holiday if it
        # falls within the an acceptable quantity of countries celebrating, compared to the top holiday.
        
        # If a holiday exists that is celebrated in Japan (Miku's birthplace), remove any holiday options that are exclusively non-primary celebrated.
        # This is to help prioritize traditional Japanese holidays while avoiding potentially problematic preferences (IE prioritizing a different religion over Miku's cultural background)
        has_japan_holiday = bool(next((x for x in ordered_holidays if 'JP' in x[1]), False))
        
        def filter_holidays(holiday: HolidayType):
            country_count = len(holiday[1])
            holiday_specific_cutoff = 2 # Essentially filtering out unless holiday_specific_cutoff is < 1.
            if not (has_japan_holiday):
                for country in seconday_countries:
                    if (country in holiday[1]):
                        holiday_specific_cutoff = seconday_country_bias_cutoff
                        break
            for country in primary_countries:
                if (country in holiday[1]):
                    holiday_specific_cutoff = primary_country_bias_cutoff
                    break
            country_count_cutoff = top_country_count * holiday_specific_cutoff
            
            def not_a_problem(name: str): # TODO: Figure out a better way to support some of these holidays
                # Manually removing weird holiday outcomes that don't play well with generating art.
                full_name_removal_list = ['Substitute Holiday', 'Sunday', 'Juneteenth National Independence Day']
                partial_name_removal_list = ['substituted from', 'King Bhumibol'] ## Example: Day off (substituted from 09/29/2024)
                for partial_name in partial_name_removal_list:
                    if (partial_name in name):
                        return False
                return name not in full_name_removal_list

            return country_count > country_count_cutoff and not_a_problem(holiday[0])
        
        ordered_holidays = list(filter(filter_holidays, ordered_holidays))
        
        # Of the remaining options, randomly choose one.
        if (len(ordered_holidays)):
            most_promising_holiday = random.choice(ordered_holidays)

    if (most_promising_holiday):
        cc = coco.CountryConverter()
        country_names = cc.convert(names=most_promising_holiday[1], to='name_short')
        most_promising_holiday = (most_promising_holiday[0], [country_names] if isinstance(country_names, str) else country_names, most_promising_holiday[2])
        print(most_promising_holiday)

    return most_promising_holiday

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def modify_prompt_for_social_media(base_prompt: str, holiday: HolidayType):
    logging.info('Modifying base prompt for social media text.')
    prompt_sentences: list[str] = [base_prompt]
    return ' '.join(prompt_sentences)

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def modify_prompt_for_dalle(base_prompt: str, holiday: HolidayType):
    logging.info('Modifying base prompt for art generation.')
    prompt_sentences: list[str] = [base_prompt]
    
    ROOT_DIR = Path(__file__).parent
    demonym_file = '{root}/wordList/demonym_dict.json'.format(root=ROOT_DIR)
    demonym_count = 0
    demonym_filler = None
    with open(demonym_file, 'r') as f:
        demonym_dict: Dict[str, str] = json.load(f)
        def reduceToDemonymList(array: list[str], n: str):
            try:
                demonym = demonym_dict[n]
                array.append(demonym)
            except Exception:
                pass
            return array
        demonym_list = reduce(reduceToDemonymList, holiday[1], [])
        demonym_count = len(demonym_list)
        if (demonym_count > 3 or demonym_count == 0):
            demonym_filler = ' '
        elif (demonym_count > 2):
            demonym_filler = ' {} or {} '.format(', '.join(demonym_list[:-1]), demonym_list[:-1])
        elif (demonym_count == 2):
            demonym_filler = ' {} '.format(' or '.join(demonym_list))
        else:
            demonym_filler = ' {} '.format(demonym_list[0])
        clothing_prompt = "Ensure she is wearing culturally appropriate" + demonym_filler + "clothing for the event."
        prompt_sentences.append(clothing_prompt)
            
        if (demonym_count == 1):
            prompt_sentences.append("She should be in a recognizable location in {place} and there should be other people of {demonym} nationality in frame.".format(place=holiday[1][0], demonym=demonym_list[0]))
    
    return ' '.join(prompt_sentences)
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def generate_post(holiday: HolidayType):
    country_list = holiday[1]
    country_count = len(country_list)
    logging.info('Begin generation for the holiday of "{holiday}" with {countryCount} participating: {countries}'.format(holiday=holiday[0], countryCount=country_count, countries=holiday[1]))
    day_type = holiday[2]
    if (day_type == defs.DayType.BIRTHDAY): # Miku's birthday
        celebrate_with = 'her fans and music producers'
    elif (country_count > 3):
        celebrate_with = 'all nations that observe it'
    elif (country_count > 2):
        celebrate_with = '{} and {}'.format(', '.join(country_list[:-1]), country_list[:-1])
    elif (country_count == 2):
        celebrate_with = ' and '.join(country_list)
    else:
        celebrate_with = '{}'.format(country_list[0])
    main_prompt_action = 'celebrating {holiday_name} with {celebrate_with}.'.format(holiday_name=holiday[0], celebrate_with=celebrate_with)
    
    social_media_prompt = modify_prompt_for_social_media('Generate a twitter post by Hatsune Miku where she is {}'.format(main_prompt_action), holiday)
    logging.info('Social media prompt generated: "{prompt}"'.format(prompt=social_media_prompt))

    # Forcing Holiday Posts to adopt 'Studio Art' styles all the time because they are they are the least problematic outcomes. Can't be celebrating post-apocalyptic Easter Sunday, ya know?
    dalle_prompt = modify_prompt_for_dalle('{introprompt} {mainprompt}'.format(introprompt=get_random_visual_art_prompt_intro(force_style=defs.Style.StudioArt), mainprompt=main_prompt_action), holiday)
    logging.info('Art generation prompt generated: "{prompt}"'.format(prompt=dalle_prompt))

    print ({
        'chatgpt': social_media_prompt,
        'dalle': dalle_prompt
    })