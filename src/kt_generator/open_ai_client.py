import os
from enum import Enum
from loguru import logger
import openai

PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
assert PORTKEY_API_KEY, "PORTKEY_API_KEY is not set!"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "OPENAI_API_KEY is not set!"


CLASS_EXPLAINATION_PROMPT = """
Please generate a script that a text-to-speach engine will use to generate the audio file. Following is 
most of the code you need to keep in mind to generate the script:

<code>
{context_code}
</code>

<context>
This class is part of the larger codebase that provides interative agents that assists humans in documenting software requirements.
</context>

Please generate script in the following format that provides a nontechnical explanation for the class `{class_name}`.

```
    A high level narrative of what this class does and when to use it.
    Any enums or static variables declared in the class and what they mean, in one line each max.
    One line introduction of the larger public methods like kick_off, handle_user_response, and generate_story only.
```

Rules:
1. Provide only the script to be read by text to speech engine in the output; NO greetings/acknowledgement/etc.
2. Be professional, don't use too many analogies
3. Script should be concise and should not have repeatation of ideas. Anything explained before in the history, should not be mentioned again.
4. Ignore any exception handling, error management & validations related details
5. Replace underscores with spaces
"""

METHOD_EXPLAINATION_PROMPT = """
Please generate a script that a text-to-speach engine will use to generate the audio file. Following is 
most of the code you need to keep in mind to generate the script:

<code>
{context_code}
</code>

<context>
This method is part of the larger codebase that provides interative agents that assists humans in documenting software requirements.
</context>

Please generate script in the following format that provides a nontechnical explanation for the method `{method_name}`.

```
    2-3 line summary of what this method does and when to use it
    Brief summary of primary building blocks used in the method; mention both public knowledge ones 
        like OpenAI, Slack, Databases, etc. and ones that are specific to the codebase. Provide one line
        explanation of the codebase specific building blocks only.
    Provide a high level narrative of how these building blocks come together 
        to achieve the purpose of the method. Ensure you are NOT describing code line by line, it gets boring.
    Highlight any special handling typically coded with if/else, switch cases, etc.
    End the script with a one line takeaway for the listener.
```

Rules:
1. Provide only the script to be read by text to speech engine in the output; NO greetings/acknowledgement/etc.
2. Be professional, don't use too many analogies
3. Script should be concise and should not have repeatation of ideas. Anything explained before in the history, should not be mentioned again.
4. Ignore any exception handling, error management & validations related details
5. Replace underscores with spaces
"""


class OpenAIClient:
    def __init__(self, provided_history=None):
        self.history = provided_history
        if self.history is None or len(self.history) == 0:
            self.history = []
            logger.info("No history provided. Setting up system...")
            self.setup_system()

    def setup_system(self):
        self.history.append(
            {
                "role": "system",
                "content": f"""
                You are an experienced Python developer who is asked to write a script that will be used by 
                a text to speech engine to generate an audio file. You are good at explaining code to 
                non-technical people using language they will understand; but have to also follow good practices
                for writing scripts for text to speech engines.

                1. Use Simple Sentences: Complex sentences may not be processed as naturally as simpler ones.
                2. Punctuation: Proper use of punctuation can significantly affect the TTS engine's prosody (rhythm, stress, and intonation of speech).
                3. Modularize: Break down complex ideas into shorter sentences or phrases. This makes it easier for the TTS engine to process and for the audience to understand.
                4. Use Standard Abbreviations: Some TTS engines struggle with non-standard abbreviations or may not interpret them as you intend. Stick with standard forms whenever possible.
                5. Normalize Numbers and Dates: Some TTS engines may read "2023" as "two zero two three" instead of "two thousand twenty-three". Specify how you want numbers and dates to be read.
                6. Don't use underscrores in the script. Replace them with spaces.
                """,
            }
        )

    def create_chat(
        self, message, temperature=0.8, presence_penalty=0, frequency_penalty=0
    ):
        self.history.append({"role": "user", "content": message})
        openai.api_base = "https://api.portkey.ai/v1/proxy"
        response = openai.ChatCompletion.create(
            model=os.environ.get("OPENAI_MODEL_ID"),
            messages=self.history,
            temperature=temperature,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            headers={
                "x-portkey-api-key": PORTKEY_API_KEY,
                "x-portkey-mode": "proxy openai",
                "x-portkey-retry-count": "4",
                "x-portkey-cache": "simple",
            },
        )

        response_content = response.choices[0].message["content"].strip()
        self.history.append({"role": "assistant", "content": response_content})

        return response_content.replace("```\n", "```\n##### ")

    def get_history(self):
        return self.history

    def reset_history(self):
        self.history = []
        self.setup_system()
