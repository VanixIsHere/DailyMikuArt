
import sys
from .. import defs
from .. import gptutils as gpt
from ..gptutils import get_random_visual_art_prompt_intro
from datetime import datetime
from functools import reduce
from pathlib import Path
from typing import Dict, Optional
import country_converter as coco
import holidays
import json
import logging
import random

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
    most_promising_holiday: defs.HolidayType | None = None

    parsed_date = datetime.strptime(date, "%m-%d-%Y")
    parsed_out_year = '{month}-{day}'.format(month=parsed_date.month, day=parsed_date.day)
    country_code_list = list(holidays.list_supported_countries().keys())
    holiday_list: list[defs.HolidayType] = []
    ## List of holidays that should be should be shown but for some reason is not in the holidays package.
    special_holidays: Dict[str, defs.HolidayType] = {
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
        
        def filter_holidays(holiday: defs.HolidayType):
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
                partial_name_removal_list = ['substituted from', 'King Bhumibol', 'estimated'] ## Example: Day off (substituted from 09/29/2024)
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

def modify_prompt_for_social_media(base_prompt: str, holiday: defs.HolidayType):
    logging.info('Modifying base prompt for social media text.')
    prompt_sentences: list[str] = [base_prompt]
    return ' '.join(prompt_sentences)

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def modify_prompt_for_art_generation(base_prompt: str, holiday: defs.HolidayType):
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

def generate_post(props: defs.PostProps):
    holiday = props.holiday
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
        
    system_context = """Hatsune Miku is a 16 year old pop idol Vocaloid who is loved worldwide for her youthful energy, innocence, and boundless creativity.
                    She exudes a cheerful and playful demeanor, often depicted with a smile on her face and a twinkle in her eyes.
                    Miku's character is imbued with a sense of curiosity and wonder, reflecting the limitless possibilities of the digital world she inhabits.
                    Despite being a virtual entity, she connects with fans on a personal level.
                    Miku's persona radiates positivity and optimism, serving as a beacon of inspiration for fans worldwide.
                    
                    YOU are Hatsune Miku. You are on your continuous worldwide travel and are writing about your travels in the form of an informative blog post, written in a non-superfluous, college writing level.
                    Keep it professional and answer in plain English. Get straight to the point as if the writing was from Wikipedia.
                    Today's date is a holiday which will be provided to you by the user. Miku's blog post will be about her day celebrating this holiday with the groups of people and countries that typically celebrate it.
                    Pick a location at random in a place that celebrates this holiday. This can be a city or another notable place of celebration.
                    For example, some holidays such as Easter or Christmas are family oriented, so she would spend time with her family or Miku would be invited to celebrate with a host family.
                    Her post should include an event involved with the holiday and how she participated.
                    Ensure that the post captures the vibes of the holiday. Some holidays are purely for fun and people do not follow their cultural history.
                    Miku SHOULD be extremely aware of cultural norms, such as not eating pork in various abrahamic religions. She should avoid doing the wrong thing.
                    Use any additional context to decide on a creative outcome for your blog post.
                    Do NOT include any newline characters in any responses you give.
                    """
    messages = [{
        "role": "system",
        "content": system_context,
    }]
    
    prompts = []
    prompts.append(f"I would like you to generate me a one paragraph long blog post on your celebration of '{holiday[0]}' with {celebrate_with}.")
    output = gpt.handle_response(
        messages,
        gpt.new_user_message(' '.join(prompts))
    )
    print(output['response'])
    messages.append(gpt.new_assistant_message(output['response']))
    
    prompts = []
    prompts.append(f"""Turn this blog post into a twitter post. Ensure the length of the post is less than {defs.TwitterPostLength} characters.
                   The post should end with a relevant japanese sentence.
                   Include appropriate emojis that make sense.
                   When calculating the length of the twitter post, emojis and japanese characters count as 2 instead of 1.
                   """)
    social_media_text = gpt.handle_response(
        messages,
        gpt.new_user_message(' '.join(prompts))
    )
    print(social_media_text['response'])
    messages.append(gpt.new_assistant_message(output['response']))
    
    art_style = gpt.get_random_visual_art_prompt_intro(force_style=None)
    prompts = []
    prompts.append(f"""You are no longer Hatsune Miku. You are a prompt generating entity useful for describing imagery intended for generative art AI.
                   I now need you to generate an art prompt beginning with an imperative sentence and the style described as '{art_style}'.
                   You MUST make sure this prompt is not longer than 480 characters. Shorten the prompt and make it concise in order to get to this goal.
                   The remainder of the art prompt needs to be a description of a still image based the previous responses you gave me.
                   Hatsune Miku just spent the day celebrating {holiday[0]} and partook in traditions. Take this interaction and describe it as if it were a still frame in time.
                   It being a still frame should not be stated in the text.
                   Keep it professional but answer in plain English. Get straight to the point. Don't be superfluous and mention how things are symbolized.
                   To properly describe the tone you can describe the weather and the way certain lights illuminate parts of the scene.
                   """)
    art_prompt = gpt.handle_response(
        messages,
        gpt.new_user_message(' '.join(prompts))
    )
    print(art_prompt['response'])

    inscribed_text = 'Celebrating {}'.format(holiday[0])

    data = defs.PostData(socialMediaPrompt=social_media_text['response'], artPrompt=art_prompt['response'], inscribedText=inscribed_text)
    return data