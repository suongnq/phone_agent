from router import router as v1_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(v1_router, prefix = "/api",  tags = ["v1"])