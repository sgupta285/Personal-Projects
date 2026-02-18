import { v4 as uuidv4 } from "uuid";
import * as db from "../models/database";
import { publishEvent, CHANNELS } from "../utils/redis";

export const resolvers = {
  Query: {
    me: (_: any, { userId }: { userId: string }) => db.getUserById(userId),
    users: () => db.getAllUsers(),
    user: (_: any, { id }: { id: string }) => db.getUserById(id),
    channels: () => db.getAllChannels(),
    channel: (_: any, { id }: { id: string }) => db.getChannelById(id),
    userChannels: (_: any, { userId }: { userId: string }) => db.getUserChannels(userId),
    messages: (_: any, { channelId, limit, before }: { channelId: string; limit?: number; before?: string }) =>
      db.getChannelMessages(channelId, limit || 50, before),
  },

  Channel: {
    members: (channel: any) => db.getChannelMembers(channel.id),
    messages: (channel: any, { limit, before }: { limit?: number; before?: string }) =>
      db.getChannelMessages(channel.id, limit || 50, before),
    is_private: (channel: any) => Boolean(channel.is_private),
  },

  Message: {
    edited: (message: any) => Boolean(message.edited),
  },

  Mutation: {
    register: (_: any, { username, displayName }: { username: string; displayName: string }) => {
      const existing = db.getUserByUsername(username);
      if (existing) return existing;
      const id = uuidv4();
      const user = db.createUser(id, username, displayName);
      // Auto-join general channel
      const channels = db.getAllChannels();
      const general = channels.find((c: any) => c.name === "general");
      if (general) db.joinChannel(general.id, id);
      publishEvent(CHANNELS.USER_PRESENCE, { userId: id, username, status: "online" });
      return user;
    },

    updateStatus: (_: any, { userId, status }: { userId: string; status: string }) => {
      const user = db.updateUserStatus(userId, status);
      publishEvent(CHANNELS.USER_PRESENCE, { userId, status });
      return user;
    },

    createChannel: (_: any, { name, description, userId }: { name: string; description?: string; userId: string }) => {
      const id = uuidv4();
      const channel = db.createChannel(id, name, description || "", userId);
      publishEvent(CHANNELS.CHANNEL_UPDATE, { type: "created", channel });
      return channel;
    },

    joinChannel: (_: any, { channelId, userId }: { channelId: string; userId: string }) => {
      db.joinChannel(channelId, userId);
      publishEvent(CHANNELS.CHANNEL_UPDATE, { type: "member_joined", channelId, userId });
      return true;
    },

    leaveChannel: (_: any, { channelId, userId }: { channelId: string; userId: string }) => {
      db.leaveChannel(channelId, userId);
      publishEvent(CHANNELS.CHANNEL_UPDATE, { type: "member_left", channelId, userId });
      return true;
    },

    sendMessage: (_: any, { channelId, userId, content }: { channelId: string; userId: string; content: string }) => {
      const id = uuidv4();
      const message = db.createMessage(id, channelId, userId, content);
      publishEvent(CHANNELS.NEW_MESSAGE, { channelId, message });
      return message;
    },

    editMessage: (_: any, { messageId, content }: { messageId: string; content: string }) => {
      const message = db.editMessage(messageId, content);
      publishEvent(CHANNELS.EDIT_MESSAGE, { message });
      return message;
    },

    deleteMessage: (_: any, { messageId }: { messageId: string }) => {
      const msg = db.getMessageById(messageId);
      db.deleteMessage(messageId);
      if (msg) publishEvent(CHANNELS.DELETE_MESSAGE, { messageId, channelId: msg.channel_id });
      return true;
    },
  },
};
