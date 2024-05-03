import country_converter as coco
import random
from .. import defs
from datetime import datetime
from typing import Dict

import holidays
from ..gptutils import handle_response, new_user_message, new_assistant_message

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
        primary_countries = defs.MajorCountries
        seconday_countries = defs.MinorCountries
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
            
    if (most_promising_holiday != None):
        cc = coco.CountryConverter()
        country_names = cc.convert(names=most_promising_holiday[1], to='name_short')
        most_promising_holiday = (most_promising_holiday[0], [country_names] if type(country_names) == type('') else country_names)

    return most_promising_holiday

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def traveling_the_world_prompt(include_words: list[str]):
    ## To properly travel the world, Miku needs a bit of information generated for her to get inspiration for what to do.
    ## She may be provided a country to start in. If provided a country, the proper climate should be realized.
    
    word_topics = ''
    if (len(include_words) == 1):
        word_topics = "'{}'".format(include_words[0])
    if (len(include_words) == 2):
        word_topics = "'{}' and '{}'".format(include_words[0], include_words[1])
    if (len(include_words) > 2):
        quoted_words = list(map(lambda x: "'{}'".format(x), include_words))
        word_topics = '{} and {}'.format(', '.join(quoted_words[:-1]), quoted_words[-1])
    print(word_topics)
    system_context = "You are a text generating entity."
    word_generation_instruction = """You will generate 5 random words to output as a JSON object, with the keys being 'Place', 'Thing', 'Verb', Adjective', and 'Adverb'.
    Each random word should be the same part of speech as it's associated key in JSON object. For example, the key 'Verb' should be a word that is linguistically a verb.
    The key for 'Place' should be one of the following: a man-made location, a service, an attraction, a famous monument, a natural location, or other unique spot. Do not use anything to help generate a location.
    The key for 'Thing' can be any common mundane item with a focus on specificity.
    For the 'Adverb' word, it should be an adverb that modifies the 'Verb' word in a realistic way.
    The 'Adjective' should modify the 'Thing' noun.
    Be creative. Mundane and uncommon words are good. Avoid sexual words.
    """
    if (word_topics):
        word_topics = "The theme of the words can relate to: {}".format(word_topics)

    messages = [{
        "role": "system",
        "content": system_context,
    }, {
        "role": "assistant",
        "content": word_generation_instruction,
    }]
    
    def append_conversation(gpt_response):
        if (gpt_response):
            messages.append(new_assistant_message(gpt_response))
        return gpt_response
    
    response = append_conversation(handle_response(
        messages,
        new_user_message("""Please generate me a stringified JSON object of random mundane but specific words. {}""".format(word_topics))
    ))
    
    print(response)
    
    response = append_conversation(handle_response(
        messages,
        new_user_message("""Look over the words you generated and evaluate them. Replace 2 of the words and keep the remaining 3.
                         The new words should be less common synonyms. Output another JSON object with the same structure as the last one.
                         Ensure that each value only consists of that part of speech. For example, no adjectives should be applied to a Place or Thing noun.
                         """)
    ))
    
    print(response)
    
    response = append_conversation(handle_response(
        messages,
        new_user_message("""Using the words that you just generated, I want you to write a single imperative sentence from the 3rd person beginning with 'Generate art of Hatsune Miku'.
        The remainder of the sentence should capture the essence of the words that were just generated. The verb should be applied to what Miku is doing.
        Avoid overly violent or sexual themes.
        The adverb will typically modify the verb. Feel free to use the 'Place' and 'Thing' nouns in a creative way. It does not need to relate to Miku, her music, or technology.
        """)
    ))
    
    dalle_prompt = messages[-1]['content']
    messages[-1]['content'] = messages[-1]['content'].replace('Generate art of ', '') # Remove 'Generate art of' so we stop getting art-related twitter posts.
    print(dalle_prompt)

    response = append_conversation(handle_response(
        messages,
        new_user_message("""You are now Hatsune Miku, a 16 year old girl and hugely famous virtual pop idol. Given the previous sentence you just gave me, I want you to generate a twitter post.
                         The twitter post can be no longer than 280 characters. You, as Hatsune Miku, should describe what you did today based on the previous prompt
                         and as if you are addressing your followers. Try to capture the emotion that you felt based on whether the words used are positive or negative.
                         You can make up events that happened to you while doing this.
                         Be descriptive about how you feel.
                         Possibly talk about your music and songs.
                         Do not use too many adverbs. Do not copy the previous sentence word for word.
                         Any twitter hashtags should be related to the post.
                         Include a couple emojis that are relevant.
                         If the location is a vague location, give it a more specific name to make it sound more like a real place in Miku's world.
                         If the location is a real location, keep the real name.
                         The twitter post should end with a japanese sentence.""")    
    ))
    
    print(response)
    
    #if (response):
        # dalle_tail_end = response.split('Generate art of Hatsune Miku ')[1]
        # print(dalle_tail_end)
    '''
    response = append_conversation(handle_response(
        messages,
        new_user_message("Given the previous sentence you generated. Please generate me a twitter post with no more than 280 characters. The twitter post should be written as Hatsune Miku. Do not mention the whole prompt word for word. Miku should describe what she did and add additional comments about it such as how she feels, who she did it with, where it took place, and what was going on nearby. Keep it cute and friendly. Feel free to make up stuff or exaggerate since this is fictional.")    
    ))
    '''
    return response

###################################
#:::::::::::::::::::::::::::::::::#
###################################

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
    prompt_results = traveling_the_world_prompt(random_words)
    
    return {
        'chatgpt': 'Generate a twitter post by Hatsune Miku where she is {}'.format(main_prompt_action),
        'dalle': 'Generate art of Hatsune Miku where she is {}'.format(main_prompt_action)
    }
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def generate_post():
    return None