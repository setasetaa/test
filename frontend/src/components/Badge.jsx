const COLOR_MAP = {
  식비: 'bg-orange-100 text-orange-700',
  식료품: 'bg-green-100 text-green-700',
  외식: 'bg-orange-100 text-orange-700',
  교통: 'bg-blue-100 text-blue-700',
  쇼핑: 'bg-purple-100 text-purple-700',
  의료: 'bg-red-100 text-red-700',
  문화: 'bg-amber-100 text-amber-700',
  기타: 'bg-gray-100 text-gray-700',
};

export default function Badge({ category }) {
  const color = COLOR_MAP[category] ?? COLOR_MAP['기타'];
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {category || '기타'}
    </span>
  );
}
