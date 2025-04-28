import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  apiUrl = environment.apiBaseUrl;
  constructor(private http: HttpClient) {}

  deleteMembership(id: string) {
    return this.http.delete(`${this.apiUrl}/chat/memberships/${id}/unsubscribe/`);
  }
}
