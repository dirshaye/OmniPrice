from fastapi import APIRouter, Depends, HTTPException, status
from omniprice.core.ratelimit import rate_limit_dependency
from omniprice.schemas.llm import LLMRequest, LLMResponse

from omniprice.services.llm import LLMService

router = APIRouter()


@router.post(
    "/ask",
    response_model=LLMResponse,
    dependencies=[Depends(rate_limit_dependency(namespace="llm_ask", max_requests=6, window_seconds=60))],
)
async def ask_llm(payload: LLMRequest):
    try:
        text = LLMService.ask(
            payload.prompt,
            context=payload.context,
            model_name=payload.model or "gemini-flash-latest",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM provider error. Check model name and API key.",
        )
    return LLMResponse(response=text)
