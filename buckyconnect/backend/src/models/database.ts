import Database from "better-sqlite3";
import path from "path";

const DB_PATH = process.env.DB_PATH || path.join(__dirname, "../../data/buckyconnect.db");

let db: Database.Database;

export function getDb(): Database.Database {
  if (!db) {
    const dir = path.dirname(DB_PATH);
    const fs = require("fs");
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

    db = new Database(DB_PATH);
    db.pragma("journal_mode = WAL");
    db.pragma("foreign_keys = ON");
    initSchema(db);
  }
  return db;
}

function initSchema(db: Database.Database) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      username TEXT UNIQUE NOT NULL,
      display_name TEXT NOT NULL,
      avatar_url TEXT DEFAULT '',
      status TEXT DEFAULT 'offline',
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS channels (
      id TEXT PRIMARY KEY,
      name TEXT UNIQUE NOT NULL,
      description TEXT DEFAULT '',
      created_by TEXT REFERENCES users(id),
      is_private INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS channel_members (
      channel_id TEXT REFERENCES channels(id) ON DELETE CASCADE,
      user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
      role TEXT DEFAULT 'member',
      joined_at TEXT DEFAULT (datetime('now')),
      PRIMARY KEY (channel_id, user_id)
    );

    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY,
      channel_id TEXT REFERENCES channels(id) ON DELETE CASCADE,
      user_id TEXT REFERENCES users(id),
      content TEXT NOT NULL,
      message_type TEXT DEFAULT 'text',
      edited INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel_id, created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id);
    CREATE INDEX IF NOT EXISTS idx_channel_members_user ON channel_members(user_id);
  `);

  // Seed default channel if empty
  const count = db.prepare("SELECT COUNT(*) as c FROM channels").get() as { c: number };
  if (count.c === 0) {
    const { v4: uuidv4 } = require("uuid");
    const generalId = uuidv4();
    const systemUserId = uuidv4();

    db.prepare("INSERT INTO users (id, username, display_name, status) VALUES (?, ?, ?, ?)").run(
      systemUserId, "system", "System", "online"
    );
    db.prepare("INSERT INTO channels (id, name, description, created_by) VALUES (?, ?, ?, ?)").run(
      generalId, "general", "General discussion channel", systemUserId
    );
  }
}

// --- User Operations ---
export function createUser(id: string, username: string, displayName: string): any {
  const stmt = getDb().prepare(
    "INSERT INTO users (id, username, display_name) VALUES (?, ?, ?)"
  );
  stmt.run(id, username, displayName);
  return getUserById(id);
}

export function getUserById(id: string): any {
  return getDb().prepare("SELECT * FROM users WHERE id = ?").get(id);
}

export function getUserByUsername(username: string): any {
  return getDb().prepare("SELECT * FROM users WHERE username = ?").get(username);
}

export function getAllUsers(): any[] {
  return getDb().prepare("SELECT * FROM users ORDER BY username").all();
}

export function updateUserStatus(id: string, status: string): any {
  getDb().prepare("UPDATE users SET status = ?, updated_at = datetime('now') WHERE id = ?").run(status, id);
  return getUserById(id);
}

// --- Channel Operations ---
export function createChannel(id: string, name: string, description: string, createdBy: string): any {
  getDb().prepare(
    "INSERT INTO channels (id, name, description, created_by) VALUES (?, ?, ?, ?)"
  ).run(id, name, description, createdBy);
  // Auto-join creator
  joinChannel(id, createdBy);
  return getChannelById(id);
}

export function getChannelById(id: string): any {
  return getDb().prepare("SELECT * FROM channels WHERE id = ?").get(id);
}

export function getAllChannels(): any[] {
  return getDb().prepare("SELECT * FROM channels ORDER BY created_at").all();
}

export function joinChannel(channelId: string, userId: string): void {
  getDb().prepare(
    "INSERT OR IGNORE INTO channel_members (channel_id, user_id) VALUES (?, ?)"
  ).run(channelId, userId);
}

export function leaveChannel(channelId: string, userId: string): void {
  getDb().prepare(
    "DELETE FROM channel_members WHERE channel_id = ? AND user_id = ?"
  ).run(channelId, userId);
}

export function getChannelMembers(channelId: string): any[] {
  return getDb().prepare(`
    SELECT u.* FROM users u
    JOIN channel_members cm ON u.id = cm.user_id
    WHERE cm.channel_id = ?
    ORDER BY u.username
  `).all(channelId);
}

export function getUserChannels(userId: string): any[] {
  return getDb().prepare(`
    SELECT c.* FROM channels c
    JOIN channel_members cm ON c.id = cm.channel_id
    WHERE cm.user_id = ?
    ORDER BY c.name
  `).all(userId);
}

// --- Message Operations ---
export function createMessage(id: string, channelId: string, userId: string, content: string, messageType = "text"): any {
  getDb().prepare(
    "INSERT INTO messages (id, channel_id, user_id, content, message_type) VALUES (?, ?, ?, ?, ?)"
  ).run(id, channelId, userId, content, messageType);
  return getMessageById(id);
}

export function getMessageById(id: string): any {
  return getDb().prepare(`
    SELECT m.*, u.username, u.display_name, u.avatar_url
    FROM messages m JOIN users u ON m.user_id = u.id
    WHERE m.id = ?
  `).get(id);
}

export function getChannelMessages(channelId: string, limit = 50, before?: string): any[] {
  if (before) {
    return getDb().prepare(`
      SELECT m.*, u.username, u.display_name, u.avatar_url
      FROM messages m JOIN users u ON m.user_id = u.id
      WHERE m.channel_id = ? AND m.created_at < (SELECT created_at FROM messages WHERE id = ?)
      ORDER BY m.created_at DESC LIMIT ?
    `).all(channelId, before, limit);
  }
  return getDb().prepare(`
    SELECT m.*, u.username, u.display_name, u.avatar_url
    FROM messages m JOIN users u ON m.user_id = u.id
    WHERE m.channel_id = ?
    ORDER BY m.created_at DESC LIMIT ?
  `).all(channelId, limit);
}

export function editMessage(id: string, content: string): any {
  getDb().prepare(
    "UPDATE messages SET content = ?, edited = 1, updated_at = datetime('now') WHERE id = ?"
  ).run(content, id);
  return getMessageById(id);
}

export function deleteMessage(id: string): void {
  getDb().prepare("DELETE FROM messages WHERE id = ?").run(id);
}

export function closeDb(): void {
  if (db) db.close();
}
