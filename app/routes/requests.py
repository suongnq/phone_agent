from typing import Dict, Any
from pydantic import BaseModel

class PhoneAIRequest(BaseModel):
    question: str
class CrawlDataRequest(BaseModel):
    type: str
