import os
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io

from services.ocr_service import (
    load_expenses,
    parse_receipt,
    save_expense,
    write_expenses,
)

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB


# ──────────────────────────────────────────
# POST /api/upload
# ──────────────────────────────────────────
@router.post(
    "/upload",
    tags=["영수증"],
    summary="영수증 업로드 및 OCR 처리",
    description="JPG·PNG·PDF 영수증을 업로드하면 Upstage Vision LLM이 파싱하여 지출 데이터로 저장합니다.",
)
async def upload_receipt(file: UploadFile = File(..., description="영수증 파일 (JPG/PNG/PDF, 최대 10MB)")):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="JPG, PNG, PDF 파일만 업로드 가능합니다.")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB를 초과할 수 없습니다.")

    # 저장
    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as f:
        f.write(contents)

    # 이미지 변환
    if file.content_type == "application/pdf":
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(contents)
            image = images[0]
        except Exception:
            raise HTTPException(status_code=422, detail="PDF 변환에 실패했습니다. poppler 설치 여부를 확인하세요.")
    else:
        image = Image.open(io.BytesIO(contents)).convert("RGB")

    # OCR
    try:
        parsed = parse_receipt(image)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OCR 처리 중 오류가 발생했습니다: {str(e)}")

    expense = save_expense(parsed, str(save_path))
    return {"message": "영수증이 성공적으로 처리되었습니다.", "data": expense}


# ──────────────────────────────────────────
# GET /api/expenses
# ──────────────────────────────────────────
@router.get(
    "/expenses",
    tags=["지출"],
    summary="전체 지출 목록 조회",
    description="`from`·`to` 파라미터로 날짜 범위를 필터링할 수 있습니다. (형식: YYYY-MM-DD)",
)
def get_expenses(
    from_date: str = Query(None, alias="from", description="시작 날짜 (YYYY-MM-DD)"),
    to_date: str = Query(None, alias="to", description="종료 날짜 (YYYY-MM-DD)"),
):
    expenses = load_expenses()

    if from_date:
        expenses = [e for e in expenses if e.get("receipt_date") and e["receipt_date"] >= from_date]
    if to_date:
        expenses = [e for e in expenses if e.get("receipt_date") and e["receipt_date"] <= to_date]

    return {"총_건수": len(expenses), "data": expenses}


# ──────────────────────────────────────────
# PUT /api/expenses/{id}
# ──────────────────────────────────────────
@router.put(
    "/expenses/{expense_id}",
    tags=["지출"],
    summary="지출 수정",
    description="지출 항목의 내용을 수정합니다. 변경할 필드만 전달하면 됩니다.",
)
def update_expense(expense_id: str, body: dict):
    expenses = load_expenses()
    for i, e in enumerate(expenses):
        if e["id"] == expense_id:
            # id, created_at은 변경 불가
            body.pop("id", None)
            body.pop("created_at", None)
            expenses[i].update(body)
            write_expenses(expenses)
            return {"message": "지출이 수정되었습니다.", "data": expenses[i]}
    raise HTTPException(status_code=404, detail="해당 지출 항목을 찾을 수 없습니다.")


# ──────────────────────────────────────────
# DELETE /api/expenses/{id}
# ──────────────────────────────────────────
@router.delete(
    "/expenses/{expense_id}",
    tags=["지출"],
    summary="지출 삭제",
)
def delete_expense(expense_id: str):
    expenses = load_expenses()
    filtered = [e for e in expenses if e["id"] != expense_id]
    if len(filtered) == len(expenses):
        raise HTTPException(status_code=404, detail="해당 지출 항목을 찾을 수 없습니다.")
    write_expenses(filtered)
    return {"message": "지출이 삭제되었습니다."}


# ──────────────────────────────────────────
# GET /api/summary
# ──────────────────────────────────────────
@router.get(
    "/summary",
    tags=["지출"],
    summary="월별 지출 통계",
    description="`month` 파라미터로 특정 월을 조회합니다. (형식: YYYY-MM, 생략 시 전체)",
)
def get_summary(month: str = Query(None, description="조회 월 (YYYY-MM)")):
    expenses = load_expenses()

    if month:
        expenses = [e for e in expenses if e.get("receipt_date") and e["receipt_date"].startswith(month)]

    total = sum(e.get("total_amount", 0) for e in expenses)
    by_category: dict = {}
    for e in expenses:
        cat = e.get("category", "기타")
        by_category[cat] = by_category.get(cat, 0) + e.get("total_amount", 0)

    return {
        "조회_기간": month or "전체",
        "총_지출": total,
        "건수": len(expenses),
        "카테고리별": by_category,
    }
