from . import keys
import random
from typing import Optional
from openai import OpenAI
from . defs import Style, WeightedOption

client = OpenAI(
    api_key=keys.CHATGPT
)

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def new_assistant_message(prompt: str):
    return {
        "role": "assistant",
        "content": prompt,
    }
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def new_user_message(prompt: str):
    return {
        "role": "user",
        "content": prompt,
    }

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def handle_response(conversation_history: list[dict[str, str]], new_prompt: dict[str, str], gpt_model='gpt-3.5-turbo'):
    conversation_history.append(new_prompt)
    chat_completion = client.chat.completions.create(
        model=gpt_model,
        messages=conversation_history,
    )
    response = chat_completion.choices[0].message.content
    
    def append_conversation(conversation, gpt_response):
        if (gpt_response):
            conversation.append(new_assistant_message(gpt_response))
        return gpt_response

    full_conversation = append_conversation(conversation_history, response)
    return {
        'history': full_conversation,
        'response': response,
    }

###################################
#:::::::::::::::::::::::::::::::::#
###################################

'''
def append_conversation(gpt_response):
        if (gpt_response):
            messages.append(new_assistant_message(gpt_response))
        return gpt_response
'''

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def get_random_visual_art_prompt_intro(force_style: Optional[Style]):
    ## Randomly choose a broad art style based on weights
    style_options: list[WeightedOption] = [
        { 'name': Style.StudioArt, 'weight': 0.6 },
        { 'name': Style.Art, 'weight': 0.25 },
        { 'name': Style.Photo, 'weight': 0.15 }
    ]
    random_broad_style = random.choices([d['name'] for d in style_options], [d['weight'] for d in style_options], k=1)[0] if force_style == None else force_style
    random_photo_style = None
    random_art_style = None
    random_studio_art_style = None
    if (random_broad_style == Style.Photo):
        photo_options: list[WeightedOption] = [
            { 'name': 'a daguerreotype photo', 'weight': 0.1 },
            { 'name': 'a disposable camera photo', 'weight': 0.1 },
            { 'name': 'a double exposure photo', 'weight': 0.1 },
            { 'name': 'a fashion photography photo', 'weight': 0.1 },
            { 'name': 'a long exposure, slow shutter speed photo', 'weight': 0.1 },
            { 'name': 'a smartphone camera photo', 'weight': 0.1 },
            { 'name': 'an autochrome photo', 'weight': 0.1 }
        ]
        random_photo_style = '{} '.format(random.choices([d['name'] for d in photo_options], [d['weight'] for d in photo_options], k=1)[0])
    elif (random_broad_style == Style.Art):
        art_options: list[WeightedOption] = [
            { 'name': 'post-apocalyptic', 'weight': 0.1 },
            { 'name': 'cyberpunk', 'weight': 0.1 },
            { 'name': 'fantasy', 'weight': 0.1 },
            { 'name': 'gothic', 'weight': 0.1 },
            { 'name': 'sci-fi', 'weight': 0.1 },
            { 'name': 'vaporwave', 'weight': 0.1 },
        ]
        random_art_style = '{} '.format(random.choices([d['name'] for d in art_options], [d['weight'] for d in art_options], k=1)[0])
    elif (random_broad_style == Style.StudioArt):
        studio_art_options = [
            { 'name': 'Hayao Miyazaki', 'weight': 0.22 },
            { 'name': 'Bill Watterson', 'weight': 0.08 },
            { 'name': 'Disney', 'weight': 0.08 },
            { 'name': 'Pixar', 'weight': 0.08 },
            { 'name': 'Sanrio and Friends', 'weight': 0.18 },
            { 'name': 'Studio Trigger', 'weight': 0.16 },
            { 'name': 'Studio Mappa', 'weight': 0.16 },
            { 'name': 'Akira Toriyama', 'weight': 0.08 }
        ]
        random_studio_art_style = ' in the style of {}'.format(random.choices([d['name'] for d in studio_art_options], [d['weight'] for d in studio_art_options], k=1)[0])
        
    art_section = '' if random_photo_style else '{}art '.format(random_art_style or '')
    
    if (random_photo_style or random_art_style or random_studio_art_style):
        return 'Generate {photo}{art}of Hatsune Miku{studioart}'.format(photo=random_photo_style or '', art=art_section, studioart=random_studio_art_style or '')

    return 'Generate art of Hatsune Miku' # Fallback