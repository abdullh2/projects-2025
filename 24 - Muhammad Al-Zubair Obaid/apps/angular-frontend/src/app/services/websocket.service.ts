// src/app/services/websocket.service.ts
import { Injectable, signal, WritableSignal } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { retry, catchError } from 'rxjs/operators';
import { EMPTY, Subject } from 'rxjs';
import { ProgressUpdate } from '../interfaces/chat.interface';

const WS_ENDPOINT = 'ws://localhost:8000/ws/support/';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {
  private socket$!: WebSocketSubject<any>;
  private connectionStatus: WritableSignal<boolean> = signal(false);
  private channelName: WritableSignal<string | null> = signal(null);

  public readonly isConnected = this.connectionStatus.asReadonly();
  public readonly currentChannelName = this.channelName.asReadonly();
  public progressUpdates$ = new Subject<ProgressUpdate>();

  constructor() {
    this.connect();
  }

  private connect(): void {
    this.socket$ = webSocket(WS_ENDPOINT);
    this.socket$.pipe(
      retry({ delay: 5000 }),
      catchError(error => {
        console.error('WebSocket Error:', error);
        this.connectionStatus.set(false);
        return EMPTY;
      })
    ).subscribe({
      next: (msg) => this.handleMessage(msg),
      error: (err) => console.error('WebSocket subscription error:', err),
      complete: () => {
        this.connectionStatus.set(false);
        console.warn('WebSocket connection closed.');
      }
    });
  }

  private handleMessage(msg: any): void {
    if (!this.isConnected()) {
        this.connectionStatus.set(true);
    }

    switch (msg.type) {
      case 'connection_established':
        this.channelName.set(msg.channel_name);
        console.log('WebSocket connection established with channel:', msg.channel_name);
        break;
      case 'progress_update':
        this.progressUpdates$.next(msg.payload as ProgressUpdate);
        break;
      case 'cancellation_status':
        console.log('Cancellation status received:', msg);
        break;
      default:
        console.log('Received unknown message type:', msg);
    }
  }

  /**
   * Sends a request to the backend to cancel the current operation.
   */
  sendCancelRequest(): void {
    if (this.isConnected()) {
      this.socket$.next({ type: 'cancel_operation' });
    }
  }

  closeConnection(): void {
    this.socket$.complete();
  }
}
