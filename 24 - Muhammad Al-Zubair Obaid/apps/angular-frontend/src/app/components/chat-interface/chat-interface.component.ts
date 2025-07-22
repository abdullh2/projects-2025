// src/app/components/chat-interface/chat-interface.component.ts
import { Component, ChangeDetectionStrategy, inject, signal, WritableSignal, effect, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable, Subscription } from 'rxjs';

import { SupportApiService } from '../../services/support-api.service';
import { WebsocketService } from '../../services/websocket.service';
import { GrpcWebService } from '../../services/grpc-web.service';
import { ChatMessage, GrpcEvent, ProgressUpdate } from '../../interfaces/chat.interface';

@Component({
  selector: 'app-chat-interface',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-interface.component.html',
  styleUrls: ['./chat-interface.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatInterfaceComponent implements OnDestroy {
  private readonly apiService = inject(SupportApiService);
  public readonly websocketService = inject(WebsocketService);
  private readonly grpcWebService = inject(GrpcWebService);

  messages = signal<ChatMessage[]>([]);
  userInput = signal('');
  isLoading = signal(false);
  
  // FIX: Added a dedicated signal to hold the state of the current, in-flight operation.
  currentProgress = signal<ProgressUpdate | null>(null);
  
  private activeGrpcSubscription: Subscription | null = null;

  @ViewChild('chatContainer') private chatContainer!: ElementRef;

  constructor() {
    effect(() => { if (this.messages()) this.scrollToBottom(); });
  }

  sendMessage(): void {
    const query = this.userInput().trim();
    const channelName = this.websocketService.currentChannelName();
    if (!query || this.isLoading() || !channelName) return;

    this.messages.update(m => [...m, { id: Date.now(), text: query, sender: 'user', timestamp: new Date() }]);
    this.userInput.set('');
    this.isLoading.set(true);
    this.currentProgress.set(null); // Clear any previous progress bar

    this.apiService.sendQuery({ query, channel_name: channelName }).subscribe({
      next: (res) => {
        this.messages.update(m => [...m, { id: Date.now(), text: res.initial_response, sender: 'assistant', timestamp: new Date() }]);
        
        if (res.intent === 'app_installation' && res.entities.apps?.length) {
          this.executeGrpcStream(this.grpcWebService.installApps(res.entities.apps));
        } else if (res.intent === 'environment_setup' && res.entities.environment) {
          this.executeGrpcStream(this.grpcWebService.installEnvironment(res.entities.environment));
        } else {
          this.isLoading.set(false);
        }
      },
      error: (err) => {
        const errorText = err.error?.details || 'Could not connect to the AI service.';
        this.messages.update(m => [...m, { id: Date.now(), text: errorText, sender: 'error', timestamp: new Date() }]);
        this.isLoading.set(false);
      }
    });
  }

  private executeGrpcStream(stream$: Observable<GrpcEvent>): void {
    this.activeGrpcSubscription = stream$.subscribe({
      next: (event: GrpcEvent) => {
        if (event.data) {
          const data = event.data as ProgressUpdate;
          // FIX: Instead of pushing to the main message array, update the dedicated signal.
          // This keeps the progress bar on a single line.
          this.currentProgress.set(data);
        }
      },
      error: (err: GrpcEvent) => {
        if (err.error) {
          const errorMessage: ChatMessage = {
            id: Date.now(), sender: 'error',
            text: `gRPC Error: ${err.error.message} (Code: ${err.error.code})`,
            timestamp: new Date(),
          };
          this.messages.update(msgs => [...msgs, errorMessage]);
        }
        this.isLoading.set(false);
        this.currentProgress.set(null); // Clear progress on error
      },
      complete: () => {
        const finalProgress = this.currentProgress();
        if (finalProgress) {
            // Add the final, completed message to the permanent chat history.
            const finalMessage: ChatMessage = {
                id: Date.now(),
                sender: 'system',
                text: finalProgress.currentTask,
                timestamp: new Date()
            };
            this.messages.update(m => [...m, finalMessage]);
        }
        this.isLoading.set(false);
        this.currentProgress.set(null); // Clear progress on completion
        this.activeGrpcSubscription = null;
      }
    });
  }

  cancelOperation(): void {
    if (this.activeGrpcSubscription) {
      this.activeGrpcSubscription.unsubscribe();
      this.activeGrpcSubscription = null;
      const systemMessage: ChatMessage = {
        id: Date.now(), sender: 'system', text: 'Operation cancelled.', timestamp: new Date(),
      };
      this.messages.update(msgs => [...msgs, systemMessage]);
      this.isLoading.set(false);
      this.currentProgress.set(null);
    }
  }

  ngOnDestroy(): void { this.cancelOperation(); }
  private scrollToBottom(): void { try { setTimeout(() => this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight, 0); } catch {} }
}
