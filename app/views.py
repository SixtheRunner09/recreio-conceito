from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CadastroForm, LoginForm
from .models import Produto, Colecao


def _primeiro_nome(usuario):
    """Retorna um primeiro nome amigável para saudações."""
    base = (usuario.first_name or usuario.username).split('@')[0]
    partes = base.replace('.', ' ').replace('_', ' ').split()
    return (partes[0] if partes else base).title()


# =========================
# HOME
# =========================

def index(request):
    produtos_destaque = Produto.objects.all()[:3]
    ofertas = Produto.objects.filter(preco_antigo__isnull=False)[:4]
    colecoes = Colecao.objects.all()

    return render(request, "app/index.html", {
        "produtos_destaque": produtos_destaque,
        "ofertas": ofertas,
        "colecoes": colecoes,
    })


# =========================
# PRODUTOS
# =========================

def produtos(request):
    lista = Produto.objects.all()
    categoria = request.GET.get('categoria')

    if categoria:
        lista = lista.filter(categoria=categoria)

    return render(request, "app/produtos.html", {
        "produtos": lista,
        "categoria_selecionada": categoria,
    })


def produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)

    relacionados = (
        Produto.objects
        .filter(destaque=True)
        .exclude(pk=pk)[:4]
    )

    return render(request, "app/produto.html", {
        "produto": produto,
        "relacionados": relacionados,
    })


# =========================
# CARRINHO
# =========================

def adicionar_ao_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)

    if produto_id_str in carrinho:
        dados = carrinho[produto_id_str]

        if isinstance(dados, dict):
            dados['quantidade'] = dados.get('quantidade', 0) + 1
        else:
            carrinho[produto_id_str] = {
                'quantidade': dados + 1
            }

    else:
        carrinho[produto_id_str] = {
            'quantidade': 1
        }

    request.session['carrinho'] = carrinho
    request.session.modified = True

    return redirect('carrinho')


def carrinho(request):
    carrinho_sessao = request.session.get('carrinho', {})

    itens_carrinho = []
    total = 0

    for produto_id, dados in carrinho_sessao.items():
        produto = get_object_or_404(
            Produto,
            id=produto_id
        )

        if isinstance(dados, dict):
            quantidade = dados.get('quantidade', 1)
        else:
            quantidade = dados

        subtotal = produto.preco * quantidade
        total += subtotal

        itens_carrinho.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal,
        })

    return render(request, 'app/carrinho.html', {
        'itens_carrinho': itens_carrinho,
        'total': total,
    })


def remover_do_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)

    if produto_id_str in carrinho:
        del carrinho[produto_id_str]

        request.session['carrinho'] = carrinho
        request.session.modified = True

    return redirect('carrinho')


# =========================
# LOGIN
# =========================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    proximo = (
        request.POST.get('next')
        or request.GET.get('next', '')
    )

    if request.method == 'POST':

        form = LoginForm(
            request.POST,
            request=request
        )

        if form.is_valid():

            auth_login(
                request,
                form.user
            )

            if not request.POST.get('lembrar'):
                request.session.set_expiry(0)

            messages.success(
                request,
                f'Olá, {_primeiro_nome(form.user)}! '
                'Que bom ter você de volta.'
            )

            if (
                proximo
                and url_has_allowed_host_and_scheme(
                    proximo,
                    allowed_hosts={request.get_host()}
                )
            ):
                return redirect(proximo)

            return redirect('index')

    else:

        form = LoginForm(
            request=request
        )

    return render(
        request,
        'app/login.html',
        {
            'form': form,
            'next': proximo
        }
    )


# =========================
# CADASTRO
# =========================

def cadastro(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':

        form = CadastroForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Conta criada com sucesso! '
                'Entre com seu e-mail e senha.'
            )

            return redirect('login')

    else:

        form = CadastroForm()

    return render(
        request,
        'app/cadastro.html',
        {
            'form': form
        }
    )


# =========================
# LOGOUT
# =========================

@require_POST
def sair(request):

    auth_logout(request)

    messages.info(
        request,
        'Você saiu da sua conta. Até logo!',
        extra_tags='logout'
    )

    return redirect('index')