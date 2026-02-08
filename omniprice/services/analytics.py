from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from omniprice.core.cache import build_cache_key, cache_get_json, cache_set_json
from omniprice.models.competitor import Competitor, PriceHistory
from omniprice.models.pricing import PricingRule
from omniprice.models.product import Product
from omniprice.models.scrape import ScrapeExecution


def _safe_percent_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 2)


class AnalyticsService:
    @staticmethod
    async def get_dashboard() -> dict:
        cache_key = build_cache_key("analytics", "dashboard")
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

        total_products = await Product.count()
        active_rules = await PricingRule.find(PricingRule.status == "active").count()
        competitors_tracked = await Competitor.count()

        products = await Product.find().to_list()
        total_revenue = 0.0
        for product in products:
            qty = product.stock_quantity if product.stock_quantity is not None and product.stock_quantity > 0 else 1
            total_revenue += product.current_price * qty
        avg_price = round((sum(p.current_price for p in products) / len(products)), 2) if products else 0.0

        now = datetime.utcnow()
        day_start = datetime(now.year, now.month, now.day)
        prev_day_start = day_start - timedelta(days=1)

        today_changes = await PriceHistory.find(PriceHistory.captured_at >= day_start).count()
        products_today = await Product.find(Product.created_at >= day_start).count()
        products_prev_day = await Product.find(
            (Product.created_at >= prev_day_start) & (Product.created_at < day_start)
        ).count()

        history_today = await PriceHistory.find(PriceHistory.captured_at >= day_start).to_list()
        history_prev_day = await PriceHistory.find(
            (PriceHistory.captured_at >= prev_day_start) & (PriceHistory.captured_at < day_start)
        ).to_list()
        avg_today = sum(h.price for h in history_today) / len(history_today) if history_today else 0.0
        avg_prev = sum(h.price for h in history_prev_day) / len(history_prev_day) if history_prev_day else 0.0

        payload = {
            "total_products": total_products,
            "active_rules": active_rules,
            "competitors_tracked": competitors_tracked,
            "total_revenue": round(total_revenue, 2),
            "avg_price": avg_price,
            "price_changes_today": today_changes,
            "product_growth": f"{_safe_percent_change(products_today, products_prev_day)}%",
            "revenue_trend": f"{_safe_percent_change(avg_today, avg_prev)}%",
            "last_updated": now.isoformat() + "Z",
        }
        await cache_set_json(cache_key, payload, ttl_seconds=60)
        return payload

    @staticmethod
    async def get_price_trends(days: int = 7) -> dict:
        cache_key = build_cache_key("analytics", "price_trends", str(days))
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

        now = datetime.utcnow()
        start = datetime(now.year, now.month, now.day) - timedelta(days=days - 1)
        history = await PriceHistory.find(PriceHistory.captured_at >= start).to_list()
        products = await Product.find().to_list()

        daily_prices: dict[str, list[float]] = defaultdict(list)
        for row in history:
            key = row.captured_at.strftime("%Y-%m-%d")
            daily_prices[key].append(row.price)

        payload_rows = []
        for i in range(days):
            day = start + timedelta(days=i)
            date_key = day.strftime("%Y-%m-%d")
            prices = daily_prices.get(date_key, [])
            revenue = round(sum(prices) / len(prices), 2) if prices else round(sum(p.current_price for p in products), 2) if products else 0.0
            payload_rows.append(
                {
                    "date": date_key,
                    "revenue": revenue,
                    "products": len(products),
                }
            )

        payload = {"price_data": payload_rows}
        await cache_set_json(cache_key, payload, ttl_seconds=120)
        return payload

    @staticmethod
    async def get_competitor_distribution() -> dict:
        cache_key = build_cache_key("analytics", "competitor_distribution")
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

        competitors = await Competitor.find().to_list()
        counts: dict[str, int] = {}
        for competitor in competitors:
            counts[competitor.competitor_name] = counts.get(competitor.competitor_name, 0) + 1
        payload = {"competitor_data": [{"name": name, "value": count} for name, count in counts.items()]}
        await cache_set_json(cache_key, payload, ttl_seconds=120)
        return payload

    @staticmethod
    async def get_recent_activity(limit: int = 8) -> dict:
        cache_key = build_cache_key("analytics", "recent_activity", str(limit))
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

        activities: list[dict] = []
        latest_products = await Product.find().sort("-created_at").limit(limit).to_list()
        latest_competitors = await Competitor.find().sort("-created_at").limit(limit).to_list()
        latest_rules = await PricingRule.find().sort("-created_at").limit(limit).to_list()
        latest_prices = await PriceHistory.find().sort("-captured_at").limit(limit).to_list()

        for product in latest_products:
            activities.append(
                {
                    "timestamp": product.created_at.isoformat() + "Z",
                    "time": product.created_at.strftime("%H:%M"),
                    "message": f"Created product: {product.name}",
                }
            )
        for competitor in latest_competitors:
            activities.append(
                {
                    "timestamp": competitor.created_at.isoformat() + "Z",
                    "time": competitor.created_at.strftime("%H:%M"),
                    "message": f"Tracked competitor: {competitor.competitor_name}",
                }
            )
        for rule in latest_rules:
            activities.append(
                {
                    "timestamp": rule.created_at.isoformat() + "Z",
                    "time": rule.created_at.strftime("%H:%M"),
                    "message": f"Created pricing rule: {rule.name}",
                }
            )
        for history in latest_prices:
            activities.append(
                {
                    "timestamp": history.captured_at.isoformat() + "Z",
                    "time": history.captured_at.strftime("%H:%M"),
                    "message": f"Captured market price: {history.price} {history.currency or ''}".strip(),
                }
            )

        activities = sorted(activities, key=lambda item: item["timestamp"], reverse=True)[:limit]
        payload = {"activities": activities}
        await cache_set_json(cache_key, payload, ttl_seconds=60)
        return payload

    @staticmethod
    async def get_price_history(product_id: str, days: int = 30) -> dict:
        cache_key = build_cache_key("analytics", "price_history", product_id, str(days))
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

        now = datetime.utcnow()
        start = now - timedelta(days=max(days, 1))
        history = await PriceHistory.find(
            (PriceHistory.product_id == product_id) & (PriceHistory.captured_at >= start)
        ).sort("captured_at").to_list()
        payload = {
            "product_id": product_id,
            "days": days,
            "price_history": [
                {
                    "captured_at": row.captured_at.isoformat() + "Z",
                    "price": row.price,
                    "currency": row.currency,
                    "source": row.source,
                }
                for row in history
            ],
        }
        await cache_set_json(cache_key, payload, ttl_seconds=60)
        return payload

    @staticmethod
    async def get_market_trends(days: int = 14) -> dict:
        cache_key = build_cache_key("analytics", "market_trends", str(days))
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

        now = datetime.utcnow()
        start = now - timedelta(days=max(days, 1))
        history = await PriceHistory.find(PriceHistory.captured_at >= start).to_list()
        by_competitor: dict[str, list[float]] = defaultdict(list)
        for row in history:
            key = row.competitor_id or "unknown"
            by_competitor[key].append(row.price)

        trends = []
        for competitor_id, prices in by_competitor.items():
            if not prices:
                continue
            trends.append(
                {
                    "competitor_id": competitor_id,
                    "observations": len(prices),
                    "avg_price": round(sum(prices) / len(prices), 2),
                    "min_price": round(min(prices), 2),
                    "max_price": round(max(prices), 2),
                }
            )

        payload = {"days": days, "market_trends": trends}
        await cache_set_json(cache_key, payload, ttl_seconds=120)
        return payload

    @staticmethod
    async def get_performance_metrics() -> dict:
        cache_key = build_cache_key("analytics", "performance")
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

        total_competitors = await Competitor.count()
        active_competitors = await Competitor.find(Competitor.is_active == True).count()
        total_price_points = await PriceHistory.count()
        rules = await PricingRule.find().to_list()
        active_rules = sum(1 for rule in rules if rule.status == "active")

        payload = {
            "active_competitors": active_competitors,
            "total_competitors": total_competitors,
            "total_price_points": total_price_points,
            "active_rules": active_rules,
            "rule_activation_rate": round((active_rules / len(rules)) * 100, 2) if rules else 0.0,
        }
        await cache_set_json(cache_key, payload, ttl_seconds=60)
        return payload

    @staticmethod
    async def get_scraper_health(hours: int = 24) -> dict:
        bounded_hours = max(1, min(hours, 24 * 30))
        cache_key = build_cache_key("analytics", "scraper_health", str(bounded_hours))
        cached = await cache_get_json(cache_key)
        if cached:
            return cached

        now = datetime.utcnow()
        start = now - timedelta(hours=bounded_hours)
        rows = await ScrapeExecution.find(ScrapeExecution.created_at >= start).to_list()

        total = len(rows)
        successful = [row for row in rows if row.status == "success"]
        failed = [row for row in rows if row.status.startswith("failed")]
        retry_scheduled = [row for row in rows if row.status == "retry_scheduled"]

        by_domain: dict[str, dict[str, int]] = {}
        by_source: dict[str, int] = {}
        error_classes: dict[str, int] = {}

        for row in rows:
            domain_stats = by_domain.setdefault(row.domain, {"total": 0, "success": 0, "failed": 0})
            domain_stats["total"] += 1
            if row.status == "success":
                domain_stats["success"] += 1
            elif row.status.startswith("failed"):
                domain_stats["failed"] += 1

            if row.source:
                by_source[row.source] = by_source.get(row.source, 0) + 1
            if row.error_class:
                error_classes[row.error_class] = error_classes.get(row.error_class, 0) + 1

        avg_latency_ms = (
            round(sum((row.latency_ms or 0) for row in successful) / len(successful), 2)
            if successful
            else None
        )
        success_rate = round((len(successful) / total) * 100, 2) if total else None

        payload = {
            "window_hours": bounded_hours,
            "total_jobs": total,
            "successful_jobs": len(successful),
            "failed_jobs": len(failed),
            "retry_scheduled_jobs": len(retry_scheduled),
            "success_rate_percent": success_rate,
            "avg_success_latency_ms": avg_latency_ms,
            "by_domain": by_domain,
            "by_source": by_source,
            "error_classes": error_classes,
            "generated_at": now.isoformat() + "Z",
        }
        await cache_set_json(cache_key, payload, ttl_seconds=60)
        return payload
