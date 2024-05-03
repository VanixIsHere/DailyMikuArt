from enum import Enum

MajorCountries = ['JP', 'US', 'GB', 'KR']
MinorCountries = ['AU', 'BE', 'BR', 'CA', 'CN', 'DE', 'DK', 'EG', 'ES', 'FR', 'HK', 'IE', 'IN', 'MX', 'NL', 'NO', 'NZ', 'SE', 'SG', 'TH', 'TW', 'UA', 'WS']
AllWeightedCountries = MajorCountries + MinorCountries

PostType = Enum('PostType', ['HOLIDAY', 'RANDOM', 'WEATHER', 'SPORTS'])
DayType = Enum('DayType', ['HOLIDAY', 'BIRTHDAY'])

class TwitterPost:
    def __init__(self, text, images):
        self.text = text
        self.images = images