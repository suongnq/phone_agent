from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from phone_ai_langgraph_flow import PhoneAIFlow

router = APIRouter()
phone_ai_flow = PhoneAIFlow()


class PhoneAIRequest(BaseModel):
    question: str


class PhoneAIResponse(BaseModel):
    answer: str

@router.post("/ask", response_model=PhoneAIResponse)
def ask_question(request: PhoneAIRequest):
    question = request.question

    answer = phone_ai_flow.main(question)

    if answer is None:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "interrupt",
                "data": {
                    "answer": "Rất tiếc, hiện tại chúng tôi chưa tìm thấy câu trả lời phù hợp cho câu hỏi của bạn."
                },
            },
        )
    else:
        return JSONResponse(
            status_code=200, content={"status": "success", "data": {"answer": answer}}
        )
