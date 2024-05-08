import asyncio
from .. import keys
from openai import OpenAI
import os
from io import BytesIO
import logging
from .. import defs
from BingImageCreator import ImageGenAsync
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from PIL import Image
import urllib

client = OpenAI(
    api_key=keys.CHATGPT
)

def initiate_stability_layer(props: defs.PostProps, prompt: str, dalle_image: str, output_image: str, output_image_two: str):
    ## base_image = Image.open(dalle_image)
    ## with open(dalle_image, 'rb') as input_file:
        '''
        multipart_data = MultipartEncoder(
            fields={
                "text_prompts[0][text]": prompt,
                "text_prompts[0][weight]": 0.5,
                "init_image": (dalle_image, input_file, 'image/png'),
                #"init_image_mode"
                #"image_strength"
                "cfg_scale": 20,
                #"clip_guidance_preset"
                #"sampler"
                "samples": 1,
                "seed": 0,
                #"steps"
                #"style_preset"
            }
        )
        '''
        '''
        engine_id = "stable-diffusion-v1-6"
        encoded_data = MultipartEncoder(
            fields={
                "init_image": (dalle_image, open(dalle_image, 'rb')),
                "text_prompts[0][text]": prompt,
                "text_prompts[0][weight]": '0.01',
                "text_prompts[1][text]": 'Girl in center is Hatsune Miku, Vocaloid, two long pigtails',
                "text_prompts[1][weight]": '0.99',
                #"init_image_mode"
                "image_strength": '0.42',
                "cfg_scale": '14',
                #"clip_guidance_preset"
                #"sampler"
                "samples": '1',
                "seed": '0',
                #"steps"
                "style_preset": "anime",
            }
        )
        response = requests.post(
            f"https://api.stability.ai/v1/generation/{engine_id}/image-to-image",
            headers={
                "authorization": keys.STABILITY,
                "accept": "image/png",
                "content-type": encoded_data.content_type,
            },
            data=encoded_data
        )
        '''
        
        prompt = "Generate art of Hatsune Miku where she is at a lively Halloween street festival, amidst a kaleidoscope of costumes and decorations. Miku stands out in her usual cybernetic vocaloid attire, now infused with Gothic elements, adorned with intricate lace and dark velvet accents. Surrounding her are people of various descents, all embracing the spirit of the holiday with their imaginative outfits. The scene is illuminated by flickering jack-o'-lanterns and colorful string lights, casting eerie shadows on the cobblestone streets. Laughter and spooky music fill the air as candy is exchanged and games are played. Style: Anime with a spooky, neon-lit aesthetic."
        
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
            with open(output_image_two, 'wb') as file:
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

async def initiate_dalle_generation(props: defs.PostProps, prompt: str):
    answer = input("Skip DALL-E generation? (yes or y)")
    print('PROMPT: {}'.format(prompt))
    if answer == "yes" or answer == 'y':
        logging.info('DALL-E generation has been cancelled by the user.')
        return
    else:
        print('CALLING DALLE with {}'.format(props.folderName))
        
        image_file = '{folderNameBase}\\miku_art_{date}_{attempt}.png'.format(folderNameBase=props.folderName, date=props.date, attempt=props.attempt)
        try:
            '''
            gen = ImageGenAsync(auth_cookie=keys.BING)
            url_list = await gen.get_images(prompt=prompt)
            await gen.save_images(links=url_list, output_dir=props.folderName, download_count=1, file_name=image_file)
            '''
            
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
            stability_image_file = '{folderNameBase}\\stab_miku_art_{date}_{attempt}.png'.format(folderNameBase=props.folderName, date=props.date, attempt=props.attempt)
            stability_image_file_two = '{folderNameBase}\\stab_core_miku_art_{date}_{attempt}.png'.format(folderNameBase=props.folderName, date=props.date, attempt=props.attempt)
            # initiate_stability_layer(props, prompt, image_file, stability_image_file, stability_image_file_two)
            
            return True

        except Exception as e:
            # print(e)
            logging.error(e)
    return False