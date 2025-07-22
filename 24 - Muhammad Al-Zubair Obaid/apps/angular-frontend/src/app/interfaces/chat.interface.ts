// src/app/interfaces/chat.interface.ts

/**
 * Represents a single message in the chat interface.
 */
export interface ChatMessage {
  id: number;
  text: string;
  sender: 'user' | 'assistant' | 'system' | 'error';
  timestamp: Date;
  status?: 'sending' | 'sent';
}

/**
 * Represents the request sent to the Django backend.
 */
export interface SupportRequest {
  query: string;
  channel_name: string;
}

/**
 * Represents the initial response from the Django backend.
 */
export interface SupportResponse {
  initial_response: string;
  intent: string;
  entities: {
    apps?: string[];
    environment?: string;
  };
}

/**
 * A specific type for gRPC-Web errors.
 */
export interface GrpcError {
  code: number;
  message: string;
}

/**
 * Defines the shape of the data object received from gRPC streams.
 * The property names are camelCase to match the JSON representation.
 */
export interface ProgressUpdate {
  currentTask: string;
  overallPercentage: number;
  status: number;
}

/**
 * Wraps the data, error, and completion events from a gRPC stream.
 */
export interface GrpcEvent {
  type: 'data' | 'error' | 'end';
  data?: ProgressUpdate;
  error?: GrpcError;
}
