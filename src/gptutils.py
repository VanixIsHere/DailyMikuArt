from . defs import Style, WeightedOption
from . import keys
from openai import OpenAI
from typing import Optional
import random

client = OpenAI(
    api_key=keys.CHATGPT
)

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def new_assistant_message(prompt: str):
    """Turns the input 'prompt' parameter into a usable Dict object that can be passed into ChatGPT message history as an assistant message.

    Args:
        prompt (str): The content for the new assistant message.

    Returns:
        Dict[str, str]: A dictionary object intended for OpenAI ChatGPT's assistant role messages.
    """
    return {
        "role": "assistant",
        "content": prompt,
    }
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def new_user_message(prompt: str):
    """Turns the input 'prompt' parameter into a usable Dict object that can be passed into ChatGPT message history as a user message.

    Args:
        prompt (str): The content for the new user message.

    Returns:
        Dict[str, str]: A dictionary object intended for OpenAI ChatGPT's user role messages.
    """
    return {
        "role": "user",
        "content": prompt,
    }

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def handle_response(conversation_history: list[dict[str, str]], new_prompt: dict[str, str], gpt_model='gpt-3.5-turbo'): #gpt-4 / gpt-3.5-turbo
    """Submits a 'new_prompt' user message to ChatGPT and handles appending the response to the resulting output Dict.

    Args:
        conversation_history (list[dict[str, str]]): A list of conversation history between ChatGPT's system, assistant, and user messages.
        new_prompt (dict[str, str]): A new user message to be passed to ChatGPT for a chat completion.
        gpt_model (str, optional): A string of the gpt model to target for this chat completion. Defaults to 'gpt-3.5-turbo' unless the model is overridden in .env.

    Returns:
        Dict[str, str | list[dict[str, str]]]: A dictionary containing the resulting chat history for further processing (key='history') and
        the response from the 'new_prompt' that was passed in (key='response').
    """
    conversation_history.append(new_prompt)
    chat_completion = client.chat.completions.create(
        model=gpt_model,
        messages=conversation_history,
        temperature=0.2
    )
    response = chat_completion.choices[0].message.content
    
    def append_conversation(conversation: list[dict[str, str]], gpt_response: str):
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
    """Selects a visual art style at random and builds a one sentence prompt for declaring the image generation style.
       The visual art styles are broken down into categories: 'Studio Art', 'Art', and 'Photo'. These are all weighted differently in the RNG selection.
       - 'Studio Art' consists of various real studio names or specific artist names, generally sticking to anime/cartoon styles. These result in more
         familiar imagery of Miku and tends to keep locations and items relatively intact and historically accurate.
       - 'Art' consists of various popular genres of art imagery not defined by a specific artist. These generally result in art that is more
         fantastical in nature, with the possibility of real world locations being greatly altered to fit the theming.
       - 'Photo' consists of various forms of photography that result in more realistic images of Miku. These can result in images that
         portray Miku as almost doll-like or 3D rendered. Most of these images are muted in color, grayscale, or washed out.

    Args:
        force_style (Optional[Style]): An optional style can be specified to get the random choice to be a specific category.

    Returns:
        str: A full sentence prompt for generating Hatsune Miku art with a random visual art style.
    """
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
            { 'name': 'Hiroyuki Imaishi', 'weight': 0.16 },
            { 'name': 'Studio Mappa', 'weight': 0.16 },
            { 'name': 'Akira Toriyama', 'weight': 0.08 }
        ]
        random_studio_art_style = ' in the style of {}'.format(random.choices([d['name'] for d in studio_art_options], [d['weight'] for d in studio_art_options], k=1)[0])
        
    art_section = '' if random_photo_style else '{}art '.format(random_art_style or '')
    
    if (random_photo_style or random_art_style or random_studio_art_style):
        return 'Generate {photo}{art}of Hatsune Miku{studioart}'.format(photo=random_photo_style or '', art=art_section, studioart=random_studio_art_style or '')

    return 'Generate art of Hatsune Miku' # Fallback