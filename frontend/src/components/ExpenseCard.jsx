import { useNavigate } from 'react-router-dom';
import Badge from './Badge.jsx';

export default function ExpenseCard({ expense }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/expense/${expense.id}`)}
      className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200 p-4 cursor-pointer"
    >
      <div className="flex items-start justify-between mb-2">
        <Badge category={expense.category} />
        <span className="text-xs text-gray-400">{expense.receipt_date || '-'}</span>
      </div>
      <p className="text-base font-semibold text-gray-900 mb-1 truncate">
        {expense.store_name || '상호명 없음'}
      </p>
      <p className="text-xl font-bold text-indigo-600">
        ₩{(expense.total_amount || 0).toLocaleString()}
      </p>
      {expense.payment_method && (
        <p className="text-xs text-gray-400 mt-1">{expense.payment_method}</p>
      )}
    </div>
  );
}
