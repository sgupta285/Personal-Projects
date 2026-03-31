import { useState, useEffect, useRef, useCallback } from "react";
import { Upload, FileText, Shield, AlertTriangle, CheckCircle, ChevronRight, ChevronDown, Search, Download, Eye, X, Zap, Lock, BookOpen, ArrowRight, Star, Clock, BarChart3, Menu, LogOut } from "lucide-react";

/* ─── ClearCause MVP ─── AI-Powered Contract Clarity ─── */

// ─── SIMULATED ANALYSIS ENGINE ───
const CLAUSE_LIBRARY = {
  arbitration: {
    label: "Binding Arbitration",
    risk: "high",
    icon: "⚖️",
    description: "Waives your right to sue in court or join class-action lawsuits.",
    what_to_ask: "Can I opt out of arbitration within 30 days? Is there a small-claims court exception?",
    section: "§ 14.2",
    original: "Any dispute arising out of or relating to this Agreement shall be resolved exclusively through binding arbitration administered by the American Arbitration Association, and you agree to waive any right to participate in a class-action lawsuit or class-wide arbitration."
  },
  auto_renewal: {
    label: "Auto-Renewal",
    risk: "medium",
    icon: "🔄",
    description: "Your subscription renews automatically unless you cancel before the renewal date.",
    what_to_ask: "What is the exact cancellation deadline? Will I receive a reminder before renewal?",
    section: "§ 3.4",
    original: "This Agreement shall automatically renew for successive one-year terms unless either party provides written notice of non-renewal at least thirty (30) days prior to the expiration of the then-current term."
  },
  liability_cap: {
    label: "Liability Limitation",
    risk: "high",
    icon: "🛡️",
    description: "Limits the maximum amount you can recover in damages, often to what you paid in the last 12 months.",
    what_to_ask: "Does this cap apply to data breaches or negligence? Are there exceptions for gross misconduct?",
    section: "§ 11.1",
    original: "In no event shall Company's total aggregate liability exceed the amounts actually paid by you to Company in the twelve (12) month period preceding the claim. Company shall not be liable for any indirect, incidental, special, consequential, or punitive damages."
  },
  data_sharing: {
    label: "Data Sharing with Third Parties",
    risk: "medium",
    icon: "📡",
    description: "Your data may be shared with advertising partners, analytics providers, and affiliated companies.",
    what_to_ask: "Can I opt out of third-party data sharing? What data is shared and with whom specifically?",
    section: "§ 7.3",
    original: "We may share your personal information with our trusted partners, including advertising networks, analytics providers, and affiliated entities, to improve our services and deliver personalized content and advertisements."
  },
  unilateral_changes: {
    label: "Unilateral Modification",
    risk: "high",
    icon: "✏️",
    description: "The company can change terms at any time without your explicit consent. Continued use = acceptance.",
    what_to_ask: "Will I be notified of material changes? Can I terminate if I disagree with new terms?",
    section: "§ 2.1",
    original: "Company reserves the right to modify these Terms at any time in its sole discretion. Your continued use of the Service after any such modifications constitutes your acceptance of the revised Terms."
  },
  termination: {
    label: "Termination Without Cause",
    risk: "medium",
    icon: "🚪",
    description: "Either party can terminate the agreement at any time with just 15 days notice, with no refund for prepaid amounts.",
    what_to_ask: "Is there a pro-rated refund if terminated mid-cycle? What happens to my data after termination?",
    section: "§ 9.2",
    original: "Either party may terminate this Agreement for any reason upon fifteen (15) days' prior written notice. Upon termination, all prepaid fees are non-refundable and your access to the Service will be immediately suspended."
  },
  ip_assignment: {
    label: "IP & Content Rights",
    risk: "low",
    icon: "©️",
    description: "You retain ownership of your content, but grant a broad license for the company to use it.",
    what_to_ask: "Is the license revocable? Does it survive termination of the agreement?",
    section: "§ 6.1",
    original: "You retain all ownership rights in your content. By submitting content, you grant Company a worldwide, non-exclusive, royalty-free license to use, reproduce, modify, and display such content in connection with the Service."
  },
  indemnification: {
    label: "Indemnification Clause",
    risk: "medium",
    icon: "🔒",
    description: "You agree to cover the company's legal costs if your use of the service leads to a lawsuit.",
    what_to_ask: "Is indemnification mutual? Are there caps on indemnification liability?",
    section: "§ 12.1",
    original: "You agree to indemnify, defend, and hold harmless Company and its officers, directors, employees, and agents from and against any claims, damages, losses, liabilities, costs, and expenses arising from your use of the Service or violation of these Terms."
  }
};

