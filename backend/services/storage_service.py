import json
import os
import uuid
from datetime import datetime
from pathlib import Path


def _data_file() -> Path:
    return Path(os.getenv("DATA_FILE_PATH", "data/expenses.json"))


def load_expenses() -> list:
    f = _data_file()
    if not f.exists():
        return []
    with open(f, "r", encoding="utf-8") as fp:
        return json.load(fp)


def save_expenses(expenses: list) -> None:
    f = _data_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    with open(f, "w", encoding="utf-8") as fp:
        json.dump(expenses, fp, ensure_ascii=False, indent=2)


def append_expense(parsed: dict, image_path: str) -> dict:
    expense = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(),
        "store_name": parsed.get("store_name"),
        "receipt_date": parsed.get("receipt_date"),
        "receipt_time": parsed.get("receipt_time"),
        "category": parsed.get("category", "기타"),
        "items": parsed.get("items", []),
        "subtotal": parsed.get("subtotal", 0),
        "discount": parsed.get("discount", 0),
        "tax": parsed.get("tax", 0),
        "total_amount": parsed.get("total_amount", 0),
        "payment_method": parsed.get("payment_method"),
        "raw_image_path": image_path,
    }
    expenses = load_expenses()
    expenses.append(expense)
    save_expenses(expenses)
    return expense
