
from groq import Groq
from creds import groq_token as groq_api


def groq_token():
    if not hasattr(groq_token, 'index'):
        groq_token.index = 0
    item = groq_api[groq_token.index]
    groq_token.index = (groq_token.index + 1) % len(groq_api)
    return item


def ask_llama(prompt, model="llama3-8b-8192"):
    client = Groq(api_key=groq_token())

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "you are a helpfull assisstant, answer prompts in same language as prompt"
            },
            {
                "role": "user",
                "content": prompt
            }

        ],
        temperature=1,
        max_tokens=4096,
        top_p=1,
        stream=True,
        stop=None,
    )
    return completion


def ask_llama_reply(prompt, reply, model="llama3-8b-8192"):
    client = Groq(api_key=groq_token())

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "you are a helpfull assisstant, answer prompts in same language as prompt"
            },
            {
                "role": "assistant",
                "content": reply
            },
            {
                "role": "user",
                "content": prompt
            }

        ],
        temperature=1,
        max_tokens=4096,
        top_p=1,
        stream=True,
        stop=None,
    )
    return completion
