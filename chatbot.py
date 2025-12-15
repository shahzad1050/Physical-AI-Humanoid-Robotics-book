import os
import openai

class ChatBot:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat(self, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
