import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { Output, EventEmitter } from '@angular/core';
import { GoogleLoginProvider, SocialAuthService } from '@abacritt/angularx-social-login';
import { Router } from '@angular/router';

@Component({
  selector: 'app-form',
  templateUrl: './form.component.html',
  styleUrls: ['./form.component.css']
})
export class FormComponent implements OnInit {
  @Output('onLogin') onLogin = new EventEmitter()

  form!: FormGroup;
  
  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private socialAuthService: SocialAuthService,
    private router: Router
  ) { }
  
  ngOnInit(): void {
    this.form = this.formBuilder.group({
      email: '',
      password: '',
    })
  }

  submit(){
    this.authService.login(this.form.getRawValue()).subscribe(
      res => {
        this.onLogin.emit(res);
      }
    )
  }

  googleLogin(){
    this.socialAuthService.signIn(GoogleLoginProvider.PROVIDER_ID).then(
      googleUser => {
        this.authService.googleLogin({
            token: googleUser.idToken
        }).subscribe(
          (res: any )=> {
            this.authService.accessToken = res.token;
            AuthService.authEmitter.emit(true);
            this.router.navigate(['/']);
          }
        )
      }
    )
  }
}
