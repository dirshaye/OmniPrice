from fastapi import APIRouter, Depends, HTTPException
from app.grpc_clients import GrpcClients
from app.proto import product_service_pb2
import grpc

router = APIRouter()

def get_grpc_clients(request):
    return request.app.state.grpc_clients

@router.post("/")
async def create_product(
    product_data: dict,
    clients: GrpcClients = Depends(get_grpc_clients)
):
    try:
        request = product_service_pb2.CreateProductRequest(**product_data)
        response = await clients.product_stub.CreateProduct(request)
        return response
    except grpc.aio.AioRpcError as e:
        raise HTTPException(status_code=e.code(), detail=e.details())

@router.get("/{product_id}")
async def get_product(
    product_id: str,
    clients: GrpcClients = Depends(get_grpc_clients)
):
    try:
        request = product_service_pb2.GetProductRequest(id=product_id)
        response = await clients.product_stub.GetProduct(request)
        return response
    except grpc.aio.AioRpcError as e:
        raise HTTPException(status_code=e.code(), detail=e.details())

@router.put("/{product_id}")
async def update_product(
    product_id: str,
    product_data: dict,
    clients: GrpcClients = Depends(get_grpc_clients)
):
    try:
        product_data["id"] = product_id
        request = product_service_pb2.UpdateProductRequest(**product_data)
        response = await clients.product_stub.UpdateProduct(request)
        return response
    except grpc.aio.AioRpcError as e:
        raise HTTPException(status_code=e.code(), detail=e.details())

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    clients: GrpcClients = Depends(get_grpc_clients)
):
    try:
        request = product_service_pb2.DeleteProductRequest(id=product_id)
        response = await clients.product_stub.DeleteProduct(request)
        return response
    except grpc.aio.AioRpcError as e:
        raise HTTPException(status_code=e.code(), detail=e.details())

@router.get("/")
async def list_products(
    clients: GrpcClients = Depends(get_grpc_clients)
):
    try:
        request = product_service_pb2.ListProductsRequest()
        response = await clients.product_stub.ListProducts(request)
        return response
    except grpc.aio.AioRpcError as e:
        raise HTTPException(status_code=e.code(), detail=e.details())
