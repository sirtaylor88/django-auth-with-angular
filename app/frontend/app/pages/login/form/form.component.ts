import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { Output, EventEmitter } from '@angular/core';

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
}
