import os
from .. import defs
from . import holiday_post, random_post, sports_post, weather_post
from .art_generation import initiate_art_generation
import logging

###################################
#:::::::::::::::::::::::::::::::::#
###################################

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

def write_post_content_to_file(props: defs.PostProps, content: str):
    ## props.folderName
    file_name = '{folder}\\miku_twitter_content_{uuid}.txt'.format(folder=props.folderName, uuid=props.uuid)
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
            logging.info('Successful twitter post write to file at: "{}."'.format(file_name))
            return True
    except Exception as e:
        logging.error(e)
        return False
        
###################################
#:::::::::::::::::::::::::::::::::#
###################################

async def initiate_post_generation(props: defs.PostProps):
    print('Initiating prompt generation for {}'.format(props.type))
    logging.info('Initiating prompt generation for {postType}.'.format(postType=props.type))
    postData = None
    match props.type:
        case defs.PostType.HOLIDAY:
            postData = holiday_post.generate_post(props) if props.holiday else None
        case defs.PostType.RANDOM:
            postData = random_post.generate_post(props)
        case defs.PostType.WEATHER:
            postData = weather_post.generate_post(props)
        case defs.PostType.SPORTS:
            postData = sports_post.generate_post(props)
            
    print(postData)
    if (postData.artPrompt and postData.inscribedText and postData.socialMediaPrompt):
        content_write_success = write_post_content_to_file(props, postData.socialMediaPrompt)
        return await initiate_art_generation(props, postData.artPrompt, postData.inscribedText) and content_write_success

    return False