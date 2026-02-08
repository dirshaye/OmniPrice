from fastapi import APIRouter, status

from omniprice.schemas.pricing import (
    PricingRecommendationResponse,
    PricingRuleCreate,
    PricingRuleResponse,
    PricingRuleUpdate,
)
from omniprice.services.pricing import PricingService

router = APIRouter()


def _to_response(r) -> PricingRuleResponse:
    return PricingRuleResponse(
        id=str(r.id),
        name=r.name,
        description=r.description,
        type=r.type,
        category=r.category,
        adjustment=r.adjustment,
        status=r.status,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.get("/rules", response_model=list[PricingRuleResponse])
async def list_rules(limit: int = 50, offset: int = 0):
    rules = await PricingService.list_rules(limit=limit, offset=offset)
    return [_to_response(r) for r in rules]


@router.post("/rules", response_model=PricingRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(payload: PricingRuleCreate):
    return _to_response(await PricingService.create_rule(payload))


@router.put("/rules/{rule_id}", response_model=PricingRuleResponse)
async def update_rule(rule_id: str, payload: PricingRuleUpdate):
    return _to_response(await PricingService.update_rule(rule_id, payload))


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: str):
    await PricingService.delete_rule(rule_id)
    return None


@router.get("/recommendations/{product_id}", response_model=PricingRecommendationResponse)
async def recommend_price(product_id: str):
    return PricingRecommendationResponse(**(await PricingService.recommend_price(product_id)))

