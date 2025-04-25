import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { Router, RouterModule } from '@angular/router';
import { CommonModule, DatePipe } from '@angular/common';

// Material Modules
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { CreateRoomDialogComponent } from './create-room-dialog/create-room-dialog/create-room-dialog.component';

interface ChatRoom {
  id: string;
  name: string;
  created_by: number;
  created_at: string;
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
    DatePipe,
    CommonModule,
    RouterModule
  ],
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.css']
})
export class LayoutComponent implements OnInit {
  rooms: ChatRoom[] = [];
  userData: UserData | null = null;

  isLoading = true;
  isCreatingRoom = false;

  constructor(
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private router: Router
    
  ) {}

  ngOnInit(): void {
    this.loadRooms();
    this.loadUserData();
  }

  private getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    };
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
      this.http.post('http://127.0.0.1:8000/api/v1/accounts/logout/', {
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
    this.http.get<ChatRoom[]>('http://127.0.0.1:8000/api/v1/chat/rooms/', this.getAuthHeaders())
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
      'http://127.0.0.1:8000/api/v1/chat/rooms/create/', 
      { name }, 
      this.getAuthHeaders()
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
}