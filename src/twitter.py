from TwitterAPI import TwitterAPI, OAuthType
from . import keys
import base64
import requests

api = TwitterAPI(
    consumer_key=keys.CONSUMERAPI,
    consumer_secret=keys.CONSUMERSECRET,
    access_token_key=keys.TWITTERACCESS,
    access_token_secret=keys.TWITTERSECRET,
    auth_type=OAuthType.OAUTH1,
    api_version="2"
)

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def prepare_twitter_post(date: str):
    # POST /2/tweets
    
    '''
    auth = "tweet.write"
    url = "statuses/update"
    encoded_keys = base64.b64encode("{access}:{secret}".format(access=keys.TWITTERACCESS, secret=keys.TWITTERSECRET).encode('utf-8'))
    auth_url_endpoint = "https://api.twitter.com/oauth2/token"
    print(encoded_keys)
    
    api.request()
    '''
    
    '''
    response = requests.post(
        auth_url_endpoint,
        headers={
            "authorization": encoded_keys,
            ## "accept": "image/*",
            ##"content-type": encoded_data.content_type,
        }
    )
    '''
    
    print(response)

###################################
#:::::::::::::::::::::::::::::::::#
###################################