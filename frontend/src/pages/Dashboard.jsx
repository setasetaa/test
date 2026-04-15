import { useEffect, useState } from 'react';
import { getExpenses, getSummary } from '../api/index.js';
import SummaryCard from '../components/SummaryCard.jsx';
import FilterBar from '../components/FilterBar.jsx';
import ExpenseCard from '../components/ExpenseCard.jsx';

export default function Dashboard() {
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState({});
  const [thisMonth, setThisMonth] = useState(0);
  const [loading, setLoading] = useState(true);

  const currentMonth = new Date().toISOString().slice(0, 7);

  async function fetchData(params = {}) {
    setLoading(true);
    try {
      const [expRes, sumRes, monthRes] = await Promise.all([
        getExpenses(params),
        getSummary(),
        getSummary(currentMonth),
      ]);
      setExpenses(expRes.data.data || []);
      setSummary(sumRes.data);
      setThisMonth(monthRes.data.총_지출 || 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchData(); }, []);

  function handleFilter({ from, to }) {
    const params = {};
    if (from) params.from = from;
    if (to) params.to = to;
    fetchData(params);
  }

  return (
    <div>
      <SummaryCard
        total={summary.총_지출 || 0}
        thisMonth={thisMonth}
        byCategory={summary.카테고리별 || {}}
      />
      <FilterBar onFilter={handleFilter} />

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          지출 내역
          {!loading && (
            <span className="text-sm font-normal text-gray-400 ml-2">
              ({expenses.length}건)
            </span>
          )}
        </h2>
      </div>

      {loading ? (
        <div className="text-center py-16 text-gray-400">불러오는 중...</div>
      ) : expenses.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">🧾</div>
          <p className="text-gray-500 font-medium mb-1">등록된 지출 내역이 없습니다</p>
          <p className="text-sm text-gray-400">영수증을 업로드하여 지출을 기록해 보세요</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {expenses.map((exp) => (
            <ExpenseCard key={exp.id} expense={exp} />
          ))}
        </div>
      )}
    </div>
  );
}
