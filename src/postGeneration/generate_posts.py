import asyncio
from .. import defs
from . import holiday_post, random_post, sports_post, weather_post
from . dalle import initiate_dalle_generation
import logging
from typing import Optional
        
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
            
    if (postData.artPrompt):
        fileOutput = ''
        return await initiate_dalle_generation(props, postData.artPrompt)

    return False