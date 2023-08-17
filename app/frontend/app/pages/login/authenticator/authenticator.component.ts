import { Component } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { Input } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-authenticator',
  templateUrl: './authenticator.component.html',
  styleUrls: ['./authenticator.component.css']
})
export class AuthenticatorComponent {
  @Input('loginData') loginData = {
    id: 0,
    img: ''
  };

  form!: FormGroup;
  
  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) { }
  ngOnInit(): void {
    this.form = this.formBuilder.group({
      code: '',
    })
  }
  submit(){
    const formData = this.form.getRawValue();
    const data = this.loginData;

    this.authService.authenticatorLogin({
      ...data,
      ...formData
    }).subscribe(
      (res: any )=> {
        this.authService.accessToken = res.token;
        AuthService.authEmitter.emit(true);
        this.router.navigate(['/']);
      }
    )
  }
}
