from django.shortcuts import redirect, render, get_object_or_404
from .models import Produto, Colecao
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.models import User

def index(request):
    produtos_destaque = Produto.objects.all()[:3]
    ofertas = Produto.objects.filter(preco_antigo__isnull=False)[:4]
    colecoes = Colecao.objects.all()
    return render(request, "app/index.html", {
        "produtos_destaque": produtos_destaque,
        "ofertas": ofertas,
        "colecoes": colecoes,
    })

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
    relacionados = Produto.objects.filter(destaque=True).exclude(pk=pk)[:4]
    return render(request, "app/produto.html", {
        "produto": produto,
        "relacionados": relacionados,
    })

def adicionar_ao_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)

    # Mantém o formato de dicionário esperado pela classe Carrinho
    if produto_id_str in carrinho:
        carrinho[produto_id_str]['quantidade'] += 1
    else:
        carrinho[produto_id_str] = {'quantidade': 1}

    request.session['carrinho'] = carrinho
    return redirect('carrinho')

def carrinho(request):
    carrinho_sessao = request.session.get('carrinho', {})
    itens_carrinho = []
    total = 0

    for produto_id, dados in carrinho_sessao.items():
        produto = get_object_or_404(Produto, id=produto_id)
        
        # Garante a leitura correta se dados for um dicionário
        quantidade = dados['quantidade'] if isinstance(dados, dict) else dados
        
        subtotal = produto.preco * quantidade
        total += subtotal
        itens_carrinho.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal
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

    return redirect('carrinho')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index') # Se já estiver logado, redireciona para a home

    if request.method == 'POST':
        usuario_input = request.POST.get('username')
        senha_input = request.POST.get('password')
        lembrar = request.POST.get('lembrar')

        # Autentica o usuário
        user = authenticate(request, username=usuario_input, password=senha_input)

        if user is not None:
            auth_login(request, user)
            
            # Se a opção "Lembrar de mim" não estiver marcada, a sessão expira ao fechar o navegador
            if not lembrar:
                request.session.set_expiry(0)
                
            messages.success(request, f"Bem-vinda de volta, {user.first_name or user.username}!")
            return redirect('index') # Ou redireciona para o checkout/perfil
        else:
            messages.error(request, "E-mail ou senha incorretos. Verifique seus dados.")

    return render(request, 'app/login.html')

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('index')

def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        sobrenome = request.POST.get('sobrenome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '')
        confirmar_senha = request.POST.get('confirmar_senha', '')
        aceite_termos = request.POST.get('aceite_termos')

        erros = {}

        if not nome or not sobrenome:
            erros['nome'] = 'Nome e sobrenome são obrigatórios.'

        if not email:
            erros['email'] = 'Informe um e-mail válido.'
        elif User.objects.filter(email=email).exists():
            erros['email'] = 'Este e-mail já está cadastrado em nosso sistema.'

        if len(senha) < 8:
            erros['senha'] = 'A senha deve ter no mínimo 8 caracteres.'

        if senha != confirmar_senha:
            erros['confirmar_senha'] = 'As senhas não coincidem.'

        if not aceite_termos:
            erros['non_field'] = 'Você precisa aceitar os termos de uso.'

        if erros:
            return render(request, 'app/cadastro.html', {
                'erros': erros,
                'dados': {
                    'nome': nome,
                    'sobrenome': sobrenome,
                    'email': email,
                }
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=senha,
            first_name=nome,
            last_name=sobrenome
        )

        auth_login(request, user)
        return redirect('index')

    return render(request, 'app/cadastro.html')