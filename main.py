from typing import Dict
import random
import holidays
from datetime import date

import holidays.calendars
import holidays.constants
import holidays.countries
import holidays.holiday_base
import holidays.observed_holiday_base
import holidays.registry

import holidays.locale

def getSpecialHoliday(date):
    """
    Gets a list of holidays that are celebrated from a handful of selected countries.
    Returns an object representing either the most commonly celebrated holiday,
    or a specialized holiday in country order priority (how they are ordered in the list),
    or none if there is no holiday.
    """
    ##country_code_list = ['JP', 'US', 'KR', 'FR', 'DE']
    country_code_list = list(holidays.list_supported_countries().keys())
    holiday_dict: Dict[str, list[str]] = {}
    for code in country_code_list:
        holiday = holidays.country_holidays(code).get(date)
        if (holiday):
            holiday_list = holiday.split(',') # multiple holidays separated by comma
            for unique_holiday in holiday_list:
                current_dict_value = holiday_dict.get(unique_holiday)
                if (current_dict_value):
                    holiday_dict[unique_holiday] += [code]
                else:
                    holiday_dict[unique_holiday] = [code]
    # Once the holiday dictionary is created, we must determine a suitable holiday.
    most_promising_holiday = None
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

def generate_random_date():
    ## pass Custom Holiday for Miku's birthday
    today = date.today()
    print(today)
    holiday = getSpecialHoliday('5-22-2024')
    print(holiday)

def start():
    generate_random_date()
    
# HOLIDAY GENERATING TIPS
# 'Generate Hatsune Miku celebrating X in Y in traditional clothing. Do not include any weaponry or political propaganda.'

start()