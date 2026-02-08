from __future__ import annotations

from typing import List

from omniprice.core.exceptions import ConflictException, NotFoundException
from omniprice.models.product import Product
from omniprice.repositories.product import ProductRepository
from omniprice.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    async def list_products(limit: int = 50, offset: int = 0) -> List[Product]:
        return await ProductRepository.list(limit=limit, offset=offset)

    @staticmethod
    async def get_product(product_id: str) -> Product:
        product = await ProductRepository.get(product_id)
        if not product:
            raise NotFoundException("Product not found")
        return product

    @staticmethod
    async def create_product(payload: ProductCreate) -> Product:
        if payload.sku:
            existing = await ProductRepository.get_by_sku(payload.sku)
            if existing:
                raise ConflictException("SKU already exists")
        product = Product(**payload.model_dump())
        return await ProductRepository.create(product)

    @staticmethod
    async def update_product(product_id: str, payload: ProductUpdate) -> Product:
        product = await ProductRepository.get(product_id)
        if not product:
            raise NotFoundException("Product not found")

        update_fields = payload.model_dump(exclude_unset=True)
        if "sku" in update_fields and update_fields["sku"]:
            existing = await ProductRepository.get_by_sku(update_fields["sku"])
            if existing and str(existing.id) != str(product.id):
                raise ConflictException("SKU already exists")
        if update_fields:
            product = await ProductRepository.update(product, **update_fields)
        return product

    @staticmethod
    async def delete_product(product_id: str) -> None:
        product = await ProductRepository.get(product_id)
        if not product:
            raise NotFoundException("Product not found")
        await ProductRepository.delete(product)
