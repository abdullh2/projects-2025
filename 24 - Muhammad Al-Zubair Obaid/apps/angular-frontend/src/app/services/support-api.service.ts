import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SupportRequest, SupportResponse } from '../interfaces/chat.interface';

@Injectable({ providedIn: 'root' })
export class SupportApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api';

  sendQuery(request: SupportRequest): Observable<SupportResponse> {
    return this.http.post<SupportResponse>(`${this.apiUrl}/ai-request/`, request);
  }
}
