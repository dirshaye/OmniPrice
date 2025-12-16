from fastapi import APIRouter

router = APIRouter()

@router.post("/ask")
async def ask_llm():
    return {"message": "LLM response"}
