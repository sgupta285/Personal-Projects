type InvoiceRow = {
  id: number;
  vendor: string;
  amount: string;
  status: string;
  dueDate: string;
};

export function InvoiceTable({ invoices }: { invoices: InvoiceRow[] }) {
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr style={{ textAlign: 'left', color: '#5d6b82', borderBottom: '1px solid #e8edf5' }}>
          <th style={{ padding: '12px 0' }}>Invoice ID</th>
          <th style={{ padding: '12px 0' }}>Vendor</th>
          <th style={{ padding: '12px 0' }}>Amount</th>
          <th style={{ padding: '12px 0' }}>Status</th>
          <th style={{ padding: '12px 0' }}>Due date</th>
        </tr>
      </thead>
      <tbody>
        {invoices.map((invoice) => (
          <tr key={invoice.id} style={{ borderBottom: '1px solid #eef2f8' }}>
            <td style={{ padding: '14px 0' }}>#{invoice.id}</td>
            <td style={{ padding: '14px 0' }}>{invoice.vendor}</td>
            <td style={{ padding: '14px 0' }}>{invoice.amount}</td>
            <td style={{ padding: '14px 0' }}>{invoice.status}</td>
            <td style={{ padding: '14px 0' }}>{invoice.dueDate}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
