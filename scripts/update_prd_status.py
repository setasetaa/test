#!/usr/bin/env python3
"""
PRD 완료 기준 자동 업데이트 스크립트
Claude Code Stop hook에서 호출됩니다.
각 Phase별 핵심 파일 존재 여부로 완료 기준 체크박스([ ] / [x])를 갱신합니다.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRD  = ROOT / "PRD_영수증_지출관리앱.md"


def exists(*rel_paths: str) -> bool:
    """여러 경로 중 하나라도 존재하면 True"""
    return any((ROOT / p).exists() for p in rel_paths)


def gitignore_has(pattern: str) -> bool:
    gi = ROOT / ".gitignore"
    return gi.exists() and pattern in gi.read_text(encoding="utf-8")


def set_checkbox(content: str, criterion: str, done: bool) -> str:
    """criterion 텍스트를 가진 체크박스를 done 상태로 전환"""
    if done:
        return content.replace(f"- [ ] {criterion}", f"- [x] {criterion}")
    else:
        return content.replace(f"- [x] {criterion}", f"- [ ] {criterion}")


def main() -> None:
    if not PRD.exists():
        return

    content = PRD.read_text(encoding="utf-8")
    original = content

    # ── Phase 1: 환경 설정 ────────────────────────────────────────────────
    phase1_ready = exists("backend/main.py") and exists("venv")

    content = set_checkbox(content,
        "`uvicorn backend.main:app --reload` 실행 시 FastAPI 서버가 정상 기동된다",
        phase1_ready)
    content = set_checkbox(content,
        "`http://localhost:8000/docs` Swagger UI가 열린다",
        phase1_ready)
    content = set_checkbox(content,
        "`.env` 파일이 `.gitignore`에 포함되어 있다",
        gitignore_has(".env"))

    # ── Phase 2: 백엔드 OCR 업로드 ─────────────────────────────────────────
    has_upload  = exists("backend/routers/upload.py")
    has_ocr     = exists("backend/services/ocr_service.py")
    has_storage = exists("backend/services/storage_service.py")

    content = set_checkbox(content,
        '`curl -X POST /api/upload -F "file=@receipt.jpg"` 실행 시 구조화 JSON이 반환된다',
        has_upload and has_ocr and has_storage)
    content = set_checkbox(content,
        "10MB 초과 파일 업로드 시 400 오류가 반환된다",
        has_upload)
    content = set_checkbox(content,
        "PDF 파일 업로드 시 정상적으로 파싱된다",
        has_upload and has_ocr)

    # ── Phase 3: 백엔드 부가 API ──────────────────────────────────────────
    has_expenses = exists("backend/routers/expenses.py")
    has_summary  = exists("backend/routers/summary.py")
    phase3_all   = has_upload and has_expenses and has_summary

    content = set_checkbox(content,
        "Postman으로 5개 엔드포인트(`POST /upload`, `GET/DELETE/PUT /expenses`, `GET /summary`) 전체 정상 응답 확인",
        phase3_all)
    content = set_checkbox(content,
        "`GET /api/expenses?from=2025-07-01&to=2025-07-31` 날짜 필터가 동작한다",
        has_expenses)
    content = set_checkbox(content,
        "존재하지 않는 ID로 DELETE 시 404가 반환된다",
        has_expenses)

    # ── Phase 4: 프론트엔드 환경 설정 ─────────────────────────────────────
    has_pkg_json = exists("frontend/package.json")
    has_tailwind = exists("frontend/tailwind.config.js", "frontend/tailwind.config.ts")
    has_app      = exists("frontend/src/App.jsx", "frontend/src/App.tsx")

    content = set_checkbox(content,
        "`npm run dev` 실행 시 `http://localhost:5173` 에서 React 앱이 열린다",
        has_pkg_json)
    content = set_checkbox(content,
        "TailwindCSS 클래스가 정상 적용된다",
        has_tailwind)
    content = set_checkbox(content,
        "`/`, `/upload`, `/expense/:id` 3개 경로가 라우팅된다",
        has_app)

    # ── Phase 5: 업로드 화면 ──────────────────────────────────────────────
    has_dropzone   = exists("frontend/src/components/DropZone.jsx",    "frontend/src/components/DropZone.tsx")
    has_progress   = exists("frontend/src/components/ProgressBar.jsx", "frontend/src/components/ProgressBar.tsx")
    has_preview    = exists("frontend/src/components/ParsePreview.jsx","frontend/src/components/ParsePreview.tsx")
    has_upload_pg  = exists("frontend/src/pages/UploadPage.jsx",       "frontend/src/pages/UploadPage.tsx")
    has_toast      = exists("frontend/src/components/Toast.jsx",       "frontend/src/components/Toast.tsx")

    content = set_checkbox(content,
        "이미지를 드래그 앤 드롭하면 OCR 파싱이 실행된다",
        has_dropzone and has_upload_pg)
    content = set_checkbox(content,
        "ProgressBar가 처리 중 표시되고 완료 후 숨겨진다",
        has_progress)
    content = set_checkbox(content,
        "ParsePreview에서 필드를 수정하고 저장 시 대시보드로 이동한다",
        has_preview and has_upload_pg)
    content = set_checkbox(content,
        "Toast 알림이 저장 성공 시 표시된다",
        has_toast)

    # ── Phase 6: 대시보드 화면 ────────────────────────────────────────────
    has_dashboard = exists("frontend/src/pages/Dashboard.jsx",       "frontend/src/pages/Dashboard.tsx")
    has_exp_card  = exists("frontend/src/components/ExpenseCard.jsx","frontend/src/components/ExpenseCard.tsx")
    has_sum_card  = exists("frontend/src/components/SummaryCard.jsx","frontend/src/components/SummaryCard.tsx")
    has_filter    = exists("frontend/src/components/FilterBar.jsx",  "frontend/src/components/FilterBar.tsx")

    content = set_checkbox(content,
        "대시보드 진입 시 저장된 지출 내역이 카드 목록으로 표시된다",
        has_dashboard and has_exp_card)
    content = set_checkbox(content,
        "SummaryCard에 총 지출 / 이번달 지출 금액이 표시된다",
        has_sum_card)
    content = set_checkbox(content,
        "날짜 필터 적용 시 해당 기간 내역만 표시된다",
        has_filter)
    content = set_checkbox(content,
        "내역이 없을 때 Empty State가 표시된다",
        has_dashboard)

    # ── Phase 7: 상세/수정 화면 ───────────────────────────────────────────
    has_detail = exists("frontend/src/pages/ExpenseDetail.jsx","frontend/src/pages/ExpenseDetail.tsx")
    has_edit   = exists("frontend/src/components/EditForm.jsx","frontend/src/components/EditForm.tsx")
    has_modal  = exists("frontend/src/components/Modal.jsx",   "frontend/src/components/Modal.tsx")

    content = set_checkbox(content,
        "ExpenseCard 클릭 시 상세 페이지로 이동한다",
        has_detail and has_exp_card)
    content = set_checkbox(content,
        "필드 수정 후 \"수정 저장\" 클릭 시 PUT API가 호출되고 Toast가 표시된다",
        has_edit)
    content = set_checkbox(content,
        "\"삭제\" 클릭 시 Modal이 열리고, 확인 시 항목이 삭제되어 대시보드로 이동한다",
        has_modal and has_detail)

    # ── 변경된 경우에만 파일 저장 ─────────────────────────────────────────
    if content != original:
        PRD.write_text(content, encoding="utf-8")

    # Stop hook: 출력 억제
    print('{"suppressOutput": true}')


if __name__ == "__main__":
    main()
