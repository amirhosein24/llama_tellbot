from groq import Groq
from creds import groq_token as token


client = Groq(api_key=token)


def ask_llama(promt):

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": "helpfull assisstant"
            },
            {
                "role": "user",
                "content": promt
            }

        ],
        temperature=1,
        max_tokens=8192,
        top_p=1,
        stream=True,
        stop=None,
    )

    # for chunk in completion:
    #     print(chunk.choices[0].delta.content or "",
    #           end="")  # TODO learn this

    return completion
