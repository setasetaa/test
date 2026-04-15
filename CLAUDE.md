# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 프로젝트 개요

영수증(이미지/PDF)을 업로드하면 **Upstage Vision LLM**이 자동으로 파싱·구조화하여 지출 데이터를 저장·조회할 수 있는 경량 웹 애플리케이션 (1일 스프린트 MVP).

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 프론트엔드 | React 18 + Vite 5 + TailwindCSS 3 + Axios |
| 백엔드 | Python FastAPI + LangChain + Upstage Document AI (`document-digitization-vision`) |
| 파일 처리 | Pillow / pdf2image (이미지 Base64 전처리) |
| 데이터 저장 | `backend/data/expenses.json` (DB 미사용) |
| 배포 | Vercel (프론트 정적 빌드 + 백엔드 서버리스) |

---

## 프로젝트 구조

```
receipt-tracker/
├── frontend/
│   ├── src/
│   │   ├── pages/          # Dashboard, UploadPage, ExpenseDetail
│   │   ├── components/     # Badge, Modal, Toast
│   │   └── api/            # Axios 인스턴스 및 API 호출 함수
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── main.py             # FastAPI 앱 진입점
│   ├── routers/            # 엔드포인트 라우터
│   ├── services/           # LangChain + Upstage OCR 로직
│   ├── data/
│   │   └── expenses.json   # 지출 데이터 저장소
│   └── requirements.txt
├── vercel.json
└── .env                    # UPSTAGE_API_KEY, GITHUB_API_KEY
```

---

## 개발 명령어

### 백엔드 (Python FastAPI)

```bash
# 의존성 설치
cd backend && pip install -r requirements.txt

# 개발 서버 실행 (hot reload)
uvicorn main:app --reload --port 8000

# API 문서 확인
# http://localhost:8000/docs
```

### 프론트엔드 (React + Vite)

```bash
# 의존성 설치
cd frontend && npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 빌드 결과 미리보기
npm run preview
```

---

## API 엔드포인트

| 메서드 | URL | 설명 |
|--------|-----|------|
| `POST` | `/api/upload` | 영수증 업로드 → Upstage OCR → JSON 저장 |
| `GET` | `/api/expenses` | 전체 지출 목록 조회 (`?from=&to=` 날짜 필터) |
| `DELETE` | `/api/expenses/{id}` | 특정 지출 삭제 |
| `PUT` | `/api/expenses/{id}` | 특정 지출 수정 |
| `GET` | `/api/summary` | 지출 통계 (`?month=` 필터) |

---

## 데이터 스키마 (expenses.json)

```json
{
  "id": "uuid-v4",
  "created_at": "ISO8601",
  "store_name": "string",
  "receipt_date": "YYYY-MM-DD",
  "receipt_time": "HH:MM",
  "category": "string",
  "items": [{ "name": "", "quantity": 0, "unit_price": 0, "total_price": 0 }],
  "subtotal": 0,
  "discount": 0,
  "tax": 0,
  "total_amount": 0,
  "payment_method": "string",
  "raw_image_path": "uploads/..."
}
```

---

## LangChain OCR 처리 흐름

1. 업로드된 파일을 PIL(이미지) 또는 pdf2image(PDF)로 읽어 Base64 인코딩
2. `ChatUpstage` Vision LLM에 Base64 이미지 + System Prompt("JSON 형식으로만 응답") 전달
3. LangChain Output Parser로 구조화 JSON 추출
4. `expenses.json`에 append 저장

---

## 환경변수

`.env` 파일 또는 Vercel Environment Variables에 설정:

| 변수명 | 용도 |
|--------|------|
| `UPSTAGE_API_KEY` | Upstage Document AI 인증 키 |
| `VITE_API_BASE_URL` | 프론트엔드에서 백엔드 API 기본 URL |
| `DATA_FILE_PATH` | expenses.json 저장 경로 (기본: `backend/data/expenses.json`) |

---

## Vercel 배포

```json
// vercel.json
{
  "builds": [
    { "src": "frontend/package.json", "use": "@vercel/static-build" },
    { "src": "backend/main.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "backend/main.py" },
    { "src": "/(.*)", "dest": "frontend/dist/$1" }
  ]
}
```

> **주의**: Vercel 서버리스는 요청마다 새 컨테이너를 사용하므로 `expenses.json` 파일 영속성이 보장되지 않습니다. MVP 단계에서는 클라이언트 `localStorage` 병행 저장을 권장하며, 장기적으로는 Vercel KV 또는 Supabase 전환을 고려하세요.

---

## 지원 파일 및 제약

- 영수증 파일 형식: JPG, PNG, PDF (최대 10MB)
- 지원 언어: 한국어, 영어 영수증
- 인증/로그인 미구현 (1차 범위 외)
- 동시 접속은 단일 사용자 기준
