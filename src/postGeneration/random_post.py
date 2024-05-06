from .. import gptutils as gpt
from .. import defs

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def traveling_the_world_prompt(include_words: list[str]):
    ## To properly travel the world, Miku needs a bit of information generated for her to get inspiration for what to do.
    ## She may be provided a country to start in. If provided a country, the proper climate should be realized.
    
    word_topics = ''
    if (len(include_words) == 1):
        word_topics = "'{}'".format(include_words[0])
    if (len(include_words) == 2):
        word_topics = "'{}' and '{}'".format(include_words[0], include_words[1])
    if (len(include_words) > 2):
        quoted_words = list(map(lambda x: "'{}'".format(x), include_words))
        word_topics = '{} and {}'.format(', '.join(quoted_words[:-1]), quoted_words[-1])
    print(word_topics)
    system_context = "You are a text generating entity."
    word_generation_instruction = """You will generate 5 random words to output as a JSON object, with the keys being 'Place', 'Thing', 'Verb', Adjective', and 'Adverb'.
    Each random word should be the same part of speech as it's associated key in JSON object. For example, the key 'Verb' should be a word that is linguistically a verb.
    The key for 'Place' should be one of the following: a man-made location, a service, an attraction, a famous monument, a natural location, or other unique spot. Do not use anything to help generate a location.
    The key for 'Thing' can be any common mundane item with a focus on specificity.
    For the 'Adverb' word, it should be an adverb that modifies the 'Verb' word in a realistic way.
    The 'Adjective' should modify the 'Thing' noun.
    Be creative. Mundane and uncommon words are good. Avoid sexual words.
    """
    if (word_topics):
        word_topics = "The theme of the words can relate to: {}".format(word_topics)

    messages = [{
        "role": "system",
        "content": system_context,
    }, {
        "role": "assistant",
        "content": word_generation_instruction,
    }]
    
    response = gpt.append_conversation(gpt.handle_response(
        messages,
        gpt.new_user_message("""Please generate me a stringified JSON object of random mundane but specific words. {}""".format(word_topics))
    ))
    
    print(response)
    
    response = gpt.append_conversation(gpt.handle_response(
        messages,
        gpt.new_user_message("""Look over the words you generated and evaluate them. Replace 2 of the words and keep the remaining 3.
                         The new words should be less common synonyms. Output another JSON object with the same structure as the last one.
                         Ensure that each value only consists of that part of speech. For example, no adjectives should be applied to a Place or Thing noun.
                         """)
    ))
    
    print(response)
    
    response = gpt.append_conversation(gpt.handle_response(
        messages,
        gpt.new_user_message("""Using the words that you just generated, I want you to write a single imperative sentence from the 3rd person beginning with 'Generate art of Hatsune Miku'.
        The remainder of the sentence should capture the essence of the words that were just generated. The verb should be applied to what Miku is doing.
        Avoid overly violent or sexual themes.
        The adverb will typically modify the verb. Feel free to use the 'Place' and 'Thing' nouns in a creative way. It does not need to relate to Miku, her music, or technology.
        """)
    ))
    
    dalle_prompt = messages[-1]['content']
    messages[-1]['content'] = messages[-1]['content'].replace('Generate art of ', '') # Remove 'Generate art of' so we stop getting art-related twitter posts.
    print(dalle_prompt)

    response = gpt.append_conversation(gpt.handle_response(
        messages,
        gpt.new_user_message("""You are now Hatsune Miku, a 16 year old girl and hugely famous virtual pop idol. Given the previous sentence you just gave me, I want you to generate a twitter post.
                         The twitter post can be no longer than 280 characters. You, as Hatsune Miku, should describe what you did today based on the previous prompt
                         and as if you are addressing your followers. Try to capture the emotion that you felt based on whether the words used are positive or negative.
                         You can make up events that happened to you while doing this.
                         Be descriptive about how you feel.
                         Possibly talk about your music and songs.
                         Do not use too many adverbs. Do not copy the previous sentence word for word.
                         Any twitter hashtags should be related to the post.
                         Include a couple emojis that are relevant.
                         If the location is a vague location, give it a more specific name to make it sound more like a real place in Miku's world.
                         If the location is a real location, keep the real name.
                         The twitter post should end with a japanese sentence.""")    
    ))
    
    print(response)
    
    #if (response):
        # dalle_tail_end = response.split('Generate art of Hatsune Miku ')[1]
        # print(dalle_tail_end)
    '''
    response = append_conversation(handle_response(
        messages,
        new_user_message("Given the previous sentence you generated. Please generate me a twitter post with no more than 280 characters. The twitter post should be written as Hatsune Miku. Do not mention the whole prompt word for word. Miku should describe what she did and add additional comments about it such as how she feels, who she did it with, where it took place, and what was going on nearby. Keep it cute and friendly. Feel free to make up stuff or exaggerate since this is fictional.")    
    ))
    '''
    return response

###################################
#:::::::::::::::::::::::::::::::::#
###################################

def generate_post():
    data = defs.PostData(socialMediaPrompt='', artPrompt='')
    return data