import { useState, useEffect, useRef, useCallback } from "react";

const COLORS = {
  bg: "#0B1120",
  bgCard: "#111827",
  bgCardHover: "#1A2332",
  border: "#1E293B",
  borderAccent: "#0D9488",
  teal: "#14B8A6",
  tealDark: "#0D9488",
  tealLight: "#5EEAD4",
  navy: "#1E3A5F",
  red: "#EF4444",
  orange: "#F59E0B",
  green: "#22C55E",
  text: "#F1F5F9",
  textMuted: "#94A3B8",
  textDim: "#64748B",
  white: "#FFFFFF",
};

const RISK_COLORS = { High: COLORS.red, Medium: COLORS.orange, Low: COLORS.green };

// ─── Spinner ───
function Spinner({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={{ animation: "spin 1s linear infinite" }}>
      <circle cx="12" cy="12" r="10" stroke={COLORS.teal} strokeWidth="3" fill="none" strokeDasharray="31.4 31.4" strokeLinecap="round" />
    </svg>
  );
}

// ─── Icons ───
function ShieldIcon({ color = COLORS.teal, size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}
function UploadIcon({ size = 40 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={COLORS.teal} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}
function FileIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={COLORS.tealLight} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}
function AlertIcon({ color, size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}
function CheckIcon({ color = COLORS.green, size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
function DownloadIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}

// ─── Analysis Prompt ───
function buildPrompt(text) {
  return `You are ClearCause, an AI legal document analyzer. Analyze the following contract/legal document and return your analysis as valid JSON ONLY (no markdown, no backticks, no explanation outside the JSON).

JSON format:
{
  "document_title": "string - inferred title of the document",
  "document_type": "string - e.g. Terms of Service, Lease Agreement, SaaS Contract, NDA, etc.",
  "overall_risk": "High" | "Medium" | "Low",
  "risk_score": number 1-100,
  "executive_summary": "string - 2-3 sentence plain-English summary of what this document does, written at 8th grade reading level",
  "clauses": [
    {
      "clause_name": "string - e.g. Arbitration Clause, Auto-Renewal, Data Collection",
      "risk_level": "High" | "Medium" | "Low",
      "original_text": "string - exact quote from the document (keep under 40 words)",
      "plain_summary": "string - what this means in simple English (1-2 sentences, 8th grade level)",
      "what_to_ask": "string - a question the user should ask the other party about this clause",
      "section_ref": "string - section number or location reference like §3.2 or 'Paragraph 5'"
    }
  ],
  "key_risks": [
    {
      "risk": "string - short risk title",
      "severity": "High" | "Medium" | "Low",
      "explanation": "string - 1 sentence plain English explanation"
    }
  ],
  "positive_points": ["string - good things about this contract for the signer"],
  "negotiation_tips": ["string - actionable negotiation suggestions"],
  "readability_grade": "string - estimated reading level like 'College' or 'Grade 12'"
}

Analyze 6-10 clauses minimum. Focus on clauses that carry risk or are commonly misunderstood. Be thorough but keep language simple.

DOCUMENT TEXT:
${text.substring(0, 12000)}`;
}

// ─── Risk Badge ───
function RiskBadge({ level, large }) {
  const color = RISK_COLORS[level] || COLORS.textMuted;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      padding: large ? "6px 16px" : "3px 10px",
      borderRadius: 20,
      background: color + "18",
      color: color,
      fontSize: large ? 15 : 12,
      fontWeight: 700,
      letterSpacing: 0.5,
      border: `1px solid ${color}30`,
    }}>
      {level === "High" ? <AlertIcon color={color} size={large ? 16 : 13} /> : level === "Low" ? <CheckIcon color={color} size={large ? 16 : 13} /> : <AlertIcon color={color} size={large ? 16 : 13} />}
      {level}
    </span>
  );
}

