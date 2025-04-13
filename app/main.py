from fastapi import FastAPI
from app.routes.router import router as v1_router

app = FastAPI()
app.include_router(v1_router, prefix = "/api",  tags = ["v1"])