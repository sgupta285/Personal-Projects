interface Member {
  id: string;
  username: string;
  display_name: string;
  status: string;
}

export default function MembersPanel({ members }: { members: Member[] }) {
  const online = members.filter((m) => m.status === "online");
  const offline = members.filter((m) => m.status !== "online");

  return (
    <div className="members-panel">
      {online.length > 0 && (
        <>
          <h3>Online — {online.length}</h3>
          {online.map((m) => (
            <div key={m.id} className="member-item">
              <div className="status-dot" />
              <span>{m.display_name || m.username}</span>
            </div>
          ))}
        </>
      )}
      {offline.length > 0 && (
        <>
          <h3 style={{ marginTop: online.length > 0 ? 16 : 0 }}>Offline — {offline.length}</h3>
          {offline.map((m) => (
            <div key={m.id} className="member-item">
              <div className="status-dot offline" />
              <span>{m.display_name || m.username}</span>
            </div>
          ))}
        </>
      )}
      {members.length === 0 && (
        <p style={{ color: "var(--text-muted)", fontSize: 13 }}>No members yet</p>
      )}
    </div>
  );
}
