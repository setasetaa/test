from fastapi import APIRouter, Query

from services.storage_service import load_expenses

router = APIRouter()


@router.get(
    "/summary",
    tags=["지출"],
    summary="월별 지출 통계",
    description="`month` 파라미터(YYYY-MM)로 특정 월을 조회합니다. 생략 시 전체 통계를 반환합니다.",
)
def get_summary(month: str = Query(None, description="조회 월 (YYYY-MM)")):
    expenses = load_expenses()

    if month:
        expenses = [
            e for e in expenses
            if e.get("receipt_date") and e["receipt_date"].startswith(month)
        ]

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
