from fastapi import FastAPI
from app.routers import product_router
from app.grpc_clients import GrpcClients

app = FastAPI(
    title="API Gateway",
    description="The main entry point for the OmniPriceX API.",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    app.state.grpc_clients = GrpcClients()

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.grpc_clients.close()

app.include_router(product_router.router, prefix="/products", tags=["products"])

@app.get("/")
async def root():
    return {"message": "Welcome to the OmniPriceX API Gateway"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}
