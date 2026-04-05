export default function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="flex items-center gap-2 py-8 text-sm text-slate-500">
      <div className="h-4 w-4 animate-spin rounded-full border-2 border-accent border-t-transparent" />
      {label}
    </div>
  );
}
