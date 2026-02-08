from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    prompt: str = Field(min_length=3)
    context: str | None = None
    model: str | None = None


class LLMResponse(BaseModel):
    response: str
