import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router); // inject Router in functional interceptor
  const authToken = localStorage.getItem('access_token');

  let authReq = req;
  if (authToken) {
    authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${authToken}`
      }
    });
  }
  return next(authReq).pipe(
    catchError((error) => {
      if (error.status === 401) {
        // Clear localStorage and navigate to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        router.navigate(['/login']);
      }
      return throwError(() => error);
    })

  );
};