function simulateAnalysis(fileName) {
  const clauseKeys = Object.keys(CLAUSE_LIBRARY);
  const numClauses = 5 + Math.floor(Math.random() * 3);
  const selected = clauseKeys.sort(() => Math.random() - 0.5).slice(0, numClauses);
  const clauses = selected.map(k => ({ id: k, ...CLAUSE_LIBRARY[k] }));
  
  const highCount = clauses.filter(c => c.risk === "high").length;
  const medCount = clauses.filter(c => c.risk === "medium").length;
  const overallRisk = highCount >= 3 ? "high" : highCount >= 1 ? "medium" : "low";
  const riskScore = Math.min(100, highCount * 28 + medCount * 14 + clauses.length * 3);

  return {
    fileName,
    analyzedAt: new Date().toLocaleString(),
    documentType: ["SaaS Agreement", "Terms of Service", "Lease Agreement", "Service Contract"][Math.floor(Math.random() * 4)],
    pageCount: 12 + Math.floor(Math.random() * 20),
    readingLevel: "College-level (Grade 14+)",
    simplifiedLevel: "8th Grade",
    overallRisk,
    riskScore,
    clauses,
    summary: `This ${fileName.replace('.pdf', '')} contains ${clauses.length} notable clauses that affect your rights. ${highCount} are flagged as high-risk, meaning they significantly limit your legal options or expose you to unexpected obligations. Key concerns include ${clauses.filter(c => c.risk === 'high').map(c => c.label.toLowerCase()).join(', ')}. We recommend reviewing these sections carefully before signing.`,
    recommendations: [
      highCount > 0 ? "Negotiate or request removal of binding arbitration clauses" : "Terms are relatively standard",
      "Request a data processing addendum (DPA) before sharing sensitive information",
      "Set calendar reminders for auto-renewal deadlines",
      "Ask for mutual indemnification rather than one-sided obligations",
      "Request a 30-day written notice requirement for any term modifications"
    ].slice(0, 3 + Math.floor(Math.random() * 2))
  };
}

