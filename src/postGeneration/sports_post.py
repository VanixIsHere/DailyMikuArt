from ..gptutils import handle_response, new_user_message, new_assistant_message
from .. import defs

def generate_post(props: defs.PostProps):
    data = defs.PostData(socialMediaPrompt='', artPrompt='')
    return data