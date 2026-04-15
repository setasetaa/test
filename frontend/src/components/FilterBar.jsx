import { useState } from 'react';

export default function FilterBar({ onFilter }) {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 mb-6 flex flex-wrap gap-3 items-end">
      <div>
        <label className="text-xs text-gray-500 block mb-1">시작일</label>
        <input
          type="date"
          value={from}
          onChange={(e) => setFrom(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>
      <div>
        <label className="text-xs text-gray-500 block mb-1">종료일</label>
        <input
          type="date"
          value={to}
          onChange={(e) => setTo(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>
      <button
        onClick={() => onFilter({ from, to })}
        className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors text-sm"
      >
        조회
      </button>
      <button
        onClick={() => { setFrom(''); setTo(''); onFilter({}); }}
        className="bg-white hover:bg-gray-50 text-gray-700 font-semibold py-2 px-4 rounded-lg border border-gray-300 transition-colors text-sm"
      >
        초기화
      </button>
    </div>
  );
}
