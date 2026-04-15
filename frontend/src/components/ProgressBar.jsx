export default function ProgressBar({ loading }) {
  if (!loading) return null;

  return (
    <div className="my-4">
      <p className="text-sm text-blue-600 font-medium mb-2">OCR 분석 중...</p>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className="h-full bg-indigo-500 rounded-full animate-pulse w-full" />
      </div>
    </div>
  );
}
