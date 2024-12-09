import json
from typing import Any, Dict, List

from openai import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)

from chatgpt_cli.tools.tool_manager import TOOL_FUNCTIONS, TOOLS
from chatgpt_cli.utils.config import settings


class OpenAIClient:
    def __init__(self, stream: bool = False):
        self.stream = stream
        self.client = OpenAI(api_key=settings.openai.api_key.get_secret_value())

    async def list_models(self) -> List[Dict[str, Any]]:
        """Fetch and filter available models."""
        try:
            models = self.client.models.list().data
            return sorted(
                [
                    model
                    for model in models
                    if model.owned_by in ["system", "openai"]
                    and ("o1" in model.id or "gpt-4" in model.id)
                ],
                key=lambda x: x.id,
            )
        except (AuthenticationError, APIConnectionError, RateLimitError, APIError) as e:
            self._log_error("Failed to list models", e)
            return []

    def call_openai(
        self, model_name: str, messages: List[Dict[str, str]], **kwargs
    ) -> Any:
        """Send a chat completion request to OpenAI."""
        if "o1" in model_name:
            kwargs = {k: v for k, v in kwargs.items() if "tool" not in k}
        return self.client.chat.completions.create(
            model=model_name, messages=messages, **kwargs
        )

    async def acall_openai(
        self, model_name: str, messages: List[Dict[str, str]], **kwargs
    ) -> Any:
        """Send a chat completion request to OpenAI."""
        return self.call_openai(model_name, messages, **kwargs)

    async def deal_with_function_call(
        self, function_name: str, arguments: Dict
    ) -> Dict:
        """Handle a tool function call."""
        tool_func = TOOL_FUNCTIONS.get(function_name)
        if not tool_func:
            return {"error": "No such tool function."}
        return await tool_func(**arguments)

    async def get_response(
        self, model_name: str, messages: List[Dict[str, str]]
    ) -> str:
        """Get a response from OpenAI, handling streaming if enabled."""
        return (
            await self.process_stream(model_name, messages)
            if self.stream
            else await self.get_complete_response(model_name, messages)
        )

    async def get_complete_response(
        self, model_name: str, messages: List[Dict[str, str]]
    ) -> str:
        """Handle non-streaming responses."""
        response = await self.acall_openai(
            model_name, messages, tools=TOOLS, tool_choice="auto", stream=False
        )
        response_text = await self._handle_response(response, model_name, messages)
        print(f"Assistant: {response_text}", flush=True, end="\n\n")
        return response_text

    async def process_stream(
        self, model_name: str, messages: List[Dict[str, str]]
    ) -> str:
        """Handle streaming responses."""
        stream_response = await self.acall_openai(
            model_name, messages, tools=TOOLS, tool_choice="auto", stream=True
        )
        response_text, tool_calls = "", []
        print("Assistant: ", end="", flush=True)

        for chunk in stream_response:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
                response_text += delta.content
            if delta.tool_calls:
                self._accumulate_tool_calls(tool_calls, delta.tool_calls)

        if tool_calls:
            await self._process_tool_calls(tool_calls, messages)
            response_stream = self.call_openai(
                model_name,
                messages,
                stream=True,
            )
            response_text = ""
            for chunk in response_stream:
                chunk_text = chunk.choices[0].delta.content
                if chunk_text is not None:
                    response_text += chunk_text
                    print(chunk_text, end="", flush=True)

        print("\n", flush=True)
        return response_text

    async def _handle_response(
        self, response: Any, model_name: str, messages: List[Dict[str, str]]
    ) -> str:
        """Process the initial response and handle tool calls if needed."""
        message = response.choices[0].message
        if response.choices[0].finish_reason == "tool_calls":
            await self._process_tool_calls(message.tool_calls, messages)
            response = await self.acall_openai(model_name, messages)
            return response.choices[0].message.content
        return message.content

    async def _process_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        messages: List[Dict[str, str]],
    ) -> str:
        """Execute tool calls and continue processing."""
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            tool_response = await self.deal_with_function_call(function_name, arguments)
            messages.extend(
                [
                    {"role": "assistant", "tool_calls": [tool_call]},
                    {
                        "role": "tool",
                        "content": str(tool_response),
                        "tool_call_id": tool_call.id,
                    },
                ]
            )

    def _accumulate_tool_calls(
        self,
        tool_calls: List[ChatCompletionMessageToolCall],
        delta_tool_calls: List[ChatCompletionMessageToolCall],
    ):
        """Accumulate tool call chunks during streaming."""
        for tcchunk in delta_tool_calls:
            if len(tool_calls) <= tcchunk.index:
                tool_calls.append(
                    ChatCompletionMessageToolCall(
                        id="", function=Function(name="", arguments=""), type="function"
                    )
                )
            tool_call = tool_calls[tcchunk.index]
            if tcchunk.id:
                tool_call.id += tcchunk.id
            if tcchunk.function.name:
                tool_call.function.name += tcchunk.function.name
            if tcchunk.function.arguments:
                tool_call.function.arguments += tcchunk.function.arguments

    @staticmethod
    def _log_error(message: str, error: Exception):
        """Log errors in a standardized format."""
        print(f"{message}: {error}")
