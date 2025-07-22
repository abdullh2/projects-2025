// src/app/app.component.ts
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatInterfaceComponent } from './components/chat-interface/chat-interface.component';
import { WebsocketService } from './services/websocket.service';
import 'zone.js';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ChatInterfaceComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  // Inject the WebSocket service to initialize it and make its properties
  // available to the template.
  public readonly websocketService = inject(WebsocketService);
}
