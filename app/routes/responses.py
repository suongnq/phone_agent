from typing import Dict, Any
from pydantic import BaseModel

class SuccessResponse(BaseModel):
    status: str
    data: Dict[str, Any]

class ErrorResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]