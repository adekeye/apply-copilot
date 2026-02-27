import json
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def structured_completion(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
        fallback_data: dict[str, Any],
    ) -> BaseModel:
        if not self.settings.llm_api_base or not self.settings.llm_api_key:
            return response_model.model_validate(fallback_data)

        schema = response_model.model_json_schema()
        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "schema": schema,
                    "strict": True,
                },
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.settings.llm_api_base.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.llm_api_key}"},
                json=payload,
            )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        try:
            data = json.loads(content)
            return response_model.model_validate(data)
        except (json.JSONDecodeError, ValidationError):
            return response_model.model_validate(fallback_data)


llm_client = LLMClient()
