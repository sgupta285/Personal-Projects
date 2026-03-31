import { InvoiceTable } from './components/InvoiceTable';
import { MetricCard } from './components/MetricCard';

const sampleInvoices = [
  { id: 104, vendor: 'North Ridge Supply', amount: '$1,825.45', status: 'approved', dueDate: '2026-03-31' },
  { id: 105, vendor: 'Bayside Office Goods', amount: '$120.00', status: 'pending_review', dueDate: '2026-03-20' },
  { id: 106, vendor: 'Harbor Electric', amount: '$2,500.00', status: 'scheduled_for_payment', dueDate: '2026-03-29' },
];

export default function App() {
  return (
    <div style={{ fontFamily: 'Inter, Arial, sans-serif', background: '#f7f8fb', minHeight: '100vh', color: '#18212f' }}>
      <header style={{ padding: '32px 40px 12px' }}>
        <h1 style={{ margin: 0, fontSize: '2rem' }}>Accounting Operations Platform</h1>
        <p style={{ marginTop: 10, maxWidth: 760, lineHeight: 1.6 }}>
          Internal finance workspace for invoice intake, approvals, payment scheduling, and audit visibility.
        </p>
      </header>

      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 16, padding: '0 40px 24px' }}>
        <MetricCard label="Open liability" value="$4,445.45" helper="Pending, approved, and scheduled invoices" />
        <MetricCard label="Awaiting review" value="3" helper="Invoices still in triage" />
        <MetricCard label="Paid this week" value="$7,920.00" helper="Completed remittances" />
      </section>

      <main style={{ padding: '0 40px 40px' }}>
        <div style={{ background: 'white', borderRadius: 16, padding: 24, boxShadow: '0 10px 30px rgba(20,30,55,0.06)' }}>
          <h2 style={{ marginTop: 0 }}>Recent invoices</h2>
          <InvoiceTable invoices={sampleInvoices} />
        </div>
      </main>
    </div>
  );
}
