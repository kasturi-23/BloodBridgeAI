export default function ChartCard({ title, children }) {
  return (
    <div className="card p-4">
      <h3 className="mb-3 text-sm font-semibold text-slate-700">{title}</h3>
      <div className="h-64">{children}</div>
    </div>
  );
}
