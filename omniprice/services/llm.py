from __future__ import annotations

from typing import Optional

import google.generativeai as genai

from omniprice.core.config import settings


class LLMService:
    @staticmethod
    def _ensure_client_ready() -> None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=settings.GEMINI_API_KEY)

    @staticmethod
    def _build_prompt(prompt: str, context: Optional[str] = None) -> str:
        if context:
            return (
                "You are a pricing intelligence assistant. Use the context to answer.\n\n"
                f"Context:\n{context}\n\n"
                f"User question:\n{prompt}\n"
            )
        return (
            "You are a pricing intelligence assistant.\n\n"
            f"User question:\n{prompt}\n"
        )

    @staticmethod
    def ask(prompt: str, context: Optional[str] = None, *, model_name: str = "gemini-flash-latest") -> str:
        LLMService._ensure_client_ready()
        model = genai.GenerativeModel(model_name)
        full_prompt = LLMService._build_prompt(prompt, context)
        response = model.generate_content(full_prompt)
        return response.text or ""
