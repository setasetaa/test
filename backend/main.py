from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import expenses, summary, upload

load_dotenv()

tags_metadata = [
    {"name": "기본", "description": "서버 상태 확인 엔드포인트"},
    {"name": "영수증", "description": "영수증 업로드 및 OCR 처리 (Upstage OCR API → Solar LLM 구조화)"},
    {"name": "지출", "description": "지출 내역 조회·수정·삭제 및 통계 요약"},
]

app = FastAPI(
    title="영수증 지출 관리 API",
    description=(
        "영수증(이미지/PDF)을 업로드하면 **Upstage Document OCR API**로 텍스트를 추출하고 "
        "**ChatUpstage(Solar)**가 지출 데이터로 구조화하여 저장합니다.\n\n"
        "| 엔드포인트 | 설명 |\n"
        "|---|---|\n"
        "| `POST /api/upload` | 영수증 업로드 → OCR → 저장 |\n"
        "| `GET /api/expenses` | 전체 지출 목록 조회 |\n"
        "| `PUT /api/expenses/{id}` | 지출 수정 |\n"
        "| `DELETE /api/expenses/{id}` | 지출 삭제 |\n"
        "| `GET /api/summary` | 월별 지출 통계 |"
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(summary.router, prefix="/api")


@app.get("/", tags=["기본"], summary="서버 상태 확인")
def health_check():
    """서버가 정상적으로 실행 중인지 확인합니다."""
    return {"status": "정상", "message": "영수증 지출 관리 API가 실행 중입니다."}
