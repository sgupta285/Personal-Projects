import gql from "graphql-tag";

export const typeDefs = gql`
  type User {
    id: ID!
    username: String!
    display_name: String!
    avatar_url: String
    status: String!
    created_at: String!
    updated_at: String!
  }

  type Channel {
    id: ID!
    name: String!
    description: String
    created_by: String!
    is_private: Boolean!
    created_at: String!
    updated_at: String!
    members: [User!]!
    messages(limit: Int, before: String): [Message!]!
  }

  type Message {
    id: ID!
    channel_id: String!
    user_id: String!
    content: String!
    message_type: String!
    edited: Boolean!
    created_at: String!
    updated_at: String!
    username: String
    display_name: String
    avatar_url: String
  }

  type Query {
    me(userId: ID!): User
    users: [User!]!
    user(id: ID!): User
    channels: [Channel!]!
    channel(id: ID!): Channel
    userChannels(userId: ID!): [Channel!]!
    messages(channelId: ID!, limit: Int, before: String): [Message!]!
  }

  type Mutation {
    register(username: String!, displayName: String!): User!
    updateStatus(userId: ID!, status: String!): User!
    createChannel(name: String!, description: String, userId: ID!): Channel!
    joinChannel(channelId: ID!, userId: ID!): Boolean!
    leaveChannel(channelId: ID!, userId: ID!): Boolean!
    sendMessage(channelId: ID!, userId: ID!, content: String!): Message!
    editMessage(messageId: ID!, content: String!): Message!
    deleteMessage(messageId: ID!): Boolean!
  }
`;
