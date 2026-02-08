from fastapi import APIRouter, status

from omniprice.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from omniprice.services.product import ProductService

router = APIRouter()


def _to_response(p) -> ProductResponse:
    return ProductResponse(
        id=str(p.id),
        name=p.name,
        sku=p.sku,
        category=p.category,
        cost=p.cost,
        current_price=p.current_price,
        stock_quantity=p.stock_quantity,
        is_active=p.is_active,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@router.get("/", response_model=list[ProductResponse])
async def list_products(limit: int = 50, offset: int = 0):
    products = await ProductService.list_products(limit=limit, offset=offset)
    return [_to_response(p) for p in products]


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate):
    return _to_response(await ProductService.create_product(payload))


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    return _to_response(await ProductService.get_product(product_id))


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, payload: ProductUpdate):
    return _to_response(await ProductService.update_product(product_id, payload))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str):
    await ProductService.delete_product(product_id)
    return None