// ─── Risk Score Ring ───
function RiskRing({ score, size = 140 }) {
  const r = (size - 16) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score >= 70 ? COLORS.red : score >= 40 ? COLORS.orange : COLORS.green;
  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={COLORS.border} strokeWidth="8" />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1.2s ease" }} />
      </svg>
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
      }}>
        <span style={{ fontSize: 36, fontWeight: 800, color, lineHeight: 1 }}>{score}</span>
        <span style={{ fontSize: 11, color: COLORS.textMuted, marginTop: 2 }}>/ 100</span>
      </div>
    </div>
  );
}

// ─── Clause Card ───
function ClauseCard({ clause, index }) {
  const [open, setOpen] = useState(false);
  const color = RISK_COLORS[clause.risk_level] || COLORS.textMuted;
  return (
    <div style={{
      background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
      borderRadius: 12, overflow: "hidden", transition: "border-color 0.2s",
      borderLeft: `3px solid ${color}`,
    }}
      onMouseEnter={e => e.currentTarget.style.borderColor = color + "60"}
      onMouseLeave={e => e.currentTarget.style.borderColor = COLORS.border}
    >
      <div onClick={() => setOpen(!open)} style={{
        padding: "16px 20px", cursor: "pointer", display: "flex",
        alignItems: "center", justifyContent: "space-between", gap: 12,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, flex: 1, minWidth: 0 }}>
          <span style={{
            width: 28, height: 28, borderRadius: 8, background: color + "18",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 12, fontWeight: 700, color, flexShrink: 0,
          }}>{index + 1}</span>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: 15, fontWeight: 600, color: COLORS.text }}>{clause.clause_name}</div>
            {clause.section_ref && (
              <span style={{ fontSize: 11, color: COLORS.teal, fontFamily: "monospace" }}>{clause.section_ref}</span>
            )}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <RiskBadge level={clause.risk_level} />
          <span style={{ color: COLORS.textDim, fontSize: 18, transition: "transform 0.2s", transform: open ? "rotate(180deg)" : "rotate(0)" }}>▾</span>
        </div>
      </div>
      {open && (
        <div style={{ padding: "0 20px 20px 20px", animation: "fadeIn 0.2s ease" }}>
          <div style={{ borderTop: `1px solid ${COLORS.border}`, paddingTop: 16 }}>
            {clause.original_text && (
              <div style={{
                background: COLORS.bg, borderRadius: 8, padding: "12px 16px", marginBottom: 14,
                borderLeft: `2px solid ${COLORS.tealDark}`, fontSize: 13, color: COLORS.textMuted,
                fontStyle: "italic", lineHeight: 1.6,
              }}>
                "{clause.original_text}"
              </div>
            )}
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.teal, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>Plain English</div>
              <div style={{ fontSize: 14, color: COLORS.text, lineHeight: 1.7 }}>{clause.plain_summary}</div>
            </div>
            {clause.what_to_ask && (
              <div style={{
                background: COLORS.teal + "10", border: `1px solid ${COLORS.teal}25`,
                borderRadius: 8, padding: "10px 14px",
              }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.teal, textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>💡 What to Ask</div>
                <div style={{ fontSize: 13, color: COLORS.tealLight, lineHeight: 1.5 }}>{clause.what_to_ask}</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Landing Page ───
function LandingPage({ onGetStarted }) {
  const features = [
    { icon: "🔍", title: "Clause Detection", desc: "Identifies arbitration, auto-renewal, liability caps, data collection, and more" },
    { icon: "🎯", title: "Risk Scoring", desc: "Every clause scored Low / Medium / High with transparent, explainable reasoning" },
    { icon: "📖", title: "Plain English", desc: "Complex legalese translated to 8th-grade reading level with exact citations" },
    { icon: "💬", title: "Negotiation Tips", desc: "Actionable prompts telling you exactly what to ask the other party" },
  ];
  return (
    <div style={{ minHeight: "100vh", background: COLORS.bg, color: COLORS.text }}>
      {/* Hero */}
      <div style={{
        minHeight: "80vh", display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", textAlign: "center",
        padding: "60px 24px",
        background: `radial-gradient(ellipse 80% 60% at 50% 20%, ${COLORS.teal}08, transparent),
                      radial-gradient(ellipse 60% 40% at 80% 80%, ${COLORS.navy}20, transparent)`,
      }}>
        <div style={{
          display: "inline-flex", alignItems: "center", gap: 8, marginBottom: 32,
          padding: "6px 16px", borderRadius: 20, background: COLORS.teal + "12",
          border: `1px solid ${COLORS.teal}30`, fontSize: 13, color: COLORS.teal,
        }}>
          <ShieldIcon size={16} /> AI-Powered Contract Intelligence
        </div>
        <h1 style={{
          fontSize: "clamp(42px, 6vw, 72px)", fontWeight: 800, lineHeight: 1.1,
          margin: 0, letterSpacing: -2,
          fontFamily: "'Georgia', 'Times New Roman', serif",
        }}>
          <span style={{ color: COLORS.tealLight }}>Clear</span>Cause
        </h1>
        <p style={{
          fontSize: "clamp(16px, 2vw, 20px)", color: COLORS.textMuted,
          maxWidth: 580, margin: "20px 0 40px", lineHeight: 1.7,
        }}>
          Upload any contract. Get instant plain-English summaries, risk scores, and negotiation tips — no law degree required.
        </p>
        <button onClick={onGetStarted} style={{
          padding: "16px 40px", fontSize: 16, fontWeight: 700,
          background: `linear-gradient(135deg, ${COLORS.tealDark}, ${COLORS.teal})`,
          color: COLORS.white, border: "none", borderRadius: 12, cursor: "pointer",
          boxShadow: `0 4px 24px ${COLORS.teal}30`,
          transition: "transform 0.15s, box-shadow 0.15s",
        }}
          onMouseEnter={e => { e.target.style.transform = "translateY(-2px)"; e.target.style.boxShadow = `0 8px 32px ${COLORS.teal}40`; }}
          onMouseLeave={e => { e.target.style.transform = "translateY(0)"; e.target.style.boxShadow = `0 4px 24px ${COLORS.teal}30`; }}
        >
          Analyze a Contract →
        </button>
        <div style={{ display: "flex", gap: 24, marginTop: 28, flexWrap: "wrap", justifyContent: "center" }}>
          {["No signup required", "Free analysis", "Your data stays private"].map(t => (
            <span key={t} style={{ fontSize: 13, color: COLORS.textDim, display: "flex", alignItems: "center", gap: 6 }}>
              <CheckIcon size={14} color={COLORS.teal} /> {t}
            </span>
          ))}
        </div>
      </div>
      {/* Features */}
      <div style={{
        maxWidth: 960, margin: "0 auto", padding: "40px 24px 80px",
        display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 20,
      }}>
        {features.map(f => (
          <div key={f.title} style={{
            background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
            borderRadius: 14, padding: 24, transition: "border-color 0.2s",
          }}
            onMouseEnter={e => e.currentTarget.style.borderColor = COLORS.teal + "40"}
            onMouseLeave={e => e.currentTarget.style.borderColor = COLORS.border}
          >
            <div style={{ fontSize: 28, marginBottom: 12 }}>{f.icon}</div>
            <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 8, color: COLORS.text }}>{f.title}</div>
            <div style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.6 }}>{f.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Upload Page ───
function UploadPage({ onAnalyze, analyzing }) {
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState(null);
  const [pasteText, setPasteText] = useState("");
  const [mode, setMode] = useState("upload"); // upload | paste
  const inputRef = useRef();

  const handleFile = (f) => {
    if (f) setFile(f);
  };

  const startAnalysis = async () => {
    if (mode === "paste" && pasteText.trim()) {
      onAnalyze(pasteText.trim());
    } else if (file) {
      const text = await file.text();
      onAnalyze(text);
    }
  };

  const ready = mode === "paste" ? pasteText.trim().length > 50 : !!file;

  return (
    <div style={{
      minHeight: "100vh", background: COLORS.bg, color: COLORS.text,
      display: "flex", flexDirection: "column", alignItems: "center",
      padding: "60px 24px",
      background: `radial-gradient(ellipse 80% 40% at 50% 10%, ${COLORS.teal}06, transparent), ${COLORS.bg}`,
    }}>
      <h2 style={{ fontSize: 32, fontWeight: 800, marginBottom: 8, fontFamily: "'Georgia', serif" }}>
        <span style={{ color: COLORS.tealLight }}>Analyze</span> Your Contract
      </h2>
      <p style={{ color: COLORS.textMuted, marginBottom: 36, fontSize: 15 }}>
        Upload a document or paste the contract text directly
      </p>

      {/* Mode toggle */}
      <div style={{
        display: "flex", gap: 4, marginBottom: 28, background: COLORS.bgCard,
        borderRadius: 10, padding: 4, border: `1px solid ${COLORS.border}`,
      }}>
        {[["upload", "📄 Upload File"], ["paste", "✍️ Paste Text"]].map(([m, label]) => (
          <button key={m} onClick={() => setMode(m)} style={{
            padding: "10px 24px", borderRadius: 8, border: "none", cursor: "pointer",
            fontSize: 14, fontWeight: 600, transition: "all 0.15s",
            background: mode === m ? COLORS.teal + "20" : "transparent",
            color: mode === m ? COLORS.teal : COLORS.textMuted,
          }}>{label}</button>
        ))}
      </div>

      {mode === "upload" ? (
        <div
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={e => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
          onClick={() => inputRef.current?.click()}
          style={{
            width: "100%", maxWidth: 560, minHeight: 220,
            border: `2px dashed ${dragOver ? COLORS.teal : COLORS.border}`,
            borderRadius: 16, cursor: "pointer", transition: "all 0.2s",
            background: dragOver ? COLORS.teal + "08" : COLORS.bgCard,
            display: "flex", flexDirection: "column", alignItems: "center",
            justifyContent: "center", gap: 12, padding: 32,
          }}
        >
          <input ref={inputRef} type="file" accept=".txt,.pdf,.doc,.docx,.md,.html,.rtf" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
          {file ? (
            <>
              <FileIcon size={36} />
              <div style={{ fontSize: 16, fontWeight: 600, color: COLORS.tealLight }}>{file.name}</div>
              <div style={{ fontSize: 13, color: COLORS.textMuted }}>{(file.size / 1024).toFixed(1)} KB — Click to change</div>
            </>
          ) : (
            <>
              <UploadIcon size={44} />
              <div style={{ fontSize: 16, fontWeight: 600 }}>Drop your contract here</div>
              <div style={{ fontSize: 13, color: COLORS.textMuted }}>or click to browse — .txt, .md, .html, .rtf supported</div>
              <div style={{ fontSize: 12, color: COLORS.textDim, marginTop: 4 }}>For best results, use plain text. PDF text extraction coming soon.</div>
            </>
          )}
        </div>
      ) : (
        <textarea
          value={pasteText}
          onChange={e => setPasteText(e.target.value)}
          placeholder="Paste your contract or Terms of Service text here...&#10;&#10;Tip: Copy the full text from the document for the most thorough analysis."
          style={{
            width: "100%", maxWidth: 560, minHeight: 260,
            background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
            borderRadius: 14, padding: 20, fontSize: 14, color: COLORS.text,
            resize: "vertical", outline: "none", lineHeight: 1.7,
            fontFamily: "'Courier New', monospace",
          }}
          onFocus={e => e.target.style.borderColor = COLORS.teal}
          onBlur={e => e.target.style.borderColor = COLORS.border}
        />
      )}

      <button onClick={startAnalysis} disabled={!ready || analyzing} style={{
        marginTop: 28, padding: "14px 44px", fontSize: 16, fontWeight: 700,
        background: ready && !analyzing ? `linear-gradient(135deg, ${COLORS.tealDark}, ${COLORS.teal})` : COLORS.border,
        color: ready && !analyzing ? COLORS.white : COLORS.textDim,
        border: "none", borderRadius: 12, cursor: ready && !analyzing ? "pointer" : "not-allowed",
        display: "flex", alignItems: "center", gap: 10,
        boxShadow: ready && !analyzing ? `0 4px 24px ${COLORS.teal}25` : "none",
        transition: "all 0.2s",
      }}>
        {analyzing ? <><Spinner size={20} /> Analyzing...</> : "🔍 Analyze Contract"}
      </button>

      {analyzing && (
        <div style={{ marginTop: 32, textAlign: "center", animation: "fadeIn 0.4s ease" }}>
          <div style={{ color: COLORS.teal, fontSize: 14, marginBottom: 8 }}>AI is reading your document...</div>
          <div style={{ fontSize: 12, color: COLORS.textDim }}>Detecting clauses · Scoring risks · Writing summaries</div>
        </div>
      )}
    </div>
  );
}

// ─── Results Dashboard ───
function ResultsPage({ analysis, onNew, documentText }) {
  const a = analysis;

  const exportReport = () => {
    let report = `CLEARCAUSE CONTRACT ANALYSIS REPORT\n${"=".repeat(50)}\n\n`;
    report += `Document: ${a.document_title}\nType: ${a.document_type}\nOverall Risk: ${a.overall_risk} (${a.risk_score}/100)\nReadability: ${a.readability_grade}\n\n`;
    report += `EXECUTIVE SUMMARY\n${"-".repeat(30)}\n${a.executive_summary}\n\n`;
    report += `KEY RISKS\n${"-".repeat(30)}\n`;
    a.key_risks?.forEach((r, i) => { report += `${i + 1}. [${r.severity}] ${r.risk}: ${r.explanation}\n`; });
    report += `\nCLAUSE ANALYSIS\n${"-".repeat(30)}\n`;
    a.clauses?.forEach((c, i) => {
      report += `\n${i + 1}. ${c.clause_name} [${c.risk_level}] ${c.section_ref || ""}\n`;
      report += `   Original: "${c.original_text}"\n`;
      report += `   Summary: ${c.plain_summary}\n`;
      report += `   Ask: ${c.what_to_ask}\n`;
    });
    report += `\nPOSITIVE POINTS\n${"-".repeat(30)}\n`;
    a.positive_points?.forEach((p, i) => { report += `${i + 1}. ${p}\n`; });
    report += `\nNEGOTIATION TIPS\n${"-".repeat(30)}\n`;
    a.negotiation_tips?.forEach((t, i) => { report += `${i + 1}. ${t}\n`; });
    report += `\n${"=".repeat(50)}\nGenerated by ClearCause — AI Contract Analysis\n`;

    const blob = new Blob([report], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `ClearCause_Report_${(a.document_title || "contract").replace(/\s+/g, "_")}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const highCount = a.clauses?.filter(c => c.risk_level === "High").length || 0;
  const medCount = a.clauses?.filter(c => c.risk_level === "Medium").length || 0;
  const lowCount = a.clauses?.filter(c => c.risk_level === "Low").length || 0;

  return (
    <div style={{
      minHeight: "100vh", background: COLORS.bg, color: COLORS.text,
      padding: "40px 24px 80px",
    }}>
      <div style={{ maxWidth: 900, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16, marginBottom: 36 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <ShieldIcon size={22} />
              <span style={{ fontSize: 14, fontWeight: 700, color: COLORS.teal, letterSpacing: 1 }}>CLEARCAUSE REPORT</span>
            </div>
            <h1 style={{ fontSize: 28, fontWeight: 800, margin: 0, fontFamily: "'Georgia', serif" }}>{a.document_title}</h1>
            <span style={{ fontSize: 13, color: COLORS.textMuted }}>{a.document_type} · Readability: {a.readability_grade}</span>
          </div>
          <div style={{ display: "flex", gap: 10 }}>
            <button onClick={exportReport} style={{
              padding: "10px 20px", borderRadius: 10, border: `1px solid ${COLORS.teal}40`,
              background: "transparent", color: COLORS.teal, fontSize: 14, fontWeight: 600,
              cursor: "pointer", display: "flex", alignItems: "center", gap: 8,
            }}>
              <DownloadIcon /> Export
            </button>
            <button onClick={onNew} style={{
              padding: "10px 20px", borderRadius: 10, border: `1px solid ${COLORS.border}`,
              background: COLORS.bgCard, color: COLORS.textMuted, fontSize: 14, fontWeight: 600,
              cursor: "pointer",
            }}>+ New</button>
          </div>
        </div>

        {/* Top Row: Score + Summary */}
        <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 20, marginBottom: 28 }}>
          {/* Score Card */}
          <div style={{
            background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
            borderRadius: 16, padding: 28, display: "flex", flexDirection: "column",
            alignItems: "center", gap: 12, minWidth: 190,
          }}>
            <RiskRing score={a.risk_score} />
            <RiskBadge level={a.overall_risk} large />
            <div style={{ display: "flex", gap: 14, marginTop: 6 }}>
              {[["High", highCount], ["Med", medCount], ["Low", lowCount]].map(([label, count]) => (
                <div key={label} style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 20, fontWeight: 800, color: RISK_COLORS[label === "Med" ? "Medium" : label] }}>{count}</div>
                  <div style={{ fontSize: 10, color: COLORS.textDim, textTransform: "uppercase" }}>{label}</div>
                </div>
              ))}
            </div>
          </div>
          {/* Summary + Risks */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{
              background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
              borderRadius: 14, padding: 22, flex: 1,
            }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.teal, textTransform: "uppercase", letterSpacing: 1, marginBottom: 10 }}>Executive Summary</div>
              <div style={{ fontSize: 15, lineHeight: 1.8, color: COLORS.text }}>{a.executive_summary}</div>
            </div>
            {/* Key Risks */}
            <div style={{
              background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
              borderRadius: 14, padding: 22,
            }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.red, textTransform: "uppercase", letterSpacing: 1, marginBottom: 12 }}>Key Risks</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {a.key_risks?.map((r, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                    <RiskBadge level={r.severity} />
                    <div>
                      <span style={{ fontWeight: 700, fontSize: 14 }}>{r.risk}: </span>
                      <span style={{ fontSize: 13, color: COLORS.textMuted }}>{r.explanation}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Clause Analysis */}
        <div style={{ marginBottom: 28 }}>
          <h2 style={{ fontSize: 20, fontWeight: 800, marginBottom: 16, display: "flex", alignItems: "center", gap: 10, fontFamily: "'Georgia', serif" }}>
            📋 Clause-by-Clause Analysis
            <span style={{ fontSize: 12, fontWeight: 500, color: COLORS.textDim }}>({a.clauses?.length || 0} clauses found)</span>
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {a.clauses?.map((c, i) => <ClauseCard key={i} clause={c} index={i} />)}
          </div>
        </div>

        {/* Bottom: Positives + Negotiation */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
          <div style={{
            background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
            borderRadius: 14, padding: 22,
          }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.green, textTransform: "uppercase", letterSpacing: 1, marginBottom: 14 }}>✅ Positive Points</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {a.positive_points?.map((p, i) => (
                <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                  <CheckIcon size={16} color={COLORS.green} />
                  <span style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.6 }}>{p}</span>
                </div>
              ))}
            </div>
          </div>
          <div style={{
            background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
            borderRadius: 14, padding: 22,
          }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.teal, textTransform: "uppercase", letterSpacing: 1, marginBottom: 14 }}>💬 Negotiation Tips</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {a.negotiation_tips?.map((t, i) => (
                <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                  <span style={{ color: COLORS.teal, fontWeight: 700, fontSize: 14 }}>{i + 1}.</span>
                  <span style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.6 }}>{t}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div style={{
          marginTop: 40, padding: "16px 20px", borderRadius: 10,
          background: COLORS.teal + "08", border: `1px solid ${COLORS.teal}15`,
          fontSize: 12, color: COLORS.textDim, lineHeight: 1.6, textAlign: "center",
        }}>
          ⚠️ ClearCause provides informational analysis only. This is not legal advice. Risk scores are relative to typical consumer contracts. Consult a licensed attorney for legal decisions.
        </div>
      </div>
    </div>
  );
}

// ─── Error Panel ───
function ErrorPanel({ error, onRetry }) {
  return (
    <div style={{
      minHeight: "100vh", background: COLORS.bg, color: COLORS.text,
      display: "flex", flexDirection: "column", alignItems: "center",
      justifyContent: "center", padding: 24, textAlign: "center",
    }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
      <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 12, fontFamily: "'Georgia', serif" }}>Analysis Error</h2>
      <p style={{ color: COLORS.textMuted, maxWidth: 480, marginBottom: 8, lineHeight: 1.7, fontSize: 14 }}>
        {error || "Something went wrong while analyzing your document. This could be due to the document format or a temporary issue."}
      </p>
      <p style={{ color: COLORS.textDim, maxWidth: 480, marginBottom: 28, lineHeight: 1.7, fontSize: 13 }}>
        Tip: Try pasting the contract text directly for best results.
      </p>
      <button onClick={onRetry} style={{
        padding: "12px 32px", borderRadius: 10,
        background: `linear-gradient(135deg, ${COLORS.tealDark}, ${COLORS.teal})`,
        color: COLORS.white, border: "none", fontSize: 15, fontWeight: 700, cursor: "pointer",
      }}>Try Again</button>
    </div>
  );
}

// ─── Main App ───
export default function ClearCauseApp() {
  const [page, setPage] = useState("landing"); // landing | upload | results | error
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [docText, setDocText] = useState("");
  const [error, setError] = useState("");

  const analyze = useCallback(async (text) => {
    setAnalyzing(true);
    setDocText(text);
    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 4000,
          messages: [{ role: "user", content: buildPrompt(text) }],
        }),
      });
      const data = await response.json();
      const raw = data.content?.map(b => b.text || "").join("") || "";
      // Strip any markdown fences
      const cleaned = raw.replace(/```json\s*/g, "").replace(/```\s*/g, "").trim();
      const parsed = JSON.parse(cleaned);
      setAnalysis(parsed);
      setPage("results");
    } catch (err) {
      console.error("Analysis failed:", err);
      setError(err.message || "Failed to parse analysis results");
      setPage("error");
    } finally {
      setAnalyzing(false);
    }
  }, []);

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'DM Sans', -apple-system, sans-serif; -webkit-font-smoothing: antialiased; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
        ::selection { background: ${COLORS.teal}40; }
        textarea::placeholder { color: ${COLORS.textDim}; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: ${COLORS.bg}; }
        ::-webkit-scrollbar-thumb { background: ${COLORS.border}; border-radius: 4px; }
      `}</style>
      {page === "landing" && <LandingPage onGetStarted={() => setPage("upload")} />}
      {page === "upload" && <UploadPage onAnalyze={analyze} analyzing={analyzing} />}
      {page === "results" && <ResultsPage analysis={analysis} onNew={() => { setAnalysis(null); setPage("upload"); }} documentText={docText} />}
      {page === "error" && <ErrorPanel error={error} onRetry={() => setPage("upload")} />}
    </>
  );
}
