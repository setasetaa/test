import base64
import json
import os
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path

from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage, SystemMessage
from PIL import Image


SYSTEM_PROMPT = """당신은 영수증 이미지를 분석하는 전문가입니다.
이미지에서 영수증 정보를 추출하여 반드시 아래 JSON 형식으로만 응답하세요.
다른 설명이나 마크다운 없이 순수 JSON만 출력하세요.

{
  "store_name": "상호명 (문자열)",
  "receipt_date": "날짜 YYYY-MM-DD 형식 (없으면 null)",
  "receipt_time": "시간 HH:MM 형식 (없으면 null)",
  "category": "카테고리 (식비/교통/쇼핑/의료/문화/기타 중 하나)",
  "items": [
    {
      "name": "품목명",
      "quantity": 수량(숫자),
      "unit_price": 단가(숫자),
      "total_price": 금액(숫자)
    }
  ],
  "subtotal": 소계(숫자),
  "discount": 할인액(숫자, 없으면 0),
  "tax": 부가세(숫자, 없으면 0),
  "total_amount": 총합계(숫자),
  "payment_method": "결제수단 (현금/카드/모바일페이/기타)"
}

금액은 숫자만 입력하고 통화 기호나 쉼표는 제외하세요.
영수증에서 읽을 수 없는 항목은 null로 설정하세요."""


def _image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def parse_receipt(image: Image.Image) -> dict:
    llm = ChatUpstage(model="solar-vision")
    image_data = _image_to_base64(image)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                },
                {"type": "text", "text": "이 영수증의 내용을 JSON 형식으로 추출해주세요."},
            ]
        ),
    ]

    response = llm.invoke(messages)
    raw_text = response.content.strip()

    # 마크다운 코드블록 제거
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1])

    return json.loads(raw_text)


def _data_file() -> Path:
    return Path(os.getenv("DATA_FILE_PATH", "data/expenses.json"))


def load_expenses() -> list:
    f = _data_file()
    if not f.exists():
        return []
    with open(f, "r", encoding="utf-8") as fp:
        return json.load(fp)


def write_expenses(expenses: list) -> None:
    f = _data_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    with open(f, "w", encoding="utf-8") as fp:
        json.dump(expenses, fp, ensure_ascii=False, indent=2)


def save_expense(parsed: dict, image_path: str) -> dict:
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
    write_expenses(expenses)
    return expense
