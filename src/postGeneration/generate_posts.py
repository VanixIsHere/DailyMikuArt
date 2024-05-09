import asyncio
import os
from .. import defs
from . import holiday_post, random_post, sports_post, weather_post
from .art_generation import initiate_art_generation
import logging
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

def get_image_files(date_folder: str):
    image_list: list[str] = []
    if (os.path.isdir(date_folder)):
        files = os.listdir(date_folder)
        for file in files:
            if file.endswith(".jpeg") or file.endswith(".png"):
                image_list.append(file)
    return image_list
        
###################################
#:::::::::::::::::::::::::::::::::#
###################################

async def initiate_post_generation(props: defs.PostProps):
    print('Initiating prompt generation for {}'.format(props.type))
    logging.info('Initiating prompt generation for {postType}.'.format(postType=props.type))
    postData = None
    match props.type:
        case defs.PostType.HOLIDAY:
            postData = holiday_post.generate_post(props.holiday) if props.holiday else None
        case defs.PostType.RANDOM:
            postData = random_post.generate_post()
        case defs.PostType.WEATHER:
            postData = weather_post.generate_post()
        case defs.PostType.SPORTS:
            postData = sports_post.generate_post()
            
    if (postData.artPrompt and postData.inscribedText):
        return await initiate_art_generation(props, postData.artPrompt, postData.inscribedText)

    return False