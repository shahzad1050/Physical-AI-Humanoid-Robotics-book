import os
import openai

class ChatBot:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            print("OPENAI_API_KEY not set - ChatBot initialized in offline mode")
            self.api_available = False
            return

        try:
            self.client = openai.OpenAI(api_key=openai_api_key)
            self.api_available = True
        except Exception as e:
            print(f"Warning: Could not initialize OpenAI client: {e}")
            print("ChatBot initialized in offline mode - chat will return mock responses")
            self.api_available = False

    def chat(self, user_prompt: str) -> str:
        if not self.api_available:
            # Return a more meaningful mock response for testing purposes
            # Extract keywords from the user prompt to make the response more relevant
            import re
            # Simple keyword extraction - take the last few words as topic
            words = user_prompt.split()
            topic = " ".join(words[-3:]) if len(words) >= 3 else user_prompt

            mock_responses = {
                "hello": "Hello! I'm your Physical AI & Humanoid Robotics assistant. How can I help you today?",
                "hi": "Hi there! I'm here to answer questions about Physical AI and Humanoid Robotics. What would you like to know?",
                "help": "I'm here to help you with information about Physical AI and Humanoid Robotics. You can ask me questions about the documentation.",
                "default": f"Thank you for your question about '{topic}'. In a live environment, I would provide a detailed response based on the documentation. This is a test response showing that the system is working properly."
            }

            # Check for common greetings or help requests
            user_lower = user_prompt.lower()
            if "hello" in user_lower or "hi " in user_lower or "hey" in user_lower:
                return mock_responses["hello"]
            elif "help" in user_lower:
                return mock_responses["help"]
            elif len(user_prompt.strip()) < 2:
                return mock_responses["hi"]
            else:
                return mock_responses["default"]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return f"Error generating response: {str(e)}"
