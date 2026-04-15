import { useRef, useState } from 'react';

const ALLOWED = ['image/jpeg', 'image/png', 'application/pdf'];
const MAX_SIZE = 10 * 1024 * 1024;

export default function DropZone({ onFile, disabled }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState('');

  function validate(file) {
    if (!ALLOWED.includes(file.type)) {
      setError('JPG, PNG, PDF 파일만 업로드 가능합니다.');
      return false;
    }
    if (file.size > MAX_SIZE) {
      setError('파일 크기는 10MB를 초과할 수 없습니다.');
      return false;
    }
    setError('');
    return true;
  }

  function handleFiles(files) {
    const file = files[0];
    if (file && validate(file)) onFile(file);
  }

  return (
    <div>
      <div
        onClick={() => !disabled && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          if (!disabled) handleFiles(e.dataTransfer.files);
        }}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors duration-200
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          ${dragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 bg-gray-50 hover:border-indigo-400 hover:bg-indigo-50'}`}
      >
        <div className="text-4xl mb-3">↑</div>
        <p className="text-base font-semibold text-gray-700 mb-1">
          영수증을 드래그하거나 클릭하여 업로드하세요
        </p>
        <p className="text-xs text-gray-400">JPG, PNG, PDF · 최대 10MB</p>
        <input
          ref={inputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.pdf"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
          disabled={disabled}
        />
      </div>
      {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
    </div>
  );
}
