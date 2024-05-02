import random
import os
import logging
import openai
import holidays
import country_converter as coco
import gptutils as GptUtil
from dotenv import load_dotenv
from typing import Dict
from datetime import date, datetime
from wonderwords import RandomWord

load_dotenv()
DALLE_KEY = os.getenv("DALLE_KEY")

def getSpecialHoliday(date):
    """
    Gets a list of holidays that are celebrated from a handful of selected countries.
    Returns an object representing either the most commonly celebrated holiday,
    or a specialized holiday in country order priority (how they are ordered in the list),
    or none if there is no holiday.
    """
    most_promising_holiday = None

    parsed_date = datetime.strptime(date, "%m-%d-%Y")
    parsed_out_year = '{month}-{day}'.format(month=parsed_date.month, day=parsed_date.day)
    country_code_list = list(holidays.list_supported_countries().keys())
    holiday_dict: Dict[str, list[str]] = {}
    ## List of holidays that should be should be shown but for some reason is not in the holidays package.
    special_holidays: Dict[str, tuple[str, list[str]]] = {
        '8-31': ['Her Birthday', ['JP'] * 99], # Miku's birthday -> x99 countries will guarantee it always is chosen
        '10-30': ['Mischief Night', ['US', 'CA', 'IE', 'UK']],
        '10-31': ['Halloween', ['US', 'JP', 'CA', 'IE', 'UK', 'AU', 'NZ']]
    }
    
    if (parsed_out_year in special_holidays):
        special_day = special_holidays[parsed_out_year]
        holiday_dict[special_day[0]] = special_day[1]
        ## Adding a special day adds it to the list
    
    def add_to_holiday_dict(holiday: str):
        if (holiday):
            holiday_list = holiday.split(',') # multiple holidays separated by comma
            for unique_holiday in holiday_list:
                current_dict_value = holiday_dict.get(unique_holiday)
                if (current_dict_value):
                    holiday_dict[unique_holiday] += [code]
                else:
                    holiday_dict[unique_holiday] = [code]
        
    for code in country_code_list:
        holiday = holidays.country_holidays(code, observed=False).get(date)
        add_to_holiday_dict(holiday=holiday)

    # Once the holiday dictionary is created, we must determine a suitable holiday.
    top_country_count = 0
    ordered_holidays = sorted(holiday_dict.items(), key=lambda x: len(x[1]), reverse=True)
    if(len(ordered_holidays)):
        # list of tuples
        top_country_count = len(ordered_holidays[0][1])
        primary_countries = ['JP', 'US', 'GB', 'KR']
        seconday_countries = ['AU', 'BE', 'BR', 'CA', 'CN', 'DE', 'DK', 'EG', 'ES', 'FR', 'HK', 'IE', 'IN', 'MX', 'NL', 'NO', 'NZ', 'SE', 'SG', 'TH', 'TW', 'UA', 'WS']
        primary_country_bias_cutoff = .1
        seconday_country_bias_cutoff = .29
        # IE if the most popular holiday is celebrated by 20 countries, we will potentially choose a lesser celebrated holiday if it
        # falls within the an acceptable quantity of countries celebrating, compared to the top holiday.
        
        # If a holiday exists that is celebrated in Japan (Miku's birthplace), remove any holiday options that are exclusively non-primary celebrated.
        # This is to help prioritize traditional Japanese holidays while avoiding potentially problematic preferences (IE prioritizing a different religion over Miku's cultural background)
        has_japan_holiday = bool(next((x for x in ordered_holidays if 'JP' in x[1]), False))
        
        def filter_holidays(holiday: tuple[str, list[str]]):
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
            # Manually removing weird holiday outcomes that don't play well with generating art.
            manual_removal_list = ['Substitute Holiday', 'Sunday']
            return len(holiday[1]) > country_count_cutoff and holiday[0] not in manual_removal_list
        
        ordered_holidays = list(filter(filter_holidays, ordered_holidays))
        
        # Of the remaining options, randomly choose one.
        if (len(ordered_holidays)):
            most_promising_holiday = random.choice(ordered_holidays)

    return most_promising_holiday

def generate_random_date(seed):
    random.seed(seed)
    d = random.randint(1, seed)
    random_date = datetime.fromtimestamp(d).strftime('%m-%d-') + '2024'
    print('Random Date: {rDate}'.format(rDate=random_date))
    return random_date

def get_starting_date(use_today: bool, specific_date=''):
    if not (specific_date == ''):
        print('Specific Date: {sDate}'.format(sDate=specific_date))
        return specific_date
    else:
        return generate_random_date(int(datetime.now().strftime('%m%d%H%M%S'))) if use_today == False else date.today().strftime('%m-%d-%Y')

def build_base_prompt(holiday: tuple[str, list[str]] | None):
    main_prompt_action = ''
    if (holiday):
        # Generate art of hatsune miku
        # Generate a twitter post by hatsune miku where she
        if (len(holiday[1]) == 99): # Miku's birthday
            country_mod = ''
        elif (len(holiday[1]) > 2):
            country_mod = '{} and {}'.format(', '.join(holiday[1][:-1]), holiday[1][:-1])
        elif (len(holiday[1]) == 2):
            country_mod = ' and '.join(holiday[1])
        else:
            country_mod = '{}'.format(holiday[1][0])
        country_mod = 'all nations that observe it' if len(holiday[1]) > 3 and not len(holiday[1]) == 99 else country_mod
        main_prompt_action = 'celebrating {holiday_name} with {country_modifier}.'.format(holiday_name=holiday[0], country_modifier=country_mod)
    r = RandomWord()
    
    random_words = [r.word(), r.word(), r.word()]
    print("Helper nouns are: {}".format(' '.join(random_words)))
    prompt_results = GptUtil.ask_for_prompt(random_words)
    
    return {
        'chatgpt': 'Generate a twitter post by Hatsune Miku where she is {}'.format(main_prompt_action),
        'dalle': 'Generate art of Hatsune Miku where she is {}'.format(main_prompt_action)
    }

def start():
    selected_date = get_starting_date(use_today=False, specific_date='') # specific_date used for debugging #6-18-2024 / Islamic
        
    holiday = getSpecialHoliday(selected_date)
    if (holiday):
        cc = coco.CountryConverter()
        country_names = cc.convert(names=holiday[1], to='name_short')
        holiday = (holiday[0], [country_names] if type(country_names) == type('') else country_names)
    
    base_prompt = build_base_prompt(holiday)
    print(base_prompt['chatgpt'])
    print(base_prompt['dalle'])
    
    
# HOLIDAY GENERATING TIPS
# 'Generate Hatsune Miku celebrating X in Y in traditional clothing. Do not include any weaponry or political propaganda.'

# Miku giving a weather report for a very specific town.
# Miku posting photos at a previous sporting event.
# Miku follows Elon Musk's flight location.

start()