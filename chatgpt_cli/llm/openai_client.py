import json
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
    def __init__(self, stream: bool = False):
        self.stream = stream
        self.client = OpenAI(api_key=settings.openai.api_key.get_secret_value())

    async def list_models(self) -> List[Any]:
        try:
            models = self.client.models.list().data
            filtered_models = [
                model for model in models if model.owned_by in ["system", "openai"]
            ]
            filtered_models = [
                model
                for model in filtered_models
                if "o1" in model.id or "gpt-4" in model.id
            ]
            filtered_models = sorted(filtered_models, key=lambda x: x.id)
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

    async def call_openai(
        self, model_name: str, messages: List[Dict[str, str]], **kwargs
    ):
        response = self.client.chat.completions.create(
            model=model_name, messages=messages, **kwargs
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
        if self.stream:
            return await self.process_stream(model_name, messages)
        return await self.get_complete_response(model_name, messages)

    async def get_complete_response(
        self, model_name: str, messages: List[Dict[str, str]]
    ) -> str:
        if "o1" in model_name:
            response = await self.call_openai(model_name, messages)
            return response.choices[0].message.content
        response = await self.call_openai(
            model_name, messages, tools=TOOLS, tool_choice="auto", stream=False
        )
        msg = response.choices[0].message
        response_text = msg.content
        if response.choices[0].finish_reason == "tool_calls":
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

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
            response_text = response.choices[0].message.content

        print(f"Assistant: {response_text}", end="\n\n", flush=True)
        return response_text

    async def process_stream(self, model_name: str, messages: List[Dict[str, str]]):
        response_text = ""
        tool_calls = []
        stream_response = await self.call_openai(
            model_name, messages, tools=TOOLS, tool_choice="auto", stream=True
        )
        print("Assistant: ", end="", flush=True)
        for chunk in stream_response:
            delta = chunk.choices[0].delta

            if delta and delta.content:
                print(delta.content, end="", flush=True)
                response_text += delta.content

            elif delta and delta.tool_calls:
                tcchunklist = delta.tool_calls
                for tcchunk in tcchunklist:
                    if len(tool_calls) <= tcchunk.index:
                        tool_calls.append(
                            {
                                "id": "",
                                "type": "function",
                                "function": {"name": "", "arguments": ""},
                            }
                        )
                    tc = tool_calls[tcchunk.index]

                    if tcchunk.id:
                        tc["id"] += tcchunk.id
                    if tcchunk.function.name:
                        tc["function"]["name"] += tcchunk.function.name
                    if tcchunk.function.arguments:
                        tc["function"]["arguments"] += tcchunk.function.arguments

        if tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "tool_calls": tool_calls,
                }
            )

            for tool_call in tool_calls:
                fn_name = tool_call["function"]["name"]
                fn_args = json.loads(tool_call["function"]["arguments"])
                tool_response = await self.deal_with_function_call(fn_name, fn_args)
                
                messages.append(
                    {
                        "role": "tool",
                        "content": str(tool_response),
                        "tool_call_id": tool_call["id"],
                    }
                )

            stream = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                stream=True,
            )
            response_text = ""
            for chunk in stream:
                stream_txt = chunk.choices[0].delta.content
                if stream_txt is not None:
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    response_text += stream_txt
        print("\n")
        return response_text
