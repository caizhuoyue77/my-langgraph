from __future__ import annotations

## 单独运行的时候需要添加
import sys
import os

from configs import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import warnings
from typing import Dict

from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.pydantic_v1 import Extra, root_validator
from langchain.schema import BasePromptTemplate
from langchain.schema.language_model import BaseLanguageModel
import requests
from typing import List, Any, Optional
from datetime import datetime
from langchain.prompts import PromptTemplate
from server.agent import model_container
from pydantic import BaseModel, Field

## 使用和风天气API查询天气
KEY = "ac880e5a877042809ac7ffdd19d95b0d"
# key长这样，这里提供了示例的key，这个key没法使用，你需要自己去注册和风天气的账号，然后在这里填入你的key


_PROMPT_TEMPLATE = """
用户会提出一个关于圩区水位的问题，你的目标是拆分出用户问题中的圩区名称 并按照我提供的工具回答。
例如 用户提出的问题是: 白洋村一圩区的水位是多少？
则 提取的圩区名称是: 白洋村一圩区
如果用户提出的问题是: 白洋村一圩区的水位现在怎么样？
则 提取的圩区名称是: 白洋村一圩区

问题: ${{用户的问题}}

你的回答格式应该按照下面的内容，请注意，格式内的```text 等标记都必须输出，这是我用来提取答案的标记。
```text

${{提取的圩区名称}}
```
... waterlevelcheck(提取的圩区名称)...
```output

${{提取后的答案}}
```
答案: ${{答案}}



这是一个例子：
问题: 白洋村一圩区的水位现在怎么样？


```text
白洋村一圩区
```
...waterlevelcheck(白洋村一圩区)...

```output
白洋村一圩区的水位现在是 3.26 米

Answer: 白洋村一圩区的水位现在是 3.26 米。

现在，这是我的问题：

问题: {question}
"""
PROMPT = PromptTemplate(
    input_variables=["question"],
    template=_PROMPT_TEMPLATE,
)


def waterlevel(query):
    try:
        def get_water():
            url = "http://117.149.146.22:8800/jiaxing-wd-api/function/polder/current"
            response = requests.get(url)
            data = response.json()
            return data

        water_data = get_water()
        location = query
        for polder in water_data['data']:
            if polder['polderName'] == location:
                water_level = polder['deviceWaterBaseList'][0]['sw']

                # logger.info(f"{location}目前水位是{water_level}米" + "以上是查询到的水位信息，请你查收\n")
                return f"{location}目前水位是{water_level}米。" + "以上是查询到的水位信息，请你查收\n"

    except KeyError:
        return "输入的圩区不存在，无法提供水位预报"


class LLMWaterLevelModel(Chain):
    llm_chain: LLMChain
    llm: Optional[BaseLanguageModel] = None
    """[Deprecated] LLM wrapper to use."""
    prompt: BasePromptTemplate = PROMPT
    """[Deprecated] Prompt to use to translate to python if necessary."""
    input_key: str = "question"  #: :meta private:
    output_key: str = "answer"  #: :meta private:

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def raise_deprecation(cls, values: Dict) -> Dict:
        if "llm" in values:
            warnings.warn(
                "Directly instantiating an LLMWeatherChain with an llm is deprecated. "
                "Please instantiate with llm_chain argument or using the from_llm "
                "class method."
            )
            if "llm_chain" not in values and values["llm"] is not None:
                prompt = values.get("prompt", PROMPT)
                values["llm_chain"] = LLMChain(llm=values["llm"], prompt=prompt)
        return values

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Expect output key.

        :meta private:
        """
        return [self.output_key]

    def _evaluate_expression(self, expression: str) -> str:
        try:
            #先去除空格和换行符
            expression = expression.replace(" ", "")
            expression = expression.replace("\n", "")
            output = waterlevel(expression)
        except Exception as e:
            output = "输入的信息有误，请再次尝试"
        return output

    def _process_llm_result(
            self, llm_output: str, run_manager: CallbackManagerForChainRun
    ) -> Dict[str, str]:

        run_manager.on_text(llm_output, color="green", verbose=self.verbose)

        llm_output = llm_output.strip()
        text_match = re.search(r"^```text(.*?)```", llm_output, re.DOTALL)
        # logging.info(text_match)
        if text_match:
            expression = text_match.group(1)
            output = self._evaluate_expression(expression)
            run_manager.on_text("\nAnswer: ", verbose=self.verbose)
            run_manager.on_text(output, color="yellow", verbose=self.verbose)
            answer = "Answer: " + output
        elif llm_output.startswith("Answer:"):
            answer = llm_output
        elif "Answer:" in llm_output:
            answer = "Answer: " + llm_output.split("Answer:")[-1]
        else:
            return {self.output_key: f"输入的格式不对: {llm_output},应该输入圩区名称。例如：白洋村一圩区"}
        return {self.output_key: answer}

    async def _aprocess_llm_result(
            self,
            llm_output: str,
            run_manager: AsyncCallbackManagerForChainRun,
    ) -> Dict[str, str]:
        await run_manager.on_text(llm_output, color="green", verbose=self.verbose)
        llm_output = llm_output.strip()
        text_match = re.search(r"^```text(.*?)```", llm_output, re.DOTALL)

        if text_match:
            expression = text_match.group(1)
            output = self._evaluate_expression(expression)
            await run_manager.on_text("\nAnswer: ", verbose=self.verbose)
            await run_manager.on_text(output, color="yellow", verbose=self.verbose)
            answer = "Answer: " + output
        elif llm_output.startswith("Answer:"):
            answer = llm_output
        elif "Answer:" in llm_output:
            answer = "Answer: " + llm_output.split("Answer:")[-1]
        else:
            raise ValueError(f"unknown format from LLM: {llm_output}")
        return {self.output_key: answer}

    def _call(
            self,
            inputs: Dict[str, str],
            run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        _run_manager.on_text(inputs[self.input_key])
        llm_output = self.llm_chain.predict(
            question=inputs[self.input_key],
            stop=["```output"],
            callbacks=_run_manager.get_child(),
        )
        return self._process_llm_result(llm_output, _run_manager)

    async def _acall(
            self,
            inputs: Dict[str, str],
            run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or AsyncCallbackManagerForChainRun.get_noop_manager()
        await _run_manager.on_text(inputs[self.input_key])
        llm_output = await self.llm_chain.apredict(
            question=inputs[self.input_key],
            stop=["```output"],
            callbacks=_run_manager.get_child(),
        )
        return await self._aprocess_llm_result(llm_output, _run_manager)

    @property
    def _chain_type(self) -> str:
        return "llm_weather_chain"

    @classmethod
    def from_llm(
            cls,
            llm: BaseLanguageModel,
            prompt: BasePromptTemplate = PROMPT,
            **kwargs: Any,
    ) -> LLMWaterLevelModel:
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        return cls(llm_chain=llm_chain, **kwargs)


def waterlevelcheck(query: str):
    logger.info(f"用户输入的问题是: {query}")
    model = model_container.MODEL
    llm_waterlevel = LLMWaterLevelModel.from_llm(model, verbose=True, prompt=PROMPT)
    ans = llm_waterlevel.run(query)
    return ans


class WaterLevelSchema(BaseModel):
    polderName: str = Field(description="应该是一个圩区的名称，例如：白洋村一圩区")


if __name__ == '__main__':
    result = waterlevelcheck("白洋村一圩区的水位是多少？")
