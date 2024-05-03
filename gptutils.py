import keys
from openai import OpenAI

client = OpenAI(
    api_key=keys.CHATGPT
)

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def new_assistant_message(prompt: str):
    return {
        "role": "assistant",
        "content": prompt,
    }
    
###################################
#:::::::::::::::::::::::::::::::::#
###################################

def new_user_message(prompt: str):
    return {
        "role": "user",
        "content": prompt,
    }

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def handle_response(conversation_history: list[dict[str, str]], new_prompt: dict[str, str], gpt_model='gpt-3.5-turbo'):
    conversation_history.append(new_prompt)
    chat_completion = client.chat.completions.create(
        model=gpt_model,
        messages=conversation_history,
    )
    response = chat_completion.choices[0].message.content
    return response if response != None else ''