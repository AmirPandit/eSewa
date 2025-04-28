import { Injectable } from '@angular/core';
import { environment } from '../environments/environment';
import { io, Socket } from 'socket.io-client';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ChatWebSocketService {
  private socket: Socket | null = null;
  private connected = false;
  private messageSubject = new Subject<any>();

  connect(roomId: string): void {
    this.disconnect();

    const token = localStorage.getItem('access_token');
    const socketUrl = `${environment.socketUrl}`;
    
    this.socket = io(socketUrl, {
      path: '/socket.io',
      transports: ['websocket'],
      auth: { token },
      query: { roomId, token },
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000
    });

    this.socket.on('connect', () => {
      this.connected = true;
      this.socket?.emit('join_room', { room_id: roomId });
    });

    this.socket.on('disconnect', () => {
      this.connected = false;
    });

    this.socket.on('connect_error', (err) => {
      console.error('Connection error:', err.message);
      this.connected = false;
    });

    this.socket.on('receive_message', (data: any) => {
      this.messageSubject.next(this.normalizeMessage(data));
    });

    this.socket.onAny((event, ...args) => {
      });
  }


  private normalizeMessage(data: any): any {
    return {
      id: data.id || `ws-${Date.now()}`,
      content: data.content,
      sender: data.sender || {
        email: data.email ,
        first_name: data.first_name ,
        last_name: data.last_name 
      },
      timestamp: data.timestamp || new Date().toISOString()
    };
  }


  sendMessage(content: string, roomId: string): void {
    if (!this.connected || !this.socket) {
      throw new Error('Not connected to WebSocket');
    }
    
    this.socket.emit('send_message', {
      room_id: roomId,
      content,
      token: localStorage.getItem('access_token')
    });
  }

  onMessage(): Observable<any> {
    return this.messageSubject.asObservable();
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }
}