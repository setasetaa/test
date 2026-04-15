from fastapi import APIRouter, HTTPException, Query

from services.storage_service import load_expenses, save_expenses

router = APIRouter()


@router.get(
    "/expenses",
    tags=["지출"],
    summary="전체 지출 목록 조회",
    description="`from`·`to` 쿼리 파라미터로 날짜 범위를 필터링할 수 있습니다. (형식: YYYY-MM-DD)",
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


@router.put(
    "/expenses/{expense_id}",
    tags=["지출"],
    summary="지출 수정",
    description="변경할 필드만 JSON body로 전달하면 됩니다. `id`, `created_at`은 변경 불가.",
)
def update_expense(expense_id: str, body: dict):
    expenses = load_expenses()
    for i, e in enumerate(expenses):
        if e["id"] == expense_id:
            body.pop("id", None)
            body.pop("created_at", None)
            expenses[i].update(body)
            save_expenses(expenses)
            return {"message": "지출이 수정되었습니다.", "data": expenses[i]}
    raise HTTPException(status_code=404, detail="해당 지출 항목을 찾을 수 없습니다.")


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
    save_expenses(filtered)
    return {"message": "지출이 삭제되었습니다."}
