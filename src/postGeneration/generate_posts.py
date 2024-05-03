from .. import defs
from . import holiday_post, random_post, sports_post, weather_post
from .holiday_post import HolidayType
from typing import Optional

###################################
#:::::::::::::::::::::::::::::::::#
###################################

class PostProps:
    def __init__(self, type: defs.PostType, holiday: Optional[HolidayType]):
        self.type = type
        self.holiday = holiday
        
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def initiate_post_generation(props: PostProps):
    print('Initiating prompt generation for {}'.format(props.type))
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
    return postData