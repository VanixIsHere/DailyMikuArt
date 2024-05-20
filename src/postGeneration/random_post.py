import json
import logging
from pathlib import Path
import random
import sys
from typing import Dict
from .. import gptutils as gpt
from .. import defs

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def add_context_to_prompt_item(props: defs.PostProps, location_type: str, location: str, item_type: str, item: str):
    context: list[str] = []
    if item_type == 'Food':
        context.append(f"""Since '{item}' is a food item there are a number of ways you can describe your interaction with this. Some example are:
                       1. You ate '{item}';
                       2. You prepared a dish that is popular in '{location}' that uses '{item}';
                       3. You harvested '{item}' from a place in '{location}';
                       4. You were introduced to a local specialty of '{item}';
                       Make sure that in talking about '{item}', it makes appropriate sense. For example, you cannot harvest an Apple Pie.
                       """)
    elif item_type == 'Instrument':
        context.append(f"""Since '{item}' is a musical instrument, you are playing this instrument.
                       Remember that you yourself are a musicial and pop idol, so you have an affinity for good music and how things sound.
                       """)
    elif item_type == 'Article':
        context.append(f"""Since '{item}' is a wearable article, you ARE wearing this.
                        Remember, you did NOT find this in the middle of nature.
                        Your reason for donning this item is important because people wear things for a number of reasons. It can be for style purposes, religious purposes, weather purposes, and so on.
                       """)
    elif item_type == 'Animal':
        context.append(f"""Since '{item}' is an animal there are a number of ways you can describe your interactions with this. Some examples are:
                       1. You saw a wild '{item}';
                       2. You befriended a wild '{item}';
                       3. You acquired a pet '{item}';
                       4. You saw a group of wild '{item}', but make sure the animal is pluralized;
                       """)
    elif 'Generic' in item_type and 'Item' in item_type:
        context.append(f"""Since '{item}' is a generic item there are ton of ways you can describe your interactions with this. Some examples are:
                       1. You found a '{item}';
                       2. You saw a '{item}';
                       3. You held a '{item}';
                       4. You purchased a '{item}';
                       5. You found your lost '{item}';
                       """)
        if 'Generic Japanese Item' in item_type:
            context.append(f"""Since '{item}' originates from Japan, you can include relevant cultural information about this item's history with you.
                           Remember that you are from Japan, so you are knowledgable about this item.
                           """)
    elif item_type == 'Vehicle':
        context.append(f"""Since '{item}' is a vehicle there are a number of ways you can describe your interactions with this. Some examples are:
                       1. You drove a '{item}';
                       2. You rode in a '{item}';
                       3. You saw a really cool looking '{item}';
                       4. You raced in a sporty '{item}';
                       """)
    else:
        context = []
        
    if len(context) == 0:
        return ''
    return ' '.join(context)

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def generate_post_data(props: defs.PostProps, location_type: str, location: str, item_type: str, item: str):
    system_context = """Hatsune Miku is a 16 year old pop idol Vocaloid who is loved worldwide for her youthful energy, innocence, and boundless creativity.
                    She exudes a cheerful and playful demeanor, often depicted with a smile on her face and a twinkle in her eyes.
                    Miku's character is imbued with a sense of curiosity and wonder, reflecting the limitless possibilities of the digital world she inhabits.
                    Despite being a virtual entity, she connects with fans on a personal level.
                    Miku's persona radiates positivity and optimism, serving as a beacon of inspiration for fans worldwide.
                    
                    Use this voice: casual, friendly, and storytelling.
                    Use this tone: conversational and slightly descriptive. 
                    Use this style: informal.
                    
                    YOU are Hatsune Miku. You are on your continuous worldwide travel and are writing about your travels in the form of an informative blog post, written in a non-superfluous, college writing level.
                    Keep it professional and answer in plain English. Get straight to the point as if the writing was from Wikipedia.
                    The two most important aspects of each entry is the location you are visiting and an item. The location and item will be will be provided to you, along with suggestions on how to integrate the item into your blog post.
                    Use any additional context to decide on a creative outcome for your blog post.
                    Do NOT include any newline characters in any responses you give.
                    """
    messages = [{
        "role": "system",
        "content": system_context,
    }]
    
    indefinite_location_types = ['National Geography']
    
    prompts = []
    prompts.append(f"I would like you to generate me a one paragraph long blog post on your visit to '{location}'.")
    prompts.append("Refer to the location using indefinite articles but come up with a less vague name that your location is in.") if location_type in indefinite_location_types else prompts.append("Refer to '{}' by it's real world name.".format(location))
    prompts.append("'{}' is your relevant item on the trip.".format(item))
    prompts.append(add_context_to_prompt_item(props, location_type, location, item_type, item))
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
    prompts.append(f"""You are no longer Hatsune Miku. You are a prompt generating entity useful for describing imagery intended for generative AI.
                   I now need you to generate an art prompt beginning with the imperative sentence: "Generate art of Hatsune Miku" and describe the style to be '{art_style}'.
                   You MUST make sure this prompt is not longer than 480 characters. Shorten the prompt and make it concise in order to get to this goal.
                   The remainder of the art prompt needs to be a description of a still image based the previous responses you gave me.
                   Hatsune Miku just spent the day at '{location}' and interacted with '{item}'. Take this interaction and describe it as if it were a still frame in time.
                   Keep it professional but answer in plain English. Get straight to the point. Don't be superfluous and mention how things are symbolized.
                   To properly describe the tone you can describe the weather and the way certain lights illuminate parts of the scene.
                   """)
    art_prompt = gpt.handle_response(
        messages,
        gpt.new_user_message(' '.join(prompts))
    )
    print(art_prompt['response'])
    
    # To be written to the image
    inscribed_text = '{} / {}'.format(item, location)
    data = defs.PostData(socialMediaPrompt=social_media_text['response'], artPrompt=art_prompt['response'], inscribedText=inscribed_text)
    return data

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def generate_post(props: defs.PostProps):
    # return defs.PostData(socialMediaPrompt='test', artPrompt='test', inscribedText='TEST INSCRIBED')
    ROOT_DIR = Path(__file__).parent
    locations_file = '{root}/wordList/locations.json'.format(root=ROOT_DIR)
    items_file = '{root}/wordList/items.json'.format(root=ROOT_DIR)
    data = defs.PostData(socialMediaPrompt='', artPrompt='', inscribedText='')
    with open(locations_file, 'r', encoding='UTF-8') as location_f:
        with open(items_file, 'r', encoding='UTF-8') as item_f:
            locations_dict: Dict[str, str] = json.load(location_f)
            items_dict: Dict[str, str] = json.load(item_f)
            
            def get_list_count(n):
                return len(n['list'])
            
            item_type_weights = list(map(get_list_count, items_dict))
            random_item_type = random.choices(items_dict, item_type_weights, k=1)[0]
            random_item = random.choice(random_item_type['list'])
            
            loc_type_weights = list(map(get_list_count, locations_dict))
            random_loc_type = random.choices(locations_dict, loc_type_weights, k=1)[0]
            random_loc = random.choice(random_loc_type['list'])
            print("{} : {}".format(random_item, random_loc))
            data = generate_post_data(props, random_loc_type, random_loc, random_item_type, random_item)
    return data