import json
import logging
from pathlib import Path
import random
from typing import Dict
from .. import gptutils as gpt
from .. import defs

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def generate_social_media_post(art_prompt: str):
    system_context = "You are a generating entity capable of converting art prompts into personable Twitter posts."

    messages = [{
        "role": "system",
        "content": system_context,
    }, {
        "role": "assistant",
        "content": art_prompt,
    }]

    output = gpt.handle_response(
        messages,
        gpt.new_user_message("""You are now Hatsune Miku, a 16 year old girl and hugely famous virtual pop idol. Given the previous art prompt you just gave me, I want you to generate a twitter post.
                         The twitter post can be no longer than 280 characters. You, as Hatsune Miku, should describe what you did today based on the previous art prompt
                         and as if you are addressing your followers. Try to capture the emotion that you felt based on whether the words used are positive or negative.
                         You can make up events that happened to you while doing this.
                         Be descriptive about how you feel.
                         Possibly talk about your music and songs.
                         Make sure to talk about the location you're at and the object you're there with.
                         Do NOT use many adverbs. Do NOT copy the previous art prompt word for word.
                         You MUST be Hatsune Miku and describe your day as the scene depicts.
                         Any twitter hashtags should be related to the post.
                         Include a couple emojis that are relevant.
                         The twitter post should end with an appropriate japanese sentence.
                         REMEMBER to IGNORE THE FIRST SENTENCE of the previous art prompt starting with "Generate art of".""")    
    )
    
    print('TWITTER', output['response'] or 'No Response?')
    logging.info('Twitter post: {}'.format(output['response']))

    return output

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def generate_prompt_for_stability(location: str, item: str):
    system_context = "You are a prompt generating entity tasked with outputting ONLY the requested prompt."
    initial_word_generation_instruction = """
    I would like you to generate me a prompt. This prompt is intended for generative art AI models, and as such should begin with our protagonist Hatsune Miku.
    The start of the prompt should begin with "Generate art of Hatsune Miku" and specify the art style of the generation to be something like "{art_style}". From there, I need a verbose description of Miku spending her time at this specified location: "{location}".
    Make sure describe this location with information about the surrounding area that should be visible from a still shot image. Ask yourself, "would other people accompany her in this place or is it likely that she would be alone?".
    If you determine she is alone, do not specify anything. If people are nearby, make sure that use one or more demonyms to describe their origin.
    The following object should be integrated into the scene: "{item}". Describe the still shot image by explaining what Miku is doing with this object using an action verb. The {item} object and what Miku is doing with it should be a priority.
    If the item is a food, she should be eating it. If the item is a wearable article, she should be wearing it. Other types of items should be interacted with appropriately. The item SHOULD BE HERS.
    Miku can optionally have an emotional expression drawn in response to the object.
    Given the combination of location and object, the whole scene may be positive or negative and the tone of the whole prompt should reflect in this way.
    If the situation calls for it, Miku should be moving or otherwise doing a physical action to interact with the scene.
    Make sure to include a description of her typical clothing but modify the clothing based on the action that she is doing in the scene. For example, if it is cold then her clothing should be something cozier.
    Lastly, take note to describe some of the details of the scene, such as the lighting conditions, weather conditions, or the time of day and how it reflects the objects in the scene.
    REMEMBER, since this scene is for art generation, I NEED this description to reflect a static place in time. Miku is only in one place doing one thing.
    The output MUST be 10 sentences long.
    """.format(location=location, item=item, art_style=gpt.get_random_visual_art_prompt_intro(force_style=None))
    messages = [{
        "role": "system",
        "content": system_context,
    }]
    
    # output.history / output.response
    output = gpt.handle_response(
        messages,
        gpt.new_user_message(initial_word_generation_instruction)
    )
    
    print('OUTPUT', output['response'])
    return output

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def generate_post():
    # return defs.PostData(socialMediaPrompt='test', artPrompt='test', inscribedText='TEST INSCRIBED')
    ROOT_DIR = Path(__file__).parent
    locations_file = '{root}/wordList/locations.json'.format(root=ROOT_DIR)
    items_file = '{root}/wordList/items.json'.format(root=ROOT_DIR)
    art_prompt = {
        'response': ''
    }
    social_media_text = {
        'response': ''
    }
    with open(locations_file, 'r', encoding='UTF-8') as location_f:
        with open(items_file, 'r', encoding='UTF-8') as item_f:
            locations_dict: Dict[str, str] = json.load(location_f)
            items_dict = json.load(item_f)
            random_item = random.choice(items_dict)
            random_loc_type = random.choice(locations_dict)
            random_loc = random.choice(random_loc_type['list'])
            print("{} : {}".format(random_item, random_loc))
            art_prompt = generate_prompt_for_stability(random_loc, random_item)
            social_media_text = generate_social_media_post(art_prompt['response'])
            
    # To be written to the image
    inscribed_text = '{} / {}'.format(random_item, random_loc)
            
    data = defs.PostData(socialMediaPrompt=social_media_text['response'], artPrompt=art_prompt['response'], inscribedText=inscribed_text)
    return data