from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.services.langgraph_service import PhoneAIFlow

router = APIRouter()
phone_ai_flow = PhoneAIFlow()


class PhoneAIRequest(BaseModel):
    question: str


class SuccessResponse(BaseModel):
    status: str
    data: Dict[str, Any]


class ErrorResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]


@router.post("/ask")
def ask_question(request: PhoneAIRequest):
    question = request.question

    answer = phone_ai_flow.main(question)

    if answer is None:
        data = {
            "answer": "Rất tiếc, hiện tại chúng tôi chưa tìm thấy câu trả lời phù hợp cho câu hỏi của bạn."
        }
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(status="error", message="interrupt", data=data).dict()
        )
    else:
        data = {"answer": answer}
        return JSONResponse(
            status_code=200,
            content=SuccessResponse(status="success", data=data).dict()
        )
