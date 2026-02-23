export default function StatsCard({ title, value }) {
  return (
    <div className="glass p-6 rounded-2xl text-center">
      <h3 className="text-slate-400 text-sm">{title}</h3>
      <p className="text-2xl font-semibold mt-2">{value}</p>
    </div>
  );
}
