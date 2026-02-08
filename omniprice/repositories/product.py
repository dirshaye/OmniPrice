from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from omniprice.models.product import Product


class ProductRepository:
    @staticmethod
    async def list(limit: int = 50, offset: int = 0) -> List[Product]:
        return await Product.find().skip(offset).limit(limit).to_list()

    @staticmethod
    async def get(product_id: str) -> Optional[Product]:
        return await Product.get(product_id)

    @staticmethod
    async def get_by_sku(sku: str) -> Optional[Product]:
        return await Product.find_one(Product.sku == sku)

    @staticmethod
    async def create(product: Product) -> Product:
        return await product.insert()

    @staticmethod
    async def update(product: Product, **fields) -> Product:
        fields["updated_at"] = datetime.utcnow()
        await product.set(fields)
        return product

    @staticmethod
    async def delete(product: Product) -> None:
        await product.delete()
