import { useState, useCallback } from "react";
import { useMutation } from "@apollo/client";
import { REGISTER_USER } from "./graphql/queries";
import ChatLayout from "./components/ChatLayout";

interface User {
  id: string;
  username: string;
  display_name: string;
  status: string;
}

export default function App() {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const stored = sessionStorage.getItem("buckyconnect_user");
      return stored ? JSON.parse(stored) : null;
    } catch { return null; }
  });

  const handleLogin = useCallback((u: User) => {
    setUser(u);
    sessionStorage.setItem("buckyconnect_user", JSON.stringify(u));
  }, []);

  const handleLogout = useCallback(() => {
    setUser(null);
    sessionStorage.removeItem("buckyconnect_user");
  }, []);

  if (!user) return <LoginScreen onLogin={handleLogin} />;
  return <ChatLayout user={user} onLogout={handleLogout} />;
}

function LoginScreen({ onLogin }: { onLogin: (u: User) => void }) {
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [register, { loading, error }] = useMutation(REGISTER_USER);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;
    try {
      const { data } = await register({
        variables: {
          username: username.trim().toLowerCase(),
          displayName: displayName.trim() || username.trim(),
        },
      });
      if (data?.register) onLogin(data.register);
    } catch (err) {
      console.error("Registration error:", err);
    }
  };

  return (
    <div className="login-container">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>🔗 BuckyConnect</h1>
        <p>Real-time collaboration, instantly.</p>
        <input
          className="login-input"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoFocus
          maxLength={30}
        />
        <input
          className="login-input"
          placeholder="Display Name (optional)"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          maxLength={50}
        />
        {error && <p style={{ color: "var(--accent)", fontSize: 13, marginBottom: 8 }}>Connection error. Is the backend running?</p>}
        <button className="login-btn" type="submit" disabled={loading || !username.trim()}>
          {loading ? "Connecting..." : "Join"}
        </button>
      </form>
    </div>
  );
}
