from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "login-form-field"})
        self.fields["password"].widget.attrs.update({"class": "login-form-field"})
