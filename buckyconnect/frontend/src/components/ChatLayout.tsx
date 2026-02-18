import { useState, useEffect, useCallback, useRef, lazy, Suspense } from "react";
import { useQuery, useMutation } from "@apollo/client";
import {
  GET_CHANNELS,
  GET_MESSAGES,
  GET_CHANNEL,
  SEND_MESSAGE,
  CREATE_CHANNEL,
  JOIN_CHANNEL,
} from "../graphql/queries";
import { useWebSocket, WSMessage } from "../hooks/useWebSocket";

// Lazy-loaded components for code splitting
const MembersPanel = lazy(() => import("./MembersPanel"));

interface User {
  id: string;
  username: string;
  display_name: string;
  status: string;
}

interface Message {
  id: string;
  channel_id: string;
  user_id: string;
  content: string;
  edited: boolean;
  created_at: string;
  username: string;
  display_name: string;
}

export default function ChatLayout({ user, onLogout }: { user: User; onLogout: () => void }) {
  const [activeChannelId, setActiveChannelId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [typingUsers, setTypingUsers] = useState<Map<string, string>>(new Map());
  const [showNewChannel, setShowNewChannel] = useState(false);
  const [showMembers, setShowMembers] = useState(true);
  const typingTimeoutRef = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // GraphQL
  const { data: channelsData, refetch: refetchChannels } = useQuery(GET_CHANNELS);
  const { data: channelData } = useQuery(GET_CHANNEL, {
    variables: { id: activeChannelId },
    skip: !activeChannelId,
  });
  const { data: messagesData, refetch: refetchMessages } = useQuery(GET_MESSAGES, {
    variables: { channelId: activeChannelId, limit: 100 },
    skip: !activeChannelId,
  });
  const [sendMessageMut] = useMutation(SEND_MESSAGE);
  const [createChannelMut] = useMutation(CREATE_CHANNEL);
  const [joinChannelMut] = useMutation(JOIN_CHANNEL);

  // WebSocket
  const { send, subscribe, isConnected } = useWebSocket(user.id, user.username);

  // Set initial channel
  useEffect(() => {
    if (channelsData?.channels?.length && !activeChannelId) {
      setActiveChannelId(channelsData.channels[0].id);
    }
  }, [channelsData, activeChannelId]);

  // Load messages from GraphQL query
  useEffect(() => {
    if (messagesData?.messages) {
      setMessages([...messagesData.messages].reverse());
    }
  }, [messagesData]);

  // Join channel via WS when switching
  useEffect(() => {
    if (activeChannelId) {
      send({ type: "join_channel", channelId: activeChannelId });
      setTypingUsers(new Map());
    }
  }, [activeChannelId, send]);

  // Handle incoming WS messages
  useEffect(() => {
    return subscribe((msg: WSMessage) => {
      switch (msg.type) {
        case "new_message":
          if (msg.channelId === activeChannelId && msg.message) {
            setMessages((prev) => {
              if (prev.find((m) => m.id === msg.message.id)) return prev;
              return [...prev, msg.message];
            });
          }
          break;

        case "typing":
          if (msg.channelId === activeChannelId && msg.userId !== user.id) {
            setTypingUsers((prev) => {
              const next = new Map(prev);
              if (msg.isTyping) {
                next.set(msg.userId, msg.username);
                // Clear after 3s
                const existing = typingTimeoutRef.current.get(msg.userId);
                if (existing) clearTimeout(existing);
                typingTimeoutRef.current.set(
                  msg.userId,
                  setTimeout(() => {
                    setTypingUsers((p) => {
                      const n = new Map(p);
                      n.delete(msg.userId);
                      return n;
                    });
                  }, 3000)
                );
              } else {
                next.delete(msg.userId);
              }
              return next;
            });
          }
          break;

        case "presence":
          // Could refresh member list
          break;
      }
    });
  }, [subscribe, activeChannelId, user.id]);

  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!activeChannelId || !content.trim()) return;
      try {
        await sendMessageMut({
          variables: { channelId: activeChannelId, userId: user.id, content: content.trim() },
        });
        // WS will handle adding to local state via fanout
        // Also refetch as fallback
        refetchMessages();
      } catch (err) {
        console.error("Send message error:", err);
      }
    },
    [activeChannelId, user.id, sendMessageMut, refetchMessages]
  );

  const handleCreateChannel = useCallback(
    async (name: string, description: string) => {
      try {
        const { data } = await createChannelMut({
          variables: { name: name.trim().toLowerCase().replace(/\s+/g, "-"), description, userId: user.id },
        });
        if (data?.createChannel) {
          refetchChannels();
          setActiveChannelId(data.createChannel.id);
          setShowNewChannel(false);
        }
      } catch (err) {
        console.error("Create channel error:", err);
      }
    },
    [user.id, createChannelMut, refetchChannels]
  );

  const handleTyping = useCallback(() => {
    if (activeChannelId) {
      send({ type: "typing", channelId: activeChannelId, isTyping: true });
    }
  }, [activeChannelId, send]);

  const channels = channelsData?.channels || [];
  const members = channelData?.channel?.members || [];
  const activeChannel = channels.find((c: any) => c.id === activeChannelId);

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>🔗 BuckyConnect</h1>
        </div>
        <div className="channel-list">
          {channels.map((ch: any) => (
            <div
              key={ch.id}
              className={`channel-item ${ch.id === activeChannelId ? "active" : ""}`}
              onClick={() => setActiveChannelId(ch.id)}
            >
              <span className="hash">#</span>
              {ch.name}
            </div>
          ))}
          <button className="add-channel-btn" onClick={() => setShowNewChannel(true)}>
            + New Channel
          </button>
        </div>
        <div className="sidebar-footer">
          <div className={`status-dot ${isConnected ? "" : "offline"}`} />
          <span style={{ flex: 1 }}>{user.display_name}</span>
          <button
            className="btn-secondary"
            style={{ padding: "4px 8px", fontSize: 11 }}
            onClick={onLogout}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="channel-header">
          <div style={{ display: "flex", alignItems: "center" }}>
            <h2># {activeChannel?.name || "..."}</h2>
            {activeChannel?.description && (
              <span className="description">{activeChannel.description}</span>
            )}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div className="connection-status">
              <div className={`status-dot ${isConnected ? "" : "offline"}`} />
              {isConnected ? "Connected" : "Reconnecting..."}
            </div>
            <button
              className="btn-secondary"
              style={{ padding: "4px 10px", fontSize: 12 }}
              onClick={() => setShowMembers(!showMembers)}
            >
              {showMembers ? "Hide" : "Show"} Members
            </button>
          </div>
        </div>

        <div className="messages-container">
          {[...messages].reverse().map((msg) => (
            <div key={msg.id} className="message">
              <div className="message-avatar">
                {(msg.display_name || msg.username || "?")[0].toUpperCase()}
              </div>
              <div className="message-body">
                <div className="message-header">
                  <span className="message-username">{msg.display_name || msg.username}</span>
                  <span className="message-time">
                    {new Date(msg.created_at + "Z").toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                  {msg.edited && <span className="message-edited">(edited)</span>}
                </div>
                <div className="message-content">{msg.content}</div>
              </div>
            </div>
          ))}
          {messages.length === 0 && (
            <div style={{ textAlign: "center", color: "var(--text-muted)", padding: 40 }}>
              No messages yet. Say hello! 👋
            </div>
          )}
        </div>

        <TypingIndicator users={typingUsers} />
        <MessageInput onSend={handleSendMessage} onTyping={handleTyping} />
      </div>

      {/* Members Panel */}
      {showMembers && (
        <Suspense fallback={<div className="members-panel"><p>Loading...</p></div>}>
          <MembersPanel members={members} />
        </Suspense>
      )}

      {/* New Channel Modal */}
      {showNewChannel && (
        <NewChannelModal
          onClose={() => setShowNewChannel(false)}
          onCreate={handleCreateChannel}
        />
      )}
    </div>
  );
}

