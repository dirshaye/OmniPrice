from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from omniprice.models.pricing import PricingRule


class PricingRepository:
    @staticmethod
    async def list_rules(limit: int = 50, offset: int = 0) -> List[PricingRule]:
        return await PricingRule.find().skip(offset).limit(limit).to_list()

    @staticmethod
    async def get_rule(rule_id: str) -> Optional[PricingRule]:
        return await PricingRule.get(rule_id)

    @staticmethod
    async def create_rule(rule: PricingRule) -> PricingRule:
        return await rule.insert()

    @staticmethod
    async def update_rule(rule: PricingRule, **fields) -> PricingRule:
        fields["updated_at"] = datetime.utcnow()
        await rule.set(fields)
        return rule

    @staticmethod
    async def delete_rule(rule: PricingRule) -> None:
        await rule.delete()
