import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getExpenses, updateExpense, deleteExpense } from '../api/index.js';
import Badge from '../components/Badge.jsx';
import Modal from '../components/Modal.jsx';
import { useToast } from '../components/Toast.jsx';

const CATEGORIES = ['식비', '식료품', '외식', '교통', '쇼핑', '의료', '문화', '기타'];
const PAYMENTS = ['카드', '현금', '모바일페이', '기타'];

export default function ExpenseDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const showToast = useToast();
  const [expense, setExpense] = useState(null);
  const [form, setForm] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    getExpenses().then((res) => {
      const found = (res.data.data || []).find((e) => e.id === id);
      if (found) { setExpense(found); setForm(found); }
      else navigate('/');
    });
  }, [id]);

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSave() {
    try {
      await updateExpense(id, form);
      showToast('수정이 저장되었습니다.', 'success');
      navigate('/');
    } catch {
      showToast('저장 중 오류가 발생했습니다.', 'error');
    }
  }

  async function handleDelete() {
    try {
      await deleteExpense(id);
      showToast('지출이 삭제되었습니다.', 'success');
      navigate('/');
    } catch {
      showToast('삭제 중 오류가 발생했습니다.', 'error');
    }
  }

  if (!form) return <div className="text-center py-16 text-gray-400">불러오는 중...</div>;

  return (
    <div>
      <button
        onClick={() => navigate('/')}
        className="text-indigo-600 hover:text-indigo-700 font-medium text-sm mb-6 inline-flex items-center gap-1"
      >
        ← 뒤로
      </button>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">지출 상세</h1>

      {/* 영수증 이미지 */}
      {expense?.raw_image_path && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 mb-4">
          <img
            src={`/${expense.raw_image_path}`}
            alt="영수증"
            className="max-h-72 mx-auto object-contain rounded-lg"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
        </div>
      )}

      {/* 수정 폼 */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
        <div className="flex items-center gap-2 mb-4">
          <Badge category={form.category} />
          <span className="text-base font-semibold text-gray-900">{form.store_name}</span>
        </div>

        <div className="border-t border-gray-100 pt-4 grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">가게명</label>
            <input
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.store_name || ''}
              onChange={(e) => update('store_name', e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">날짜</label>
            <input
              type="date"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.receipt_date || ''}
              onChange={(e) => update('receipt_date', e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">카테고리</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.category || '기타'}
              onChange={(e) => update('category', e.target.value)}
            >
              {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">결제수단</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.payment_method || '기타'}
              onChange={(e) => update('payment_method', e.target.value)}
            >
              {PAYMENTS.map((p) => <option key={p}>{p}</option>)}
            </select>
          </div>
        </div>

        {/* 품목 목록 */}
        {form.items?.length > 0 && (
          <div className="mt-4 border-t border-gray-100 pt-4">
            <p className="text-xs text-gray-500 mb-2">품목 목록</p>
            <div className="space-y-1">
              {form.items.map((item, i) => (
                <div key={i} className="flex justify-between text-sm text-gray-700">
                  <span>{item.name} x{item.quantity}</span>
                  <span>₩{(item.total_price || 0).toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-gray-100 pt-3 mt-3 flex justify-between items-center">
          <span className="text-sm text-gray-500">합계</span>
          <span className="text-xl font-bold text-indigo-600">₩{(form.total_amount || 0).toLocaleString()}</span>
        </div>

        <div className="flex gap-3 mt-5 justify-between">
          <button
            onClick={() => setShowModal(true)}
            className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors text-sm"
          >
            삭제
          </button>
          <button
            onClick={handleSave}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors text-sm"
          >
            수정 저장
          </button>
        </div>
      </div>

      <Modal
        isOpen={showModal}
        title="지출 삭제"
        message="이 지출 항목을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."
        onConfirm={handleDelete}
        onCancel={() => setShowModal(false)}
      />
    </div>
  );
}
