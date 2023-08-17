import { Component } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ForgotService } from '../../services/forgot.service';

@Component({
  selector: 'app-reset',
  templateUrl: './reset.component.html',
  styleUrls: ['./reset.component.css']
})
export class ResetComponent {
  form!: FormGroup;

  constructor(
    private formBuilder: FormBuilder,
    private forgotService: ForgotService,
    private route: ActivatedRoute, // to get token from the url
    private router: Router // navigate between components
  ) { }

  ngOnInit(): void {
    this.form = this.formBuilder.group({
      password: '',
      password_confirm: ''
    })
  }
  
  submit(){
    const formData = this.form.getRawValue();
    const data = {
      ...formData,
      token: this.route.snapshot.params['token']
    };
    this.forgotService.reset(data).subscribe({
        next: () => {
          this.router.navigate(['/login']);
        }
    });
  }
}
