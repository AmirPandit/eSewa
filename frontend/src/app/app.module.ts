import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { authInterceptor } from '../interceptors/auth.interceptor';  // Your interceptor file
import { NgModule } from '@angular/core';

@NgModule({
  providers: [
    { provide: HTTP_INTERCEPTORS, useFactory: authInterceptor, multi: true },
  ],
})
export class AppModule { }
