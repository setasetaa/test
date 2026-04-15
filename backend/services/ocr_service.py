"""
OCR 서비스: Upstage Document OCR API → 텍스트 추출 → ChatUpstage(Solar) → JSON 구조화

처리 흐름:
  1. POST https://api.upstage.ai/v1/document-digitization (model=ocr)
     → 영수증 이미지에서 원문 텍스트 추출
  2. ChatUpstage(solar-pro) + System Prompt
     → 추출된 텍스트를 지출 스키마 JSON으로 구조화
"""

import json
import os

import requests
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_upstage import ChatUpstage

UPSTAGE_OCR_URL = "https://api.upstage.ai/v1/document-digitization"

STRUCTURE_PROMPT = """당신은 영수증 OCR 텍스트를 분석하는 전문가입니다.
아래에 제공되는 영수증 OCR 원문 텍스트를 읽고, 반드시 아래 JSON 형식으로만 응답하세요.
마크다운 코드블록이나 다른 설명 없이 순수 JSON만 출력하세요.

{
  "store_name": "상호명 (문자열, 없으면 null)",
  "receipt_date": "날짜 YYYY-MM-DD 형식 (없으면 null)",
  "receipt_time": "시간 HH:MM 형식 (없으면 null)",
  "category": "카테고리 (식비/교통/쇼핑/의료/문화/기타 중 하나)",
  "items": [
    {
      "name": "품목명",
      "quantity": 수량(숫자),
      "unit_price": 단가(숫자),
      "total_price": 소계(숫자)
    }
  ],
  "subtotal": 소계합계(숫자),
  "discount": 할인액(숫자, 없으면 0),
  "tax": 부가세(숫자, 없으면 0),
  "total_amount": 최종결제금액(숫자),
  "payment_method": "결제수단 (현금/카드/모바일페이/기타, 없으면 null)"
}

규칙:
- 금액은 숫자만 입력 (통화 기호, 쉼표 제외)
- 읽을 수 없는 항목은 null
- items 배열이 비어 있으면 []"""


def call_upstage_ocr(file_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Upstage Document OCR REST API 호출하여 원문 텍스트 반환.
    docs: https://console.upstage.ai/docs/capabilities/document-digitization/document-ocr
    """
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise ValueError("UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.")

    headers = {"Authorization": f"Bearer {api_key}"}
    files = {"document": (filename, file_bytes, content_type)}
    data = {"model": "ocr"}

    resp = requests.post(UPSTAGE_OCR_URL, headers=headers, files=files, data=data, timeout=30)
    resp.raise_for_status()

    result = resp.json()
    # 전체 페이지 텍스트 합산
    text = result.get("text", "")
    if not text:
        # pages[].text 로 폴백
        pages = result.get("pages", [])
        text = "\n".join(p.get("text", "") for p in pages)
    return text


def structure_receipt(ocr_text: str) -> dict:
    """
    OCR 원문 텍스트를 ChatUpstage(Solar)로 구조화된 JSON으로 변환.
    """
    llm = ChatUpstage(model="solar-pro")
    messages = [
        SystemMessage(content=STRUCTURE_PROMPT),
        HumanMessage(content=f"다음은 영수증 OCR 원문입니다:\n\n{ocr_text}"),
    ]
    response = llm.invoke(messages)
    raw = response.content.strip()

    # 마크다운 코드블록 제거
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])

    return json.loads(raw)


def parse_receipt(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """
    전체 파이프라인: OCR 추출 → JSON 구조화
    """
    ocr_text = call_upstage_ocr(file_bytes, filename, content_type)
    if not ocr_text.strip():
        raise ValueError("OCR 결과에서 텍스트를 추출하지 못했습니다.")
    return structure_receipt(ocr_text)
