import { useEffect, useMemo, useState } from "react";
import { StatCard } from "./components/StatCard";
import { SectionCard } from "./components/SectionCard";
import { RiskBadge } from "./components/RiskBadge";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export default function App() {
  const [overview, setOverview] = useState(null);
  const [advertisers, setAdvertisers] = useState([]);
  const [patterns, setPatterns] = useState({ policy_hits: [], categories: [], recent_volume: [] });
  const [ads, setAds] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [overviewRes, advertiserRes, patternRes, adsRes] = await Promise.all([
          fetch(`${API_BASE}/analytics/overview`),
          fetch(`${API_BASE}/analytics/advertisers`),
          fetch(`${API_BASE}/analytics/fraud-patterns`),
          fetch(`${API_BASE}/ads?limit=15`)
        ]);

        setOverview(await overviewRes.json());
        setAdvertisers(await advertiserRes.json());
        setPatterns(await patternRes.json());
        setAds(await adsRes.json());
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setLoading(false);
      }
    }

    load();
    const timer = setInterval(load, 5000);
    return () => clearInterval(timer);
  }, []);

  const reviewRate = useMemo(() => {
    if (!overview || !overview.total_ads) return 0;
    return Math.round(((overview.in_review_ads + overview.blocked_ads) / overview.total_ads) * 100);
  }, [overview]);

  return (
    <div className="page-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Trust & Safety / Ads Integrity</p>
          <h1>Ads Integrity Dashboard</h1>
          <p className="subcopy">
            Live moderation view for flagged creatives, advertiser risk, and policy-hit patterns.
          </p>
        </div>
        <div className="hero-pill">Event-driven moderation with Kafka + Redis + Postgres</div>
      </header>

      {loading && <p className="loading">Refreshing metrics…</p>}

      <section className="stats-grid">
        <StatCard label="Total Ads" value={overview?.total_ads ?? 0} />
        <StatCard label="Approved" value={overview?.approved_ads ?? 0} accent="green" />
        <StatCard label="Blocked" value={overview?.blocked_ads ?? 0} accent="red" />
        <StatCard label="In Review" value={overview?.in_review_ads ?? 0} accent="amber" />
        <StatCard label="Avg Risk" value={overview?.average_risk_score ?? 0} />
        <StatCard label="Review Rate" value={`${reviewRate}%`} />
      </section>

      <section className="two-col">
        <SectionCard title="Top Policy Hits">
          <div className="stack">
            {patterns.policy_hits.length === 0 && <p className="muted">No policy hits yet.</p>}
            {patterns.policy_hits.map((item) => (
              <BarRow key={item.label} label={item.label} value={item.count} />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Highest-Risk Advertisers">
          <div className="stack">
            {advertisers.length === 0 && <p className="muted">No advertisers yet.</p>}
            {advertisers.slice(0, 6).map((item) => (
              <div className="advertiser-row" key={`${item.advertiser_name}-${item.advertiser_domain}`}>
                <div>
                  <strong>{item.advertiser_name}</strong>
                  <p>{item.advertiser_domain}</p>
                </div>
                <div className="row-end">
                  <RiskBadge score={item.average_risk_score} />
                  <span className="tiny-meta">{item.blocked_ads}/{item.total_ads} blocked</span>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      </section>

      <section className="two-col">
        <SectionCard title="Status by Category">
          <div className="stack">
            {patterns.categories.length === 0 && <p className="muted">Waiting for moderation data.</p>}
            {patterns.categories.map((item) => (
              <BarRow key={item.label} label={item.label} value={item.count} compact />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Daily Submission Volume">
          <div className="stack">
            {patterns.recent_volume.length === 0 && <p className="muted">No submissions yet.</p>}
            {patterns.recent_volume.map((item) => (
              <BarRow key={item.date} label={item.date} value={item.count} compact />
            ))}
          </div>
        </SectionCard>
      </section>

      <SectionCard title="Recent Ads">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Category</th>
                <th>Status</th>
                <th>Risk</th>
                <th>Policy Hits</th>
              </tr>
            </thead>
            <tbody>
              {ads.map((ad) => (
                <tr key={ad.id}>
                  <td>
                    <div className="table-title">{ad.title}</div>
                    <div className="table-subcopy">{ad.body.slice(0, 90)}{ad.body.length > 90 ? "…" : ""}</div>
                  </td>
                  <td>{ad.category}</td>
                  <td><span className={`status status-${ad.status}`}>{ad.status}</span></td>
                  <td><RiskBadge score={ad.risk_score} /></td>
                  <td>
                    <div className="policy-list">
                      {(ad.policy_hits || []).length === 0 ? "none" : ad.policy_hits.join(", ")}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </div>
  );
}

function BarRow({ label, value, compact = false }) {
  const width = Math.min(100, value * 12 + 10);
  return (
    <div className={`bar-row ${compact ? "compact" : ""}`}>
      <div className="bar-row-head">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}
