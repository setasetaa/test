import { useState } from 'react';

const CATEGORIES = ['식비', '식료품', '외식', '교통', '쇼핑', '의료', '문화', '기타'];
const PAYMENTS = ['카드', '현금', '모바일페이', '기타'];

export default function ParsePreview({ data, onSave, onCancel }) {
  const [form, setForm] = useState(data);

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function updateItem(idx, key, value) {
    setForm((prev) => {
      const items = [...(prev.items || [])];
      items[idx] = { ...items[idx], [key]: key === 'name' ? value : Number(value) };
      return { ...prev, items };
    });
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mt-4">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">파싱 결과 미리보기</h2>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div>
          <label className="text-xs text-gray-500 mb-1 block">가게명</label>
          <input
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            value={form.store_name || ''}
            onChange={(e) => update('store_name', e.target.value)}
          />
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-1 block">날짜</label>
          <input
            type="date"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            value={form.receipt_date || ''}
            onChange={(e) => update('receipt_date', e.target.value)}
          />
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-1 block">카테고리</label>
          <select
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            value={form.category || '기타'}
            onChange={(e) => update('category', e.target.value)}
          >
            {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-1 block">결제수단</label>
          <select
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            value={form.payment_method || '기타'}
            onChange={(e) => update('payment_method', e.target.value)}
          >
            {PAYMENTS.map((p) => <option key={p}>{p}</option>)}
          </select>
        </div>
      </div>

      {/* 품목 목록 */}
      {form.items?.length > 0 && (
        <div className="mb-4">
          <p className="text-xs text-gray-500 mb-2">품목 목록</p>
          <div className="space-y-2">
            {form.items.map((item, idx) => (
              <div key={idx} className="grid grid-cols-4 gap-2 text-sm">
                <input
                  className="col-span-2 px-2 py-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  value={item.name || ''}
                  onChange={(e) => updateItem(idx, 'name', e.target.value)}
                  placeholder="품목명"
                />
                <input
                  className="px-2 py-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  type="number"
                  value={item.quantity || 0}
                  onChange={(e) => updateItem(idx, 'quantity', e.target.value)}
                  placeholder="수량"
                />
                <input
                  className="px-2 py-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  type="number"
                  value={item.total_price || 0}
                  onChange={(e) => updateItem(idx, 'total_price', e.target.value)}
                  placeholder="금액"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="border-t border-gray-100 pt-3 flex justify-between items-center">
        <span className="text-sm font-semibold text-gray-700">
          합계 <span className="text-xl font-bold text-indigo-600 ml-2">₩{(form.total_amount || 0).toLocaleString()}</span>
        </span>
      </div>

      <div className="flex gap-3 mt-4 justify-end">
        <button
          onClick={onCancel}
          className="bg-white hover:bg-gray-50 text-gray-700 font-semibold py-2 px-4 rounded-lg border border-gray-300 transition-colors text-sm"
        >
          취소
        </button>
        <button
          onClick={() => onSave(form)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors text-sm"
        >
          저장하기
        </button>
      </div>
    </div>
  );
}
