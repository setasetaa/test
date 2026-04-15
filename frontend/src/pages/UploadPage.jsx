import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadReceipt, updateExpense } from '../api/index.js';
import DropZone from '../components/DropZone.jsx';
import ProgressBar from '../components/ProgressBar.jsx';
import ParsePreview from '../components/ParsePreview.jsx';
import { useToast } from '../components/Toast.jsx';

export default function UploadPage() {
  const navigate = useNavigate();
  const showToast = useToast();
  const [loading, setLoading] = useState(false);
  const [parsed, setParsed] = useState(null);
  const [savedId, setSavedId] = useState(null);

  async function handleFile(file) {
    setLoading(true);
    setParsed(null);
    setSavedId(null);
    try {
      const res = await uploadReceipt(file);
      setParsed(res.data.data);
      setSavedId(res.data.data.id);
      showToast('OCR 파싱이 완료되었습니다.', 'info');
    } catch (e) {
      const msg = e.response?.data?.detail || 'OCR 처리 중 오류가 발생했습니다.';
      showToast(msg, 'error');
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(form) {
    try {
      await updateExpense(savedId, form);
      showToast('지출이 저장되었습니다.', 'success');
      navigate('/');
    } catch (e) {
      showToast('저장 중 오류가 발생했습니다.', 'error');
    }
  }

  return (
    <div>
      <button
        onClick={() => navigate('/')}
        className="text-indigo-600 hover:text-indigo-700 font-medium text-sm mb-6 inline-flex items-center gap-1"
      >
        ← 뒤로
      </button>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">영수증 업로드</h1>

      <DropZone onFile={handleFile} disabled={loading} />
      <ProgressBar loading={loading} />

      {parsed && (
        <ParsePreview
          data={parsed}
          onSave={handleSave}
          onCancel={() => { setParsed(null); setSavedId(null); }}
        />
      )}
    </div>
  );
}
