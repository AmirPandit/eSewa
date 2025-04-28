import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { CommonModule, DatePipe } from '@angular/common';

import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { CreateRoomDialogComponent } from './create-room-dialog/create-room-dialog/create-room-dialog.component';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

interface ChatRoom {
  id: string;
  name: string;
  created_by: number;
  created_at: string;
  is_member: boolean;
  members_count: number;
}

interface Message {
  id: string;
  room: string;
  content: string;
  sender: string;
  timestamp: string;
}

interface UserData {
  full_name: string;
  email: string;
  role: string;
  username: string;
}

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    CommonModule,
    FormsModule,
    RouterModule
  ],
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.css']
})

export class LayoutComponent implements OnInit {
  apiUrl = environment.apiBaseUrl;
  rooms: ChatRoom[] = [];
  activeRoomId: string | null = null;
  activeRoom: ChatRoom | null = null;
  userData: any = null;
  
  isLoading = true;
  isCreatingRoom = false;
  isJoiningRoom = false;
  currentJoiningRoomId: string | null = null;

  constructor(
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.loadRooms();
    this.loadUserData();
    
    this.route.params.subscribe(params => {
      if (params['room_id']) {
        this.activeRoomId = params['room_id'];
        if (this.activeRoomId) {
          this.loadRoomDetails(this.activeRoomId);
        }
      }
    });
  } 
  loadRoomDetails(roomId: string): void {
    const room = this.rooms.find(r => r.id === roomId);
    if (room) {
      this.activeRoom = room;
    }
  }

  setActiveRoom(roomId: string): void {
    this.activeRoomId = roomId;
  }

  loadUserData(): void {
    const userDataString = localStorage.getItem('user_data');
    if (userDataString) {
      this.userData = JSON.parse(userDataString);
    }
  }

  logout(): void {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (refreshToken) {
      this.http.post(`${this.apiUrl}/accounts/logout/`, {
        refresh_token: refreshToken
      }).subscribe({
        next: () => {
          this.clearLocalStorage();
          this.router.navigate(['/login']);
          this.snackBar.open('Logged out successfully', 'Close', { duration: 3000 });
        },
        error: (error) => {
          this.clearLocalStorage();
          this.router.navigate(['/login']);
          this.snackBar.open('Logged out', 'Close', { duration: 3000 });
        }
      });
    } else {
      this.clearLocalStorage();
      this.router.navigate(['/login']);
    }
  }

  private clearLocalStorage(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    this.userData = null;
  }
  
  loadRooms(): void {
    this.isLoading = true;
    this.http.get<ChatRoom[]>(`${this.apiUrl}/chat/rooms/`)
      .subscribe({
        next: (rooms) => {
          this.rooms = rooms;
          this.isLoading = false;
        },
        error: (error) => {
          if (error.status === 401) {
            this.router.navigate(['/login']);
          }
          this.snackBar.open('Failed to load rooms', 'Close', { duration: 3000 });
          this.isLoading = false;
        }
      });
  }

  openCreateRoomDialog(): void {
    const dialogRef = this.dialog.open(CreateRoomDialogComponent, {
      width: '400px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.createRoom(result);
      }
    });
  }

  createRoom(name: string): void {
    this.isCreatingRoom = true;
    this.http.post(
      `${this.apiUrl}/chat/rooms/create/`, 
      { name }
    ).subscribe({
      next: () => {
        this.snackBar.open('Room created successfully', 'Close', { duration: 3000 });
        this.loadRooms();
      },
      error: (error) => {
        if (error.status === 401) {
          this.router.navigate(['/login']);
        }
        this.snackBar.open('Failed to create room', 'Close', { duration: 3000 });
      }
    }).add(() => {
      this.isCreatingRoom = false;
    });
  }

  joinRoom(roomId: string): void {
    this.isJoiningRoom = true;
    this.currentJoiningRoomId = roomId;
    
    this.http.post(
      `${this.apiUrl}/chat/rooms/${roomId}/join/`,
      {}
    ).subscribe({
      next: () => {
        this.snackBar.open('Successfully joined room', 'Close', { duration: 3000 });
        this.loadRooms(); // Refresh the room list
      },
      error: (error) => {
        if (error.status === 401) {
          this.router.navigate(['/login']);
        }
        this.snackBar.open('Failed to join room', 'Close', { duration: 3000 });
      },
      complete: () => {
        this.isJoiningRoom = false;
        this.currentJoiningRoomId = null;
      }
    });
  }

  isJoiningCurrentRoom(roomId: string): boolean {
    return this.isJoiningRoom && this.currentJoiningRoomId === roomId;
  }
}