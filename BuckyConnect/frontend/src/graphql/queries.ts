import { gql } from "@apollo/client";

export const REGISTER_USER = gql`
  mutation Register($username: String!, $displayName: String!) {
    register(username: $username, displayName: $displayName) {
      id
      username
      display_name
      status
    }
  }
`;

export const GET_CHANNELS = gql`
  query GetChannels {
    channels {
      id
      name
      description
      created_at
    }
  }
`;

export const GET_CHANNEL = gql`
  query GetChannel($id: ID!) {
    channel(id: $id) {
      id
      name
      description
      members {
        id
        username
        display_name
        status
      }
    }
  }
`;

export const GET_MESSAGES = gql`
  query GetMessages($channelId: ID!, $limit: Int, $before: String) {
    messages(channelId: $channelId, limit: $limit, before: $before) {
      id
      channel_id
      user_id
      content
      message_type
      edited
      created_at
      username
      display_name
      avatar_url
    }
  }
`;

export const SEND_MESSAGE = gql`
  mutation SendMessage($channelId: ID!, $userId: ID!, $content: String!) {
    sendMessage(channelId: $channelId, userId: $userId, content: $content) {
      id
      content
      created_at
      username
      display_name
    }
  }
`;

export const CREATE_CHANNEL = gql`
  mutation CreateChannel($name: String!, $description: String, $userId: ID!) {
    createChannel(name: $name, description: $description, userId: $userId) {
      id
      name
      description
    }
  }
`;

export const JOIN_CHANNEL = gql`
  mutation JoinChannel($channelId: ID!, $userId: ID!) {
    joinChannel(channelId: $channelId, userId: $userId)
  }
`;

export const GET_USERS = gql`
  query GetUsers {
    users {
      id
      username
      display_name
      status
    }
  }
`;
