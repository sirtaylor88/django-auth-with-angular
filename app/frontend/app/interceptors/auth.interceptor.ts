import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  refresh = false;
  constructor(private authService: AuthService) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Clone request so we can eidt its parameter
    const req = request.clone({
      setHeaders: {
        "Authorization": `Bearer ${this.authService.accessToken}`
      }
    });
    return next.handle(req).pipe(catchError((err: HttpErrorResponse) => {
      if (err.status === 401 && !this.refresh) {
        this.refresh = true;
        return this.authService.refresh().pipe(
          switchMap((res: any) => {
            this.authService.accessToken = res.token;

            return next.handle(request.clone({
              setHeaders: {
                "Authorization": `Bearer ${this.authService.accessToken}`
              }
            }));
          })
        );
      }
      this.refresh = false;
      return throwError(() => err)
    }));
  }
}
