// src/app/services/grpc-web.service.ts
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { SupportServiceClient } from '../protos/SupportServiceClientPb';
import { InstallAppsRequest, InstallEnvironmentRequest, ProgressUpdate } from '../protos/support_pb';
import { GrpcEvent, GrpcError, ProgressUpdate as ProgressUpdateInterface } from '../interfaces/chat.interface';

@Injectable({ providedIn: 'root' })
export class GrpcWebService {
  private readonly client: SupportServiceClient;
  private readonly grpcWebServerUrl = 'http://localhost:5220';

  constructor() {
    this.client = new SupportServiceClient(this.grpcWebServerUrl);
  }

  installApps(appIds: string[]): Observable<GrpcEvent> {
    const request = new InstallAppsRequest();
    request.setAppIdsList(appIds);
    return this._executeStream(this.client.installApps(request, {}));
  }

  installEnvironment(envId: string): Observable<GrpcEvent> {
    const request = new InstallEnvironmentRequest();
    request.setEnvironmentId(envId);
    return this._executeStream(this.client.installEnvironment(request, {}));
  }

  private _executeStream(stream: any): Observable<GrpcEvent> {
    return new Observable(observer => {
      console.log('[gRPC-Web] Starting stream...');
      
      stream.on('data', (response: ProgressUpdate) => {
        const progressData: ProgressUpdateInterface = {
            currentTask: response.getCurrentTask(),
            overallPercentage: response.getOverallPercentage(),
            status: response.getStatus()
        };
        console.log('[gRPC-Web] Received data:', progressData);
        observer.next({ type: 'data', data: progressData });
      });

      stream.on('error', (err: any) => {
        console.error('[gRPC-Web] Stream error:', err);
        const error: GrpcError = { code: err.code, message: err.message };
        observer.error({ type: 'error', error: error });
      });

      stream.on('end', () => {
        console.log('[gRPC-Web] Stream ended.');
        observer.complete();
      });

      // Return a teardown logic to cancel the stream
      return () => {
        console.log('[gRPC-Web] Cancelling stream.');
        stream.cancel();
      };
    });
  }
}