// ─── RISK BADGE ───
function RiskBadge({ risk, size = "sm" }) {
  const colors = {
    high: "bg-red-500/15 text-red-400 border-red-500/30",
    medium: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    low: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
  };
  const icons = { high: <AlertTriangle size={size === "lg" ? 16 : 12} />, medium: <Shield size={size === "lg" ? 16 : 12} />, low: <CheckCircle size={size === "lg" ? 16 : 12} /> };
  const sz = size === "lg" ? "px-3 py-1.5 text-sm" : "px-2 py-0.5 text-xs";
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-semibold uppercase tracking-wider ${colors[risk]} ${sz}`}>
      {icons[risk]} {risk}
    </span>
  );
}

// ─── RISK SCORE RING ───
function RiskRing({ score, size = 120 }) {
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score >= 70 ? "#ef4444" : score >= 40 ? "#f59e0b" : "#10b981";
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="8" strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round" className="transition-all duration-1000 ease-out" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-white">{score}</span>
        <span className="text-xs text-gray-400 uppercase tracking-widest">Risk</span>
      </div>
    </div>
  );
}

// ─── CLAUSE CARD ───
function ClauseCard({ clause, index }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="group rounded-xl border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] transition-all duration-300" style={{ animationDelay: `${index * 80}ms` }}>
      <button onClick={() => setExpanded(!expanded)} className="w-full p-5 text-left flex items-start gap-4">
        <span className="text-2xl mt-0.5 shrink-0">{clause.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h3 className="font-semibold text-white text-base">{clause.label}</h3>
            <RiskBadge risk={clause.risk} />
            <span className="text-xs text-gray-500 font-mono">{clause.section}</span>
          </div>
          <p className="text-sm text-gray-400 mt-2 leading-relaxed">{clause.description}</p>
        </div>
        <div className="shrink-0 text-gray-500 group-hover:text-gray-300 transition-colors mt-1">
          {expanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
        </div>
      </button>
      {expanded && (
        <div className="px-5 pb-5 space-y-4 border-t border-white/[0.04] pt-4 mx-5">
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2 flex items-center gap-1.5">
              <BookOpen size={12} /> Original Text
            </h4>
            <p className="text-sm text-gray-400 bg-white/[0.03] rounded-lg p-3 border-l-2 border-gray-600 leading-relaxed italic">
              "{clause.original}"
            </p>
          </div>
          <div className="bg-teal-500/[0.06] rounded-lg p-4 border border-teal-500/20">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-teal-400 mb-2 flex items-center gap-1.5">
              <Zap size={12} /> What to Ask
            </h4>
            <p className="text-sm text-teal-300/90 leading-relaxed">{clause.what_to_ask}</p>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── UPLOAD ZONE ───
function UploadZone({ onAnalyze, isAnalyzing }) {
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef(null);

  const handleFile = useCallback((file) => {
    if (file) onAnalyze(file.name || "document.pdf");
  }, [onAnalyze]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer?.files?.[0];
    handleFile(file);
  }, [handleFile]);

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => fileRef.current?.click()}
      className={`relative cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-300 p-12 text-center group
        ${dragOver
          ? "border-teal-400 bg-teal-400/[0.06] scale-[1.01]"
          : "border-white/10 hover:border-white/20 bg-white/[0.02] hover:bg-white/[0.04]"
        } ${isAnalyzing ? "pointer-events-none opacity-60" : ""}`}
    >
      <input ref={fileRef} type="file" accept=".pdf" className="hidden" onChange={(e) => handleFile(e.target.files?.[0])} />
      <div className="flex flex-col items-center gap-4">
        {isAnalyzing ? (
          <>
            <div className="w-16 h-16 rounded-2xl bg-teal-500/10 flex items-center justify-center">
              <div className="w-8 h-8 border-2 border-teal-400/30 border-t-teal-400 rounded-full animate-spin" />
            </div>
            <div>
              <p className="text-lg font-semibold text-white">Analyzing your contract...</p>
              <p className="text-sm text-gray-400 mt-1">Detecting clauses, scoring risks, generating summaries</p>
            </div>
            <div className="w-64 h-1.5 bg-white/[0.06] rounded-full overflow-hidden mt-2">
              <div className="h-full bg-gradient-to-r from-teal-500 to-cyan-400 rounded-full animate-pulse" style={{ width: "60%" }} />
            </div>
          </>
        ) : (
          <>
            <div className="w-16 h-16 rounded-2xl bg-white/[0.04] group-hover:bg-teal-500/10 flex items-center justify-center transition-colors">
              <Upload size={28} className="text-gray-400 group-hover:text-teal-400 transition-colors" />
            </div>
            <div>
              <p className="text-lg font-semibold text-white">Upload a contract to analyze</p>
              <p className="text-sm text-gray-400 mt-1">Drag & drop a PDF or click to browse — leases, ToS, SaaS agreements</p>
            </div>
            <div className="flex gap-2 mt-2">
              {["PDF", "DOCX", "TXT"].map(f => (
                <span key={f} className="text-xs px-2.5 py-1 rounded-md bg-white/[0.04] text-gray-500 border border-white/[0.06]">{f}</span>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ─── DEMO FILE PICKER ───
function DemoFiles({ onSelect }) {
  const demos = [
    { name: "Netflix_Terms_of_Use.pdf", type: "Terms of Service", pages: 18 },
    { name: "Standard_Apartment_Lease.pdf", type: "Lease Agreement", pages: 24 },
    { name: "Slack_Enterprise_SaaS.pdf", type: "SaaS Agreement", pages: 31 },
    { name: "Freelancer_Service_Contract.pdf", type: "Service Contract", pages: 8 },
  ];
  return (
    <div className="mt-6">
      <p className="text-xs uppercase tracking-widest text-gray-500 mb-3 text-center">Or try a sample document</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {demos.map(d => (
          <button key={d.name} onClick={() => onSelect(d.name)}
            className="flex items-center gap-3 p-3 rounded-xl border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.05] transition-all text-left group">
            <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center shrink-0">
              <FileText size={18} className="text-red-400" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-200 truncate">{d.name}</p>
              <p className="text-xs text-gray-500">{d.type} · {d.pages} pages</p>
            </div>
            <ArrowRight size={14} className="text-gray-600 group-hover:text-teal-400 transition-colors shrink-0 ml-auto" />
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── REPORT VIEW ───
function ReportView({ report, onBack }) {
  const [activeTab, setActiveTab] = useState("overview");
  const tabs = [
    { id: "overview", label: "Overview", icon: <BarChart3 size={14} /> },
    { id: "clauses", label: `Clauses (${report.clauses.length})`, icon: <Search size={14} /> },
    { id: "actions", label: "Action Items", icon: <Zap size={14} /> },
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <button onClick={onBack} className="text-sm text-gray-400 hover:text-white transition-colors mb-3 flex items-center gap-1">
            ← Back to upload
          </button>
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <FileText size={24} className="text-teal-400" />
            {report.fileName}
          </h2>
          <div className="flex items-center gap-4 mt-2 text-sm text-gray-400 flex-wrap">
            <span>{report.documentType}</span>
            <span className="text-gray-600">·</span>
            <span>{report.pageCount} pages</span>
            <span className="text-gray-600">·</span>
            <span>Analyzed {report.analyzedAt}</span>
          </div>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-teal-500/10 border border-teal-500/30 text-teal-400 text-sm font-medium hover:bg-teal-500/20 transition-colors">
          <Download size={14} /> Export PDF
        </button>
      </div>

      {/* Risk Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="md:col-span-1 flex items-center justify-center p-6 rounded-xl border border-white/[0.06] bg-white/[0.02]">
          <RiskRing score={report.riskScore} />
        </div>
        <div className="md:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { label: "High Risk", count: report.clauses.filter(c => c.risk === "high").length, color: "red", icon: <AlertTriangle size={18} /> },
            { label: "Medium Risk", count: report.clauses.filter(c => c.risk === "medium").length, color: "amber", icon: <Shield size={18} /> },
            { label: "Low Risk", count: report.clauses.filter(c => c.risk === "low").length, color: "emerald", icon: <CheckCircle size={18} /> },
          ].map(item => (
            <div key={item.label} className="p-5 rounded-xl border border-white/[0.06] bg-white/[0.02]">
              <div className={`text-${item.color}-400 mb-3`}>{item.icon}</div>
              <p className="text-3xl font-bold text-white">{item.count}</p>
              <p className="text-sm text-gray-400 mt-1">{item.label} Clauses</p>
            </div>
          ))}
        </div>
      </div>

      {/* Reading Level */}
      <div className="p-5 rounded-xl border border-white/[0.06] bg-white/[0.02] flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <BookOpen size={20} className="text-teal-400 shrink-0" />
        <div className="flex-1">
          <p className="text-sm font-medium text-white">Reading Level Transformation</p>
          <p className="text-sm text-gray-400 mt-1">
            Original: <span className="text-red-400 font-medium">{report.readingLevel}</span>
            <span className="mx-2">→</span>
            Simplified: <span className="text-emerald-400 font-medium">{report.simplifiedLevel}</span>
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-lg bg-white/[0.03] border border-white/[0.06]">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-md text-sm font-medium transition-all
              ${activeTab === t.id ? "bg-white/[0.08] text-white" : "text-gray-400 hover:text-gray-200"}`}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="space-y-4">
          <div className="p-6 rounded-xl border border-white/[0.06] bg-white/[0.02]">
            <h3 className="text-base font-semibold text-white mb-3">Plain Language Summary</h3>
            <p className="text-sm text-gray-300 leading-relaxed">{report.summary}</p>
          </div>
          <div className="p-6 rounded-xl border border-teal-500/20 bg-teal-500/[0.04]">
            <h3 className="text-base font-semibold text-teal-300 mb-3 flex items-center gap-2">
              <Star size={16} /> Key Recommendations
            </h3>
            <div className="space-y-2.5">
              {report.recommendations.map((r, i) => (
                <div key={i} className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-teal-500/20 flex items-center justify-center text-xs font-bold text-teal-300 shrink-0 mt-0.5">{i + 1}</span>
                  <p className="text-sm text-gray-300 leading-relaxed">{r}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === "clauses" && (
        <div className="space-y-3">
          {report.clauses.map((clause, i) => (
            <ClauseCard key={clause.id} clause={clause} index={i} />
          ))}
        </div>
      )}

      {activeTab === "actions" && (
        <div className="space-y-4">
          <div className="p-6 rounded-xl border border-white/[0.06] bg-white/[0.02]">
            <h3 className="text-base font-semibold text-white mb-4">Negotiation Checklist</h3>
            <div className="space-y-3">
              {report.clauses.filter(c => c.risk !== "low").map((clause, i) => (
                <label key={clause.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-white/[0.02] transition-colors cursor-pointer">
                  <input type="checkbox" className="mt-1 accent-teal-400 w-4 h-4 rounded" />
                  <div>
                    <p className="text-sm font-medium text-white">{clause.icon} {clause.label} <span className="text-xs text-gray-500 font-mono ml-1">{clause.section}</span></p>
                    <p className="text-sm text-teal-400/80 mt-1">{clause.what_to_ask}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
          <div className="p-6 rounded-xl border border-amber-500/20 bg-amber-500/[0.04]">
            <h3 className="text-base font-semibold text-amber-300 mb-2 flex items-center gap-2">
              <Clock size={16} /> Important Deadlines
            </h3>
            <p className="text-sm text-gray-300 leading-relaxed">
              Review auto-renewal and cancellation windows. Set reminders at least 45 days before any renewal date to ensure you have time to negotiate or cancel.
            </p>
          </div>
          <p className="text-xs text-gray-500 text-center italic">
            ⚠️ This analysis is for informational purposes only and does not constitute legal advice. Consult an attorney for your specific situation.
          </p>
        </div>
      )}
    </div>
  );
}

// ─── LANDING / HERO ───
function Hero({ onGetStarted }) {
  return (
    <div className="text-center max-w-3xl mx-auto py-16 animate-fadeIn">
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-xs font-semibold uppercase tracking-wider mb-8">
        <Zap size={12} /> AI-Powered Contract Analysis
      </div>
      <h1 className="text-5xl sm:text-6xl font-bold text-white leading-tight tracking-tight">
        Understand any<br />
        <span className="bg-gradient-to-r from-teal-400 via-cyan-400 to-teal-300 bg-clip-text text-transparent">
          contract in seconds
        </span>
      </h1>
      <p className="text-lg text-gray-400 mt-6 max-w-xl mx-auto leading-relaxed">
        Upload a lease, Terms of Service, or SaaS agreement. Get plain-language summaries, risk scores, and negotiation prompts — no law degree required.
      </p>
      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-10">
        <button onClick={onGetStarted}
          className="px-8 py-3.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-black font-semibold text-base transition-all hover:shadow-lg hover:shadow-teal-500/20">
          Analyze a Contract
        </button>
        <button className="px-8 py-3.5 rounded-xl border border-white/10 hover:border-white/20 text-gray-300 hover:text-white font-medium text-base transition-all">
          See How It Works
        </button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-16">
        {[
          { icon: <Shield size={22} />, title: "Risk Scoring", desc: "Every clause rated Low, Medium, or High with explanations" },
          { icon: <BookOpen size={22} />, title: "8th Grade Summaries", desc: "Complex legalese translated into plain language anyone can understand" },
          { icon: <Lock size={22} />, title: "Citation-Verified", desc: "Every claim links to exact sections — zero hallucinations" },
        ].map(f => (
          <div key={f.title} className="p-6 rounded-xl border border-white/[0.06] bg-white/[0.02] text-left">
            <div className="text-teal-400 mb-3">{f.icon}</div>
            <h3 className="text-base font-semibold text-white">{f.title}</h3>
            <p className="text-sm text-gray-400 mt-2 leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── MAIN APP ───
export default function ClearCauseApp() {
  const [view, setView] = useState("home"); // home | analyze | report
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [report, setReport] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const startAnalysis = useCallback((fileName) => {
    setIsAnalyzing(true);
    setView("analyze");
    setTimeout(() => {
      const result = simulateAnalysis(fileName);
      setReport(result);
      setIsAnalyzing(false);
      setView("report");
    }, 2800);
  }, []);

  return (
    <div className="min-h-screen bg-[#0a0e17] text-gray-100" style={{
      backgroundImage: "radial-gradient(ellipse at 20% 0%, rgba(20,184,166,0.06) 0%, transparent 50%), radial-gradient(ellipse at 80% 100%, rgba(6,82,130,0.08) 0%, transparent 50%)"
    }}>
      {/* Nav */}
      <nav className="border-b border-white/[0.06] bg-[#0a0e17]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => { setView("home"); setReport(null); }}>
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-400 to-cyan-500 flex items-center justify-center">
              <Shield size={16} className="text-black" />
            </div>
            <span className="text-lg font-bold tracking-tight text-white">ClearCause</span>
          </div>
          <div className="hidden sm:flex items-center gap-6 text-sm">
            <button className="text-gray-400 hover:text-white transition-colors">How it works</button>
            <button className="text-gray-400 hover:text-white transition-colors">Pricing</button>
            <button onClick={() => setView("analyze")} className="px-4 py-2 rounded-lg bg-white/[0.06] hover:bg-white/[0.1] text-white font-medium transition-colors">
              Analyze
            </button>
          </div>
          <button className="sm:hidden text-gray-400" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            <Menu size={22} />
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="sm:hidden border-t border-white/[0.06] p-4 space-y-3">
            <button className="block w-full text-left text-gray-400 py-2">How it works</button>
            <button className="block w-full text-left text-gray-400 py-2">Pricing</button>
            <button onClick={() => { setView("analyze"); setMobileMenuOpen(false); }} className="block w-full text-left text-white font-medium py-2">Analyze →</button>
          </div>
        )}
      </nav>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {view === "home" && <Hero onGetStarted={() => setView("analyze")} />}
        {view === "analyze" && (
          <div className="max-w-3xl mx-auto animate-fadeIn">
            <h2 className="text-2xl font-bold text-white mb-2 text-center">Upload Your Document</h2>
            <p className="text-gray-400 text-center mb-8">We'll analyze it and show you exactly what you're agreeing to</p>
            <UploadZone onAnalyze={startAnalysis} isAnalyzing={isAnalyzing} />
            {!isAnalyzing && <DemoFiles onSelect={startAnalysis} />}
          </div>
        )}
        {view === "report" && report && (
          <ReportView report={report} onBack={() => { setView("analyze"); setReport(null); }} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/[0.04] mt-16 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-500">
          <p>© 2026 ClearCause. For informational purposes only — not legal advice.</p>
          <div className="flex gap-4">
            <a href="#" className="hover:text-gray-300 transition-colors">Privacy</a>
            <a href="#" className="hover:text-gray-300 transition-colors">Terms</a>
            <a href="#" className="hover:text-gray-300 transition-colors">Contact</a>
          </div>
        </div>
      </footer>

      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .animate-fadeIn { animation: fadeIn 0.5s ease-out; }
      `}</style>
    </div>
  );
}
