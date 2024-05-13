import asyncio
from pathlib import Path
from .. import keys
from openai import OpenAI
import os
from io import BytesIO
import logging
from .. import defs
from BingImageCreator import ImageGen

#from . BingImageCreator import ImageGen
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from PIL import Image, ImageDraw, ImageFont
import urllib

client = OpenAI(
    api_key=keys.CHATGPT
)

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def inscribe_text_on_images(props: defs.PostProps, text: str, image_file_list: list[str]):
    for image in image_file_list:
        try:
            img = Image.open(image)
            font_loc = '{}\\postResources\\BrushHandNew.ttf'.format(defs.ROOT_DIR)
            font_size = 32
            font_leading = 8
            x = 30
            y = 30
            extra_y = font_size + font_leading
            I1 = ImageDraw.Draw(img)
            with open(font_loc, 'rb') as font:
                fnt = ImageFont.truetype(font=font, size=font_size, encoding='unic')
                # Render wider black text to give the illusion of a border
                I1.text((x-1, y-1), '{date}  @DailyMikuArt'.format(date=props.date), fill=(0, 0, 0), font=fnt)
                I1.text((x+1, y-1), '{date}  @DailyMikuArt'.format(date=props.date), fill=(0, 0, 0), font=fnt)
                I1.text((x-1, y+1), '{date}  @DailyMikuArt'.format(date=props.date), fill=(0, 0, 0), font=fnt)
                I1.text((x+1, y+1), '{date}  @DailyMikuArt'.format(date=props.date), fill=(0, 0, 0), font=fnt)
                I1.text((x-1, y-1 + extra_y), text, fill=(0, 0, 0), font=fnt)
                I1.text((x+1, y-1 + extra_y), text, fill=(0, 0, 0), font=fnt)
                I1.text((x-1, y+1 + extra_y), text, fill=(0, 0, 0), font=fnt)
                I1.text((x+1, y+1 + extra_y), text, fill=(0, 0, 0), font=fnt)
                # Regular render on top
                I1.text((x, y), '{date}  @DailyMikuArt'.format(date=props.date), fill=(255, 255, 255), font=fnt)
                I1.text((x, y + extra_y), text, fill=(255, 255, 255), font=fnt)
                img.save(image)
                
        except Exception as e:
            logging.error('Failed to inscribe text on "{}" with error: {}'.format(image, e))

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def validate_image(image_file):
    try:
        Image.open(image_file).verify()
        return True
    except Exception:
        image_path = Path(image_file)
        image_path.unlink()
        print('Removing image file at "{}" because it is corrupted.'.format(image_file))
        logging.info('Removing image file at "{}" because it is corrupted.'.format(image_file))
        return False

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def initiate_dalle_layer(props: defs.PostProps, prompt: str, output_image: str):
    '''
    response = client.images.generate(
        prompt='{stop} {prompt}'.format(stop="Do NOT add any additional details other than what is already specified. I do NOT need you want to rewrite ANYTHING." ,prompt=prompt),
        model="dall-e-3",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    logging.info("Revised prompt from OpenAI: {}".format(response.data[0].revised_prompt))
    image_url = response.data[0].url
    logging.info("Successful URL generation: {}".format(image_url))
    download_image(image_url, image_file)
    '''

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def initiate_bing_layer(props: defs.PostProps, prompt: str, output_image: str, image_count: int):
    gen = ImageGen(auth_cookie=keys.BING, auth_cookie_SRCHHPGUSR=keys.BINGSEARCH, debug_file="{}\\miku_output_{}.log".format(props.folderName, props.uuid))
    url_list = gen.get_images(prompt=prompt)
    gen.save_images(links=url_list, output_dir=props.folderName, download_count=image_count, file_name=output_image)

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def initiate_stability_layer(props: defs.PostProps, prompt: str, output_image: str):
    encoded_data = MultipartEncoder(
        fields={
            "prompt": '{}'.format(prompt),
            #"aspect_ratio": "1:1",
            #"negative_prompt": "",
            "seed": '0',
            "style_preset": "anime",
            #"output_format": "png",
        }
    )
    response = requests.post(
        f"https://api.stability.ai/v2beta/stable-image/generate/core",
        headers={
            "authorization": keys.STABILITY,
            "accept": "image/*",
            "content-type": encoded_data.content_type,
        },
        data=encoded_data
    )

    if response.status_code == 200:
        with open(output_image, 'wb') as file:
            file.write(response.content)
            logging.info("Successful Stable Diffusion Core generation.")
    else:
        raise Exception(str(response.json()))
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def download_image(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            logging.info("Image downloaded successfully.")
        else:
            logging.warning("Failed to download image. Status code:", response.status_code)
    except Exception as e:
        logging.error("An error occurred while downloading the image:", str(e))
        
###################################
#:::::::::::::::::::::::::::::::::#
###################################

async def initiate_art_generation(props: defs.PostProps, prompt: str, inscribedText: str):
    image_generation_success = False
    successful_image_links: list[str] = []
    answer = input("Skip art generation? (yes or y)")
    print('PROMPT: {}'.format(prompt))
    if answer == "yes" or answer == 'y':
        logging.info('Art generation has been cancelled by the user.')
        return
    else:
        logging.info('Beginning art generation with prompt - "{}"'.format(prompt))
        try:
            bing_image_count = 3 # Attempt to download 3 images.
            bing_image_file = '{folderNameBase}\\{uuid}_bing_miku_art_{date}_{attempt}'.format(uuid=props.uuid, folderNameBase=props.folderName, date=props.date, attempt=props.attempt)
            initiate_bing_layer(props, prompt, bing_image_file, bing_image_count)
            image_variant_successes: list[bool] = []
            for x in range(0, bing_image_count):
                bing_image_variant = '{fileBase}_{countNum}.jpeg'.format(fileBase=bing_image_file, countNum=x)
                is_valid_image = validate_image(bing_image_variant)
                image_variant_successes.append(is_valid_image)
                if (is_valid_image):
                    successful_image_links.append(bing_image_variant)
            image_generation_success = any(image_variant_successes)
            if not (image_generation_success):
                raise defs.FailedImageGen('Bing failed to produce an uncorrupted image file.')
            else:
                print('Bing art generation success.')
        except Exception as e:
            logging.error(e)
            logging.info('Bing art generation failed - trying again with Stability API')
            try:
                # Stable Diffusion is worse at depicting Miku doing an action, but is more reliable at getting us to a downloaded image of Miku
                stability_image_file = '{folderNameBase}\\{uuid}_stab_miku_art_{date}_{attempt}.png'.format(uuid=props.uuid, folderNameBase=props.folderName, date=props.date, attempt=props.attempt)
                initiate_stability_layer(props, prompt, stability_image_file)
                is_valid_image = validate_image(stability_image_file)
                image_generation_success = is_valid_image
                if (is_valid_image):
                    successful_image_links.append(stability_image_file)
                if not (image_generation_success):
                    raise defs.FailedImageGen('Stability API failed to produce an uncorrupted image file.')
                else:
                    print('Stability API art generation success.')
            except Exception as e:
                logging.error(e)
                logging.warning('Stability API art generation failed - trying one last time with DALL-E api.')
                try:
                    # DALL-E can be dependable, but it will destroy Miku's identity to avoid any copyright implications (Use of Miku's image is allowed under Creative Commons and in this case is being used non-commercially)
                    # Regardless we will most likely get back an image of a generic cyan-colored-hair anime girl. If we're lucky she will have pig tails.
                    dalle_image_file = '{folderNameBase}\\{uuid}_dalle_miku_art_{date}_{attempt}.png'.format(uuid=props.uuid, folderNameBase=props.folderName, date=props.date, attempt=props.attempt)
                    initiate_dalle_layer (props, prompt, dalle_image_file)
                    is_valid_image = validate_image(dalle_image_file)
                    image_generation_success = is_valid_image
                    if (is_valid_image):
                        successful_image_links.append(dalle_image_file)
                    if not (image_generation_success):
                        raise defs.FailedImageGen('DALL-E failed to produce an uncorrupted image file.')
                    else:
                        print('DALL-E art generation success.')
                except Exception as e:
                    logging.error(e)
    if (len(successful_image_links) > 0):
        inscribe_text_on_images(props, inscribedText, successful_image_links)
    return image_generation_success