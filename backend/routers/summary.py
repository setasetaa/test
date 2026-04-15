from datetime import datetime

from fastapi import APIRouter, Query

from services.storage_service import load_expenses

router = APIRouter()


@router.get(
    "/summary",
    tags=["지출"],
    summary="지출 통계 조회",
    description=(
        "`month` 파라미터(YYYY-MM)로 특정 월의 카테고리별 통계를 조회합니다. "
        "`total_amount`(전체 합계)와 `this_month_amount`(이번달 합계)는 항상 반환됩니다."
    ),
)
def get_summary(month: str = Query(None, description="조회 월 (YYYY-MM)")):
    all_expenses = load_expenses()

    current_month = datetime.now().strftime("%Y-%m")

    # 전체 합계
    total_amount = sum(e.get("total_amount", 0) for e in all_expenses)

    # 이번달 합계
    this_month_expenses = [
        e for e in all_expenses
        if e.get("receipt_date", "").startswith(current_month)
    ]
    this_month_amount = sum(e.get("total_amount", 0) for e in this_month_expenses)

    # 카테고리별 통계 (month 파라미터로 필터)
    target = [
        e for e in all_expenses
        if e.get("receipt_date", "").startswith(month)
    ] if month else all_expenses

    category_map: dict = {}
    for e in target:
        cat = e.get("category", "기타")
        category_map[cat] = category_map.get(cat, 0) + e.get("total_amount", 0)

    category_summary = [
        {"category": cat, "amount": amount}
        for cat, amount in sorted(category_map.items(), key=lambda x: -x[1])
    ]

    return {
        "total_amount": total_amount,
        "this_month_amount": this_month_amount,
        "category_summary": category_summary,
        "건수": len(target),
        "조회_기간": month or "전체",
    }
