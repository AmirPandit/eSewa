import { Routes } from '@angular/router';
import { LayoutComponent } from './pages/layout/layout.component';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { AuthGuard } from '../service/auth.guard';
import { RegisterComponent } from './pages/register/register.component';

export const routes: Routes = [
    {
        path:'',
        redirectTo:'login',
        pathMatch:'full'   
    },
    {
        path:'login',
        component :LoginComponent
    },
    {
        path:'register',
        component :RegisterComponent
    },
    { 
      path: 'dashboard',
      component: LayoutComponent,
      canActivate: [AuthGuard],
      children: [
        { path: '', component: DashboardComponent },
        { path: ':room_id', component: DashboardComponent }
      ]
      },
  
        ];
