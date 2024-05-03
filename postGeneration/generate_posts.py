from . import defs
import holiday_post
import random_post
import sports_post
import weather_post

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def initiate_post_generation(type: defs.PostType):
    print('Initiating prompt generation for {}'.format(type))
    match type:
        case defs.PostType.HOLIDAY:
            postData = holiday_post.generate_post()
        case defs.PostType.RANDOM:
            postData = random_post.generate_post()
        case defs.PostType.WEATHER:
            postData = weather_post.generate_post()
        case defs.PostType.SPORTS:
            postData = sports_post.generate_post()
        case _:
            postData = None
    return postData