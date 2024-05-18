import random
from http import HTTPStatus
import dashscope

from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

import json
import requests

dashscope.api_key = 'sk-4eff313deac44c17ac1f2615851a6718'

class QwenLLM(LLM):
    model = ""
    temperature = ""

    @property
    def _llm_type(self) -> str:
        return "qwen-api"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model, "temperature": self.temperature}

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        # if stop is not None:
        #     raise ValueError("stop kwargs are not permitted.")

        messages = []
        messages.append({'role': 'user', 'content': prompt})

        response = dashscope.Generation.call(
            dashscope.Generation.Models.qwen_turbo,
            messages=messages,
            # set the random seed, optional, default to 1234 if not set
            seed=random.randint(1, 10000),
            temperature=0.0,
            result_format='message',  # set the result to be "message" format.
        )

        if response.status_code == HTTPStatus.OK:
            messages.append({'role': 'assistant', 'content': response.output.choices[0].message.content})
            return response.output.choices[0].message
        else:
            return ""