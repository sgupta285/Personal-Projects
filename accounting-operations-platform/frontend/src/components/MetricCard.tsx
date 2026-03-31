export function MetricCard({ label, value, helper }: { label: string; value: string; helper: string }) {
  return (
    <div style={{ background: 'white', borderRadius: 16, padding: 20, boxShadow: '0 10px 30px rgba(20,30,55,0.06)' }}>
      <div style={{ color: '#6f7f96', fontSize: 14 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, marginTop: 8 }}>{value}</div>
      <div style={{ color: '#6f7f96', marginTop: 8, lineHeight: 1.5 }}>{helper}</div>
    </div>
  );
}
