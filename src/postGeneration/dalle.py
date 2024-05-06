import asyncio
from .. import keys
from openai import OpenAI
import os
import logging
from .. import defs
from urllib.request import urlopen
from BingImageCreator import ImageGenAsync

client = OpenAI(
    api_key=keys.CHATGPT
)

async def initiate_dalle_generation(props: defs.PostProps, prompt: str):
    answer = input("Skip DALL-E generation? (yes or y)")
    if answer == "yes" or answer == 'y':
        logging.info('DALL-E generation has been cancelled by the user.')
        return
    else:
        print('CALLING DALLE with {}'.format(props.folderName))
        
        image_file = '{folderNameBase}\\miku_art_{date}_{attempt}'.format(folderNameBase=props.folderName, date=props.date, attempt=props.attempt)
        try:
            gen = ImageGenAsync(auth_cookie=keys.BING)
            url_list = await gen.get_images(prompt=prompt)
            await gen.save_images(links=url_list, output_dir=props.folderName, download_count=1, file_name=image_file)
            return True

        except Exception as e:
            # print(e)
            logging.error(e)
    return False