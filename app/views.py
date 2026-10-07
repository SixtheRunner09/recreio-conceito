from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CadastroForm, ColecaoForm, LoginForm, ProdutoForm
from .models import Colecao, Produto, ProdutoImagem


def _primeiro_nome(usuario):
    """Retorna um primeiro nome amigável para saudações."""
    base = (usuario.first_name or usuario.username).split('@')[0]
    partes = base.replace('.', ' ').replace('_', ' ').split()
    return (partes[0] if partes else base).title()


def _colecoes_com_total():
    """Coleções com a quantidade de peças de cada uma."""
    return Colecao.objects.annotate(total=Count('produtos'))


# =========================
# HOME
# =========================

def index(request):
    produtos_destaque = Produto.objects.prefetch_related('imagens')[:3]
    ofertas = (
        Produto.objects
        .filter(preco_antigo__isnull=False)
        .prefetch_related('imagens')[:4]
    )

    return render(request, "app/index.html", {
        "produtos_destaque": produtos_destaque,
        "ofertas": ofertas,
        "colecoes": _colecoes_com_total(),
    })


# =========================
# PRODUTOS
# =========================

def produtos(request):
    lista = Produto.objects.prefetch_related('imagens')
    categoria = request.GET.get('categoria')

    if categoria:
        lista = lista.filter(categoria=categoria)

    return render(request, "app/produtos.html", {
        "produtos": lista,
        "categoria_selecionada": categoria,
    })


def produto(request, pk):
    produto = get_object_or_404(
        Produto.objects.prefetch_related('imagens'), pk=pk
    )

    relacionados = (
        Produto.objects
        .filter(destaque=True)
        .exclude(pk=pk)
        .prefetch_related('imagens')[:4]
    )

    return render(request, "app/produto.html", {
        "produto": produto,
        "relacionados": relacionados,
    })


# =========================
# COLEÇÕES (SITE)
# =========================

def colecoes_lista(request):
    return render(request, 'app/colecoes.html', {
        'colecoes': _colecoes_com_total(),
    })


def colecao_detalhe(request, pk):
    colecao = get_object_or_404(Colecao, pk=pk)
    return render(request, 'app/colecao_detalhe.html', {
        'colecao': colecao,
        'produtos': colecao.produtos.prefetch_related('imagens'),
    })


# =========================
# CARRINHO
# =========================

def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)

    if produto.esgotado:
        messages.error(
            request,
            f'“{produto.nome}” está indisponível no momento.'
        )
        return redirect('produto', pk=produto.pk)

    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)

    dados = carrinho.get(produto_id_str)
    if isinstance(dados, dict):
        quantidade_atual = dados.get('quantidade', 0)
    else:
        quantidade_atual = dados or 0

    # Não deixa passar do estoque disponível
    if quantidade_atual + 1 > produto.estoque:
        messages.warning(
            request,
            f'Só temos {produto.estoque} '
            f'unidade{"s" if produto.estoque != 1 else ""} '
            f'de “{produto.nome}”.'
        )
        return redirect('carrinho')

    carrinho[produto_id_str] = {'quantidade': quantidade_atual + 1}

    request.session['carrinho'] = carrinho
    request.session.modified = True

    return redirect('carrinho')


def carrinho(request):
    carrinho_sessao = request.session.get('carrinho', {})

    # Uma única consulta para todos os produtos da sacola
    produtos_por_id = Produto.objects.prefetch_related('imagens').in_bulk(
        [int(pk) for pk in carrinho_sessao]
    )

    itens_carrinho = []
    total = 0
    removidos = []

    for produto_id, dados in carrinho_sessao.items():
        produto = produtos_por_id.get(int(produto_id))

        # Produto excluído no painel: ignora o item e limpa da sessão
        if produto is None:
            removidos.append(produto_id)
            continue

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

    if removidos:
        for produto_id in removidos:
            del carrinho_sessao[produto_id]
        request.session['carrinho'] = carrinho_sessao
        request.session.modified = True

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
# CURTIDOS
# =========================

