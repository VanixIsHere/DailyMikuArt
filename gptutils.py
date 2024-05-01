import keys
from openai import OpenAI

client = OpenAI(
    api_key=keys.CHATGPT
)

def new_assistant_message(prompt: str):
    return {
        "role": "assistant",
        "content": prompt,
    }

def new_user_message(prompt: str):
    return {
        "role": "user",
        "content": prompt,
    }

def handle_response(conversation_history: list[dict[str, str]], new_prompt: dict[str, str], gpt_model='gpt-3.5-turbo'):
    conversation_history.append(new_prompt)
    chat_completion = client.chat.completions.create(
        model=gpt_model,
        messages=conversation_history,
    )
    response = chat_completion.choices[0].message.content
    return response if response != None else ''

def ask_for_prompt(include_words: list[str]):
    system_context = "You are a sentence generating entity."
    gpt_instruction = """The prompt must involve Hatsune Miku as the subject.
    A verb should designate what she is doing, with an optional adverb to modify the verb.
    Miku can do this action on one or multiple nouns.
    These nouns can be singular, plural, or optionally have adjectives applied to them.
    The sentence should be random and almost nonsensical. It does not need to relate to Miku, her music, or technology."""
    messages = [{
        "role": "system",
        "content": system_context,
    }, {
        "role": "assistant",
        "content": gpt_instruction,
    }]
    
    def append_conversation(gpt_response):
        if (gpt_response):
            messages.append(new_assistant_message(gpt_response))
        return gpt_response
    
    response = append_conversation(handle_response(
        messages,
        new_user_message("I would like you to create a single imperative setence beginning with 'Generate art of Hatsune Miku', while also including the word 'homerun' somewhere.")    
    ))
    if (response):
        dalle_tail_end = response.split('Generate art of Hatsune Miku ')[1]
        print(dalle_tail_end)
        
    response = append_conversation(handle_response(
        messages,
        new_user_message("Given the previous sentence you generated. Please generate me a twitter post with no more than 280 characters. The twitter post should be written as Hatsune Miku. Do not mention the whole prompt word for word. Miku should describe what she did and add additional comments about it such as how she feels, who she did it with, where it took place, and what was going on nearby. Keep it cute and friendly. Feel free to make up stuff or exaggerate since this is fictional.")    
    ))
    
    if (response):
        print(response)
        
    return response