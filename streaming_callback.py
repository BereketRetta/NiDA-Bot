"""CustomCallback Handler streams to stdout on new llm token."""
from typing import Any

from langchain.callbacks.base import BaseCallbackHandler

class CustomStreamingStdOutCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming. Only works with LLMs that support streaming."""

    def __init__(self, message_placeholder):
        super().__init__()
        self.full_response = ""
        self.markdown_container = message_placeholder

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self.full_response += token
        self.markdown_container.markdown(self.full_response)