@require_POST
def alternar_curtida(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)

    curtidos = request.session.get('curtidos', [])

    if produto_id in curtidos:
        curtidos.remove(produto_id)
        curtiu = False
        messages.info(
            request,
            f'“{produto.nome}” foi removido dos seus curtidos.'
        )
    else:
        curtidos.append(produto_id)
        curtiu = True
        messages.success(
            request,
            f'“{produto.nome}” foi adicionado aos seus curtidos.'
        )

    request.session['curtidos'] = curtidos
    request.session.modified = True

    # Curtiu -> leva para a página de curtidos.
    # Descurtiu -> volta para a página de onde veio.
    proximo = request.POST.get('next', '')
    if (
        not curtiu
        and proximo
        and url_has_allowed_host_and_scheme(
            proximo, allowed_hosts={request.get_host()}
        )
    ):
        return redirect(proximo)

    return redirect('curtidos')


def curtidos(request):
    ids = request.session.get('curtidos', [])
    lista = Produto.objects.filter(pk__in=ids).prefetch_related('imagens')

    return render(request, 'app/curtidos.html', {
        'produtos': lista,
    })


# =========================
# LOGIN
# =========================

def _destino_padrao(usuario):
    """Admin (is_staff) vai pro painel; cliente vai pra home."""
    return 'painel' if usuario.is_staff else 'index'


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_destino_padrao(request.user))

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

            return redirect(_destino_padrao(form.user))

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


# =========================
# PAINEL (ADMIN DO SITE)
# =========================

def _saudacao():
    hora = timezone.localtime().hour
    if hora < 12:
        return 'Bom dia'
    return 'Boa tarde' if hora < 18 else 'Boa noite'


@staff_member_required(login_url='login')
def painel(request):
    numeros = Produto.objects.aggregate(
        total=Count('id'),
        em_oferta=Count('id', filter=Q(preco_antigo__isnull=False)),
        destaques=Count('id', filter=Q(destaque=True)),
    )
    numeros['colecoes'] = Colecao.objects.count()

    return render(request, 'app/painel.html', {
        'saudacao': _saudacao(),
        'nome': _primeiro_nome(request.user),
        'numeros': numeros,
        'recentes': Produto.objects.order_by('-id')[:5],
    })


@staff_member_required(login_url='login')
def painel_produtos(request):
    return render(request, 'app/painel_produtos.html', {
        'produtos': Produto.objects.order_by('-id'),
    })


@staff_member_required(login_url='login')
def painel_produto_form(request, pk=None):
    instancia = get_object_or_404(Produto, pk=pk) if pk else None
    editando = instancia is not None
    form = ProdutoForm(
        request.POST or None,
        request.FILES or None,
        instance=instancia,
    )

    if request.method == 'POST' and form.is_valid():
        produto_salvo = form.save()   # já salva também as coleções marcadas

        # Remove as fotos extras marcadas para exclusão
        if editando:
            ids = request.POST.getlist('remover_imagens')
            if ids:
                produto_salvo.imagens.filter(pk__in=ids).delete()

        # Adiciona as novas fotos extras (campo name="imagens", multiple)
        proxima_ordem = produto_salvo.imagens.count()
        for i, arquivo in enumerate(request.FILES.getlist('imagens')):
            ProdutoImagem.objects.create(
                produto=produto_salvo,
                imagem=arquivo,
                ordem=proxima_ordem + i,
            )

        messages.success(
            request,
            'Produto atualizado.' if editando else 'Produto cadastrado.'
        )
        return redirect('painel_produtos')

    return render(request, 'app/painel_produto_form.html', {
        'form': form,
        'editando': editando,
        'imagens_extras': instancia.imagens.all() if editando else [],
    })


@staff_member_required(login_url='login')
@require_POST
def painel_produto_excluir(request, pk):
    get_object_or_404(Produto, pk=pk).delete()
    messages.success(request, 'Produto excluído.')
    return redirect('painel_produtos')


# =========================
# PAINEL — COLEÇÕES
# =========================

@staff_member_required(login_url='login')
def painel_colecoes(request):
    form = ColecaoForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Coleção criada.')
        return redirect('painel_colecoes')

    return render(request, 'app/painel_colecoes.html', {
        'form': form,
        'colecoes': _colecoes_com_total(),
    })


@staff_member_required(login_url='login')
@require_POST
def painel_colecao_excluir(request, pk):
    get_object_or_404(Colecao, pk=pk).delete()
    messages.success(request, 'Coleção excluída.')
    return redirect('painel_colecoes')