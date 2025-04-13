from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.routes.responses import SuccessResponse, ErrorResponse
from app.routes.requests import PhoneAIRequest, CrawlDataRequest

from app.services.crawler_service import Crawler
from app.services.langgraph_service import PhoneAIFlow
from app.services.generate_embedding_service import execute_generate_embedding

router = APIRouter()

@router.post("/ask-phone-agent")
def ask_question(request: PhoneAIRequest):
    question = request.question

    phone_ai_flow = PhoneAIFlow()
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


@router.post("/crawl-data")
def crawl_data(request: CrawlDataRequest):
    crawl_type = request.type

    crawler = Crawler()
    status = crawler.crawling(crawl_type)

    if status is False:
        data = {
            "answer": "Crawl dữ liệu không thành công."
        }
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(status="error", message="failed crawl data", data=data).dict()
        )
    else:
        data = {"answer": "Crawl dữ liệu đã thành công."}
        return JSONResponse(
            status_code=200,
            content=SuccessResponse(status="success", data=data).dict()
        )

@router.get("/generate-embedding")
def generate_embedding():
    status = execute_generate_embedding()

    if status is False:
        data = {
            "answer": "Tạo Vector Database thất bại."
        }
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(status="error", message="failed generate embedding", data=data).dict()
        )
    else:
        data = {"answer": "Tạo Vector Database thành công."}
        return JSONResponse(
            status_code=200,
            content=SuccessResponse(status="success", data=data).dict()
        )
