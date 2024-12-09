from typing import Any, Dict, List

from openai import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from chatgpt_cli.tools.tool_manager import TOOL_FUNCTIONS, TOOLS
from chatgpt_cli.utils.config import settings


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai.api_key.get_secret_value())

    async def list_models(self) -> List[Any]:
        try:
            models = self.client.models.list().data
            models = [model for model in models if "bain" not in model.owned_by]
            filtered_models = [
                model
                for model in models
                if any(substr in model.id for substr in ["4o", "o1"])
            ]
            return filtered_models
        except AuthenticationError as e:
            print(f"Authentication failed: {e}. Check your API key.")
        except APIConnectionError as e:
            print(f"Network error: {e}. Check your internet connection.")
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
        except APIError as e:
            print(f"OpenAI API error: {e}")
        return []

    async def call_openai(self, model_name: str, messages: List[Dict[str, str]]):
        # Include the tools in the request
        if "o1" in model_name:
            response = self.client.chat.completions.create(
                model=model_name, messages=messages
            )
            return response

        response = self.client.chat.completions.create(
            model=model_name, messages=messages, tools=TOOLS, tool_choice="auto"
        )
        return response

    async def deal_with_function_call(
        self, function_name: str, arguments: Dict
    ) -> Dict:
        # Execute the appropriate tool function
        tool_func = TOOL_FUNCTIONS.get(function_name)
        if not tool_func:
            return {"error": "No such tool function."}
        # Call the tool function asynchronously
        result = await tool_func(**arguments)
        return result

    async def get_response(
        self, model_name: str, messages: List[Dict[str, str]]
    ) -> str:
        response = await self.call_openai(model_name, messages)
        if "o1" in model_name:
            return response.choices[0].message.content
        msg = response.choices[0].message

        if response.choices[0].finish_reason == "tool_calls":
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = eval(tool_call.function.arguments)

                tool_response = await self.deal_with_function_call(fn_name, fn_args)
                messages.append({"role": "assistant", "tool_calls": [tool_call]})
                messages.append(
                    {
                        "role": "tool",
                        "content": str(tool_response),
                        "tool_call_id": tool_call.id,
                    }
                )

            response = await self.call_openai(model_name, messages)
            return response.choices[0].message.content
        else:
            return msg.content
