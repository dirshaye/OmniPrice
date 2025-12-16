from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_products():
    return {"message": "List of products"}