function MessageInput({ onSend, onTyping }: { onSend: (content: string) => void; onTyping: () => void }) {
  const [value, setValue] = useState("");
  const typingTimerRef = useRef<NodeJS.Timeout>();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value);
    if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
    onTyping();
    typingTimerRef.current = setTimeout(() => {}, 2000);
  };

  const handleSend = () => {
    if (!value.trim()) return;
    onSend(value);
    setValue("");
  };

  return (
    <div className="message-input-container">
      <div className="message-input-wrapper">
        <input
          className="message-input"
          placeholder="Type a message..."
          value={value}
          onChange={handleChange}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
        />
        <button className="send-btn" onClick={handleSend} disabled={!value.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

function TypingIndicator({ users }: { users: Map<string, string> }) {
  if (users.size === 0) return <div className="typing-indicator" />;
  const names = Array.from(users.values());
  const text =
    names.length === 1
      ? `${names[0]} is typing...`
      : names.length === 2
      ? `${names[0]} and ${names[1]} are typing...`
      : `${names[0]} and ${names.length - 1} others are typing...`;
  return <div className="typing-indicator">{text}</div>;
}

function NewChannelModal({
  onClose,
  onCreate,
}: {
  onClose: () => void;
  onCreate: (name: string, description: string) => void;
}) {
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Create Channel</h2>
        <input
          className="login-input"
          placeholder="Channel name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
        />
        <input
          className="login-input"
          placeholder="Description (optional)"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
        />
        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={() => onCreate(name, desc)} disabled={!name.trim()}>
            Create
          </button>
        </div>
      </div>
    </div>
  );
}
