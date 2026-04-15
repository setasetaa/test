export default function SummaryCard({ total, thisMonth, byCategory }) {
  return (
    <div className="grid grid-cols-2 gap-4 mb-6">
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
        <p className="text-xs text-gray-500 mb-1">총 지출</p>
        <p className="text-2xl font-bold text-gray-900">₩{(total || 0).toLocaleString()}</p>
      </div>
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
        <p className="text-xs text-gray-500 mb-1">이번달 지출</p>
        <p className="text-2xl font-bold text-indigo-600">₩{(thisMonth || 0).toLocaleString()}</p>
      </div>
      {byCategory && Object.keys(byCategory).length > 0 && (
        <div className="col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm p-4">
          <p className="text-xs text-gray-500 mb-3">카테고리별 지출</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(byCategory).map(([cat, amount]) => (
              <div key={cat} className="flex items-center gap-1 text-sm">
                <span className="text-gray-600">{cat}</span>
                <span className="font-semibold text-gray-900">₩{amount.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
