from __future__ import annotations

from typing import List

from omniprice.core.cache import build_cache_key, cache_get_json, cache_set_json
from omniprice.core.exceptions import NotFoundException
from omniprice.models.competitor import Competitor
from omniprice.models.pricing import PricingRule
from omniprice.repositories.pricing import PricingRepository
from omniprice.repositories.product import ProductRepository
from omniprice.schemas.pricing import PricingRuleCreate, PricingRuleUpdate


class PricingService:
    @staticmethod
    async def list_rules(limit: int = 50, offset: int = 0) -> List[PricingRule]:
        return await PricingRepository.list_rules(limit=limit, offset=offset)

    @staticmethod
    async def get_rule(rule_id: str) -> PricingRule:
        rule = await PricingRepository.get_rule(rule_id)
        if not rule:
            raise NotFoundException("Pricing rule not found")
        return rule

    @staticmethod
    async def create_rule(payload: PricingRuleCreate) -> PricingRule:
        rule = PricingRule(**payload.model_dump())
        return await PricingRepository.create_rule(rule)

    @staticmethod
    async def update_rule(rule_id: str, payload: PricingRuleUpdate) -> PricingRule:
        rule = await PricingRepository.get_rule(rule_id)
        if not rule:
            raise NotFoundException("Pricing rule not found")
        update_fields = payload.model_dump(exclude_unset=True)
        if update_fields:
            rule = await PricingRepository.update_rule(rule, **update_fields)
        return rule

    @staticmethod
    async def delete_rule(rule_id: str) -> None:
        rule = await PricingRepository.get_rule(rule_id)
        if not rule:
            raise NotFoundException("Pricing rule not found")
        await PricingRepository.delete_rule(rule)

    @staticmethod
    async def recommend_price(product_id: str) -> dict:
        cache_key = build_cache_key("pricing", "recommendation", product_id)
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

        product = await ProductRepository.get(product_id)
        if not product:
            raise NotFoundException("Product not found")
        rules = await PricingRepository.list_rules(limit=200, offset=0)
        active_rules = [r for r in rules if r.status == "active"]

        current_price = product.current_price
        suggested = current_price
        reasons: list[str] = []

        competitor_prices = await Competitor.find(
            (Competitor.product_id == product_id) & (Competitor.last_price != None)
        ).to_list()
        competitor_avg = (
            sum(c.last_price for c in competitor_prices) / len(competitor_prices)
            if competitor_prices
            else None
        )

        for rule in active_rules:
            if rule.category and product.category and rule.category != product.category:
                continue

            if rule.type == "competitive" and competitor_avg:
                suggested = competitor_avg * (1 + rule.adjustment / 100)
                reasons.append(f"{rule.name}: {rule.adjustment}% vs competitor avg")
                continue

            if rule.type in {"fixed", "dynamic", "clearance"}:
                suggested = suggested * (1 + rule.adjustment / 100)
                reasons.append(f"{rule.name}: {rule.adjustment}% adjustment")

        suggested = max(round(suggested, 2), 0.01)
        reason_text = "; ".join(reasons) if reasons else "No active rules applied"
        payload = {
            "product_id": product_id,
            "current_price": round(current_price, 2),
            "suggested_price": suggested,
            "reason": reason_text,
        }
        await cache_set_json(cache_key, payload, ttl_seconds=120)
        return payload
