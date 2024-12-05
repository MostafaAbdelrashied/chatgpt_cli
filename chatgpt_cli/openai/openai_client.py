from typing import Dict, List

import openai

from chatgpt_cli.utils.config import settings


class OpenAIClient:
    def __init__(self, stream: bool, api_key: str = None):
        self.stream = stream
        openai.api_key = api_key or settings.OPENAI_API_KEY

    async def list_models(self) -> List[str]:
        try:
            models = openai.OpenAI().models.list().data
            models = [model for model in models if "bain" not in model.owned_by]
            if self.stream:
                models = [
                    model
                    for model in models
                    if any(substr not in model.id for substr in ["o1"])
                ]
            filtered_models = [
                model
                for model in models
                if any(substr in model.id for substr in ["4o", "o1"])
            ]
            return filtered_models
        except openai.AuthenticationError as e:
            print(f"Authentication failed: {e}. Check your API key.")
        except openai.APIConnectionError as e:
            print(f"Network error: {e}. Check your internet connection.")
        except openai.RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
        except openai.APIError as e:
            print(f"OpenAI API error: {e}")
        return []

    async def get_response_complete(
        self, model_name: str, messages: List[Dict[str, str]]
    ) -> str:
        try:
            response = openai.chat.completions.create(
                model=model_name, messages=messages
            )
            response_text = response.choices[0].message.content
            print(response_text, end="", flush=True)
            print("\n")
            return response_text
        except openai.OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return ""

    async def get_response_stream(
        self, model_name: str, messages: List[Dict[str, str]]
    ) -> str:
        try:
            response = openai.chat.completions.create(
                model=model_name, messages=messages, stream=True
            )
            model_reply = ""

            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                model_reply += content
            print("\n")
            return model_reply
        except openai.OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return []

    async def get_response(
        self, model_name: str, messages: List[Dict[str, str]]
    ) -> str:
        if self.stream:
            return await self.get_response_stream(model_name, messages)
        return await self.get_response_complete(model_name, messages)
