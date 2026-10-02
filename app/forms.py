from django import forms
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError

User = get_user_model()


class CadastroForm(forms.Form):
    nome = forms.CharField(max_length=150, error_messages={'required': 'Informe seu nome.'})
    sobrenome = forms.CharField(max_length=150, error_messages={'required': 'Informe seu sobrenome.'})
    email = forms.EmailField(error_messages={'required': 'Informe seu e-mail.', 'invalid': 'Informe um e-mail válido.'})
    senha = forms.CharField(error_messages={'required': 'Crie uma senha.'})
    confirmar_senha = forms.CharField(error_messages={'required': 'Confirme sua senha.'})
    aceite_termos = forms.BooleanField(error_messages={'required': 'Você precisa aceitar os termos para continuar.'})

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(username__iexact=email).exists():
            raise ValidationError('Já existe uma conta com este e-mail.')
        return email

    def clean(self):
        cleaned = super().clean()
        senha = cleaned.get('senha')
        confirmar = cleaned.get('confirmar_senha')
        if senha and confirmar and senha != confirmar:
            self.add_error('confirmar_senha', 'As senhas não coincidem.')
        if senha:
            try:
                password_validation.validate_password(senha)
            except ValidationError as e:
                self.add_error('senha', e)
        return cleaned

    def save(self):
        d = self.cleaned_data
        return User.objects.create_user(
            username=d['email'],
            email=d['email'],
            password=d['senha'],
            first_name=d['nome'],
            last_name=d['sobrenome'],
        )


class LoginForm(forms.Form):
    email = forms.EmailField(error_messages={'required': 'Informe seu e-mail.', 'invalid': 'Informe um e-mail válido.'})
    senha = forms.CharField(error_messages={'required': 'Informe sua senha.'})

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        senha = cleaned.get('senha')
        if email and senha:
            self.user = authenticate(self.request, username=email.strip().lower(), password=senha)
            if self.user is None:
                raise ValidationError('E-mail ou senha incorretos.')
        return cleaned