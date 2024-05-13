from enum import Enum
from pathlib import Path
from typing import Dict, Optional, TypedDict

ROOT_DIR = Path(__file__).parent
history_folder = '{root}\\history'.format(root=ROOT_DIR)
archive_folder = '{root}\\archive'.format(root=ROOT_DIR)

MajorCountries = ['JP', 'US', 'GB', 'KR']
MinorCountries = ['AU', 'BE', 'BR', 'CA', 'CN', 'DE', 'DK', 'EG', 'ES', 'FR', 'HK', 'IE', 'IN', 'MX', 'NL', 'NO', 'NZ', 'SE', 'SG', 'TH', 'TW', 'UA', 'WS']
AllWeightedCountries = MajorCountries + MinorCountries

PostType = Enum('PostType', ['HOLIDAY', 'RANDOM', 'WEATHER', 'SPORTS'])
DayType = Enum('DayType', ['HOLIDAY', 'BIRTHDAY'])

Vibe = Enum('Vibe', ['Epic'])
Framing = Enum('Framing', ['close-up'])

Style = Enum('Enum', ['StudioArt', 'Photo', 'Art'])

HolidayDictionary = Dict[str, list[str]]
HolidayType = tuple[str, list[str], DayType]

class TwitterPost:
    def __init__(self, text, images):
        self.text = text
        self.images = images
        
class WeightedOption(TypedDict):
    name: str
    weight: int
    
class PostProps:
    def __init__(self, uuid: str, type: PostType, date: str, folderName: str, attempt: int, holiday: Optional[HolidayType]):
        self.uuid = uuid
        self.type = type
        self.date = date
        self.folderName = folderName
        self.attempt = attempt
        self.holiday = holiday
        
class PostData:
    def __init__(self, socialMediaPrompt, artPrompt, inscribedText = ''):
        self.socialMediaPrompt: str = socialMediaPrompt
        self.artPrompt: str = artPrompt
        self.inscribedText: str = inscribedText
        
class FailedImageGen(Exception):
    pass