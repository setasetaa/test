from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.ocr_service import parse_receipt
from services.storage_service import append_expense

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB


@router.post(
    "/upload",
    tags=["영수증"],
    summary="영수증 업로드 및 OCR 처리",
    description=(
        "JPG·PNG·PDF 영수증을 업로드하면 **Upstage Document OCR API**로 텍스트를 추출하고, "
        "**ChatUpstage(Solar)**가 지출 데이터로 구조화하여 저장합니다.\n\n"
        "- 지원 형식: JPG, PNG, PDF\n"
        "- 최대 파일 크기: 10MB"
    ),
)
async def upload_receipt(
    file: UploadFile = File(..., description="영수증 파일 (JPG/PNG/PDF, 최대 10MB)"),
):
    # 파일 형식 검증
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다: {file.content_type}. JPG, PNG, PDF만 허용됩니다.",
        )

    file_bytes = await file.read()

    # 파일 크기 검증
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB를 초과할 수 없습니다.")

    # 업로드 파일 저장
    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    # OCR 파싱 (Upstage OCR API → Solar LLM 구조화)
    try:
        parsed = parse_receipt(file_bytes, file.filename, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"OCR 처리 중 오류가 발생했습니다. 이미지를 확인하고 다시 시도해 주세요. ({str(e)})",
        )

    # 지출 데이터 저장
    expense = append_expense(parsed, str(save_path))
    return {"message": "영수증이 성공적으로 처리되었습니다.", "data": expense}
