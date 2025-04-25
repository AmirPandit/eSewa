
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [ 
    DatePipe, 
    FormsModule, 
    CommonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  messages: any[] = [];
  roomId: string | null = null;
  newMessage = '';
  loadingMessages = false;

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.roomId = params['room_id'];
      if (this.roomId) {
        this.loadMessages();
      }
    });
  }

  loadMessages(): void {
    if (!this.roomId) return;
    
    this.loadingMessages = true;
    this.http.get<any[]>(`http://127.0.0.1:8000/api/v1/chat/messages/?room_id=${this.roomId}`, this.getAuthHeaders())
      .subscribe({
        next: (messages) => {
          this.messages = messages;
          this.loadingMessages = false;
        },
        error: (error) => {
          this.snackBar.open('Failed to load messages', 'Close', { duration: 3000 });
          this.loadingMessages = false;
        }
      });
  }

  sendMessage(): void {
    if (!this.newMessage.trim() || !this.roomId) return;
    
    const payload = {
      room: this.roomId,
      content: this.newMessage
    };
    
    this.http.post('http://127.0.0.1:8000/api/v1/chat/messages/', payload, this.getAuthHeaders())
      .subscribe({
        next: (res: any) => {
          this.messages.push(res);
          this.newMessage = '';
        },
        error: (error) => {
          this.snackBar.open('Failed to send message', 'Close', { duration: 3000 });
        }
      });
  }

  private getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    };
  }
}