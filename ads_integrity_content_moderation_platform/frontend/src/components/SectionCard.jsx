export function SectionCard({ title, children }) {
  return (
    <section className="section-card">
      <div className="section-head">
        <h3>{title}</h3>
      </div>
      {children}
    </section>
  );
}
