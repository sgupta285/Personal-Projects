import { v4 as uuidv4 } from "uuid";

// Use a test-specific database
process.env.DB_PATH = ":memory:";

import {
  getDb,
  createUser,
  getUserById,
  getUserByUsername,
  getAllUsers,
  updateUserStatus,
  createChannel,
  getChannelById,
  getAllChannels,
  joinChannel,
  getChannelMembers,
  createMessage,
  getChannelMessages,
  editMessage,
  deleteMessage,
  getMessageById,
  closeDb,
} from "../models/database";

beforeAll(() => {
  // Re-init with memory DB
  process.env.DB_PATH = ":memory:";
});

afterAll(() => {
  closeDb();
});

describe("Database - Users", () => {
  const userId = uuidv4();

  test("should create a user", () => {
    const user = createUser(userId, "testuser", "Test User");
    expect(user).toBeDefined();
    expect(user.username).toBe("testuser");
    expect(user.display_name).toBe("Test User");
    expect(user.status).toBe("offline");
  });

  test("should get user by id", () => {
    const user = getUserById(userId);
    expect(user).toBeDefined();
    expect(user.id).toBe(userId);
  });

  test("should get user by username", () => {
    const user = getUserByUsername("testuser");
    expect(user).toBeDefined();
    expect(user.username).toBe("testuser");
  });

  test("should list all users", () => {
    const users = getAllUsers();
    expect(users.length).toBeGreaterThanOrEqual(1);
  });

  test("should update user status", () => {
    const updated = updateUserStatus(userId, "online");
    expect(updated.status).toBe("online");
  });
});

describe("Database - Channels", () => {
  let userId: string;
  let channelId: string;

  beforeAll(() => {
    userId = uuidv4();
    createUser(userId, "chanuser", "Channel User");
  });

  test("should have a seed general channel", () => {
    const channels = getAllChannels();
    const general = channels.find((c: any) => c.name === "general");
    expect(general).toBeDefined();
  });

  test("should create a channel", () => {
    channelId = uuidv4();
    const ch = createChannel(channelId, "test-channel", "A test channel", userId);
    expect(ch).toBeDefined();
    expect(ch.name).toBe("test-channel");
  });

  test("should get channel by id", () => {
    const ch = getChannelById(channelId);
    expect(ch).toBeDefined();
    expect(ch.id).toBe(channelId);
  });

  test("creator should be a member", () => {
    const members = getChannelMembers(channelId);
    const found = members.find((m: any) => m.id === userId);
    expect(found).toBeDefined();
  });

  test("should add/remove members", () => {
    const otherUser = uuidv4();
    createUser(otherUser, "other", "Other User");
    joinChannel(channelId, otherUser);
    let members = getChannelMembers(channelId);
    expect(members.length).toBe(2);
  });
});

describe("Database - Messages", () => {
  let userId: string;
  let channelId: string;

  beforeAll(() => {
    userId = uuidv4();
    channelId = uuidv4();
    createUser(userId, "msguser", "Message User");
    createChannel(channelId, "msg-channel", "Message test", userId);
  });

  test("should create a message", () => {
    const msgId = uuidv4();
    const msg = createMessage(msgId, channelId, userId, "Hello, world!");
    expect(msg).toBeDefined();
    expect(msg.content).toBe("Hello, world!");
    expect(msg.username).toBe("msguser");
  });

  test("should list channel messages", () => {
    // Add a few more
    createMessage(uuidv4(), channelId, userId, "Second message");
    createMessage(uuidv4(), channelId, userId, "Third message");

    const messages = getChannelMessages(channelId);
    expect(messages.length).toBeGreaterThanOrEqual(3);
  });

  test("should edit a message", () => {
    const msgId = uuidv4();
    createMessage(msgId, channelId, userId, "Original");
    const edited = editMessage(msgId, "Edited content");
    expect(edited.content).toBe("Edited content");
    expect(edited.edited).toBe(1);
  });

  test("should delete a message", () => {
    const msgId = uuidv4();
    createMessage(msgId, channelId, userId, "To be deleted");
    deleteMessage(msgId);
    const msg = getMessageById(msgId);
    expect(msg).toBeUndefined();
  });
});
