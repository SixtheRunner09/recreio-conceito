from django import forms
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import Colecao, Produto

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
    # Aceita e-mail (qualquer cliente) ou nome de usuário (somente admin/is_staff).
    email = forms.CharField(error_messages={'required': 'Informe seu e-mail.'})
    senha = forms.CharField(error_messages={'required': 'Informe sua senha.'})

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user = None

        # O template envia o campo como "password"; o form usa "senha".
        if args and args[0] is not None and 'senha' not in args[0] and 'password' in args[0]:
            dados = args[0].copy()
            dados['senha'] = dados['password']
            args = (dados,) + args[1:]

        super().__init__(*args, **kwargs)

    def _autenticar(self, identificador, senha):
        erro = ValidationError('E-mail ou senha incorretos.')

        # --- Com "@": login por e-mail ---
        if '@' in identificador:
            try:
                validate_email(identificador)
            except ValidationError:
                raise ValidationError('Informe um e-mail válido.')

            email = identificador.lower()

            # Cliente comum: o username é o próprio e-mail
            user = authenticate(self.request, username=email, password=senha)
            if user is not None:
                return user

            # Admin com username diferente do e-mail (ex.: AdminMaster)
            admin = User.objects.filter(email__iexact=email, is_staff=True).first()
            if admin:
                return authenticate(
                    self.request,
                    username=admin.get_username(),
                    password=senha,
                ) or self._falhar(erro)

            raise erro

        # --- Sem "@": login por usuário, SÓ para admin ---
        admin = User.objects.filter(username__iexact=identificador, is_staff=True).first()
        if admin is None:
            raise erro

        user = authenticate(
            self.request,
            username=admin.get_username(),
            password=senha,
        )
        if user is None:
            raise erro
        return user

    @staticmethod
    def _falhar(erro):
        raise erro

    def clean(self):
        cleaned = super().clean()
        identificador = (cleaned.get('email') or '').strip()
        senha = cleaned.get('senha')
        if identificador and senha:
            self.user = self._autenticar(identificador, senha)
        return cleaned


def _aplicar_classe_campo(form):
    """Põe class="campo" nos inputs (menos checkboxes), como o painel espera."""
    sem_classe = (forms.CheckboxInput, forms.CheckboxSelectMultiple)
    for campo in form.fields.values():
        if not isinstance(campo.widget, sem_classe):
            campo.widget.attrs.setdefault('class', 'campo')


class ProdutoForm(forms.ModelForm):
    """Formulário de cadastro/edição de produtos no painel."""

    class Meta:
        model = Produto
        fields = '__all__'
        labels = {
            'imagem': 'Foto principal',
            'colecoes': 'Coleções',
        }
        widgets = {
            'colecoes': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_classe_campo(self)


class ColecaoForm(forms.ModelForm):
    """Formulário de criação de coleções no painel."""

    class Meta:
        model = Colecao
        fields = ['nome', 'descricao', 'imagem', 'ordem']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_classe_campo(self)