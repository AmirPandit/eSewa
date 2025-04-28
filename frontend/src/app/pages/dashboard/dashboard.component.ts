import {
  Component,
  OnInit,
  ViewChild,
  ElementRef,
  AfterViewChecked,
  OnDestroy
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import {
  CommonModule,
  DatePipe
} from '@angular/common';
import {
  FormsModule,
  NgForm
} from '@angular/forms';
import {
  MatFormFieldModule
} from '@angular/material/form-field';
import {
  MatInputModule
} from '@angular/material/input';
import {
  MatIconModule
} from '@angular/material/icon';
import {
  MatProgressSpinnerModule
} from '@angular/material/progress-spinner';
import {
  MatButtonModule
} from '@angular/material/button';
import { ChatService } from './service/chat.service';
import { environment } from '../../../environments/environment';
import { ChatWebSocketService } from '../../../service/chat-websocket.service';
import { Subscription } from 'rxjs';
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
    MatProgressSpinnerModule,
    MatButtonModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, AfterViewChecked, OnDestroy {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @ViewChild('messageInput') messageInput!: ElementRef;
  @ViewChild('messageForm') messageForm!: NgForm;
  apiUrl = environment.apiBaseUrl;
  messages: any[] = [];
  roomId: string | null = null;
  errorMessage: string = 'Connection Error';
  roomTitle: string = 'DashBoard';
  newMessage = '';
  loadingMessages = false;
  sendingMessage = false;
  errorState = false;
  shouldScrollToBottom = true;

  currentUser = 'You';
  currentUserEmail = '';
  private messageSubscription: Subscription | null = null;

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private chatService: ChatService,
    private chatWebSocketService: ChatWebSocketService,


  ) {}

  ngOnInit(): void {
    this.extractUserFromLocalStorage();
  
    this.route.params.subscribe(params => {
      this.cleanupWebSocket();
      
      this.roomId = params['room_id'];
      if (this.roomId) {
        
        this.chatWebSocketService.connect(this.roomId);
        
        
        this.loadMessages();
        this.loadRoomDetails();
        
        
        this.setupWebSocketSubscription();
      } else {
        this.resetChatState();
      }
    });
  }
  
  ngOnDestroy(): void {
    if (this.messageSubscription) {
      this.messageSubscription.unsubscribe();
    }
    this.chatWebSocketService.disconnect();
  }


  

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  extractUserFromLocalStorage(): void {
    const userDataString = localStorage.getItem('user_data');
    if (userDataString) {
      try {
        const userData = JSON.parse(userDataString);
        this.currentUser = userData.full_name || 'You';
        this.currentUserEmail = userData.email || '';
      } catch (e) {
        console.error('Failed to parse user_data', e);
        this.currentUser = 'You';
        this.currentUserEmail = '';
      }
    }
  }

  loadRoomDetails(): void {
    if (!this.roomId) return;

    this.http.get<any>(
      `${this.apiUrl}/chat/rooms/${this.roomId}/`
    ).subscribe({
      next: (room) => {
        this.roomTitle = room.name || 'Chat Room';
      },
      error: (error) => {
        console.error('Failed to load room details', error);
      }
    });
  }

  

  loadMessages(): void {
    if (!this.roomId) return;

    this.loadingMessages = true;
    this.errorState = false;
    this.shouldScrollToBottom = true;

    this.http.get<any[]>(
      `${this.apiUrl}/chat/messages/?room_id=${this.roomId}`
    ).subscribe({
      next: (messages) => {
        this.messages = messages;
        this.loadingMessages = false;
        this.shouldScrollToBottom = true;
      },
      error: (error) => {
        this.loadingMessages = false;
        this.errorState = true;
      
        const backendMsg = error?.error?.message || 'Failed to load messages. Please try again.';
        this.errorMessage = backendMsg;
      }
      
    });
  }
  


  sendMessage(): void {
    if (!this.newMessage.trim() || !this.roomId || this.sendingMessage) return;

    this.sendingMessage = true;
    
    const tempMessage = {
      id: 'temp-' + Date.now(),
      content: this.newMessage,
      sender: {
        email: this.currentUserEmail,
        first_name: 'You',
        last_name: ''
      },
      timestamp: new Date().toISOString()
    };
    
    
    this.messages = [...this.messages, tempMessage];
    this.newMessage = '';
    this.shouldScrollToBottom = true;
    
    try {
      this.chatWebSocketService.sendMessage(tempMessage.content, this.roomId);
    } catch (error) {
      this.showError('Failed to send message. Please try again.');
      
      this.messages = this.messages.filter(msg => msg.id !== tempMessage.id);
    } finally {
      this.sendingMessage = false;
      setTimeout(() => this.messageInput?.nativeElement?.focus(), 0);
    }
  }

  onEnterKeyPress(event: Event): void {
    const keyboardEvent = event as KeyboardEvent;
    if (!keyboardEvent.shiftKey) {
      keyboardEvent.preventDefault();
      this.sendMessage();
    }
  }

  scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
      }
    } catch(err) {
      console.error('Error scrolling to bottom:', err);
    }
  }

  onDelete(id: string) {
    this.chatService.deleteMembership(id).subscribe({
      next: (response) => {
        console.log('Deleted successfully', response);
        window.location.reload();
      },
      error: (error) => {
        console.error('Delete failed', error);
      }
    });
  }


  private resetChatState(): void {
    this.messages = [];
    this.errorState = false;
    this.loadingMessages = false;
    this.roomTitle = 'DashBoard';
  }

  private cleanupWebSocket(): void {
    if (this.messageSubscription) {
      this.messageSubscription.unsubscribe();
      this.messageSubscription = null;
    }
    this.chatWebSocketService.disconnect();
  }


  private showError(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 4000,
      panelClass: ['error-snackbar']
    });
  }

  trackByMessageId(index: number, message: any): string {
    return message.id;
  }
  
  private setupWebSocketSubscription(): void {
    this.messageSubscription = this.chatWebSocketService.onMessage().subscribe({
      next: (messageData) => {
        
      
        const isOurMessage = messageData.sender?.email === this.currentUserEmail;
        const tempIndex = this.messages.findIndex(msg => 
          msg.id?.startsWith('temp-') && isOurMessage
        );

        if (tempIndex !== -1) {
      
          this.messages[tempIndex] = messageData;
        } else if (!this.messages.some(msg => msg.id === messageData.id)) {
      
          this.messages.push(messageData);
        }
        
        this.shouldScrollToBottom = true;
      },
      error: (err) => {
        console.error('WebSocket error:', err);
        this.showError('Connection error. Trying to reconnect...');
        setTimeout(() => this.setupWebSocketSubscription(), 3000);
      }
    });
  }
  
  
}
