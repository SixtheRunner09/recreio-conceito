from django.shortcuts import render, get_object_or_404
from .models import Produto, Colecao

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

def carrinho(request):
    return render(request, "app/carrinho.html")

def login(request):
    return render(request, "app/login.html")

def cadastro(request):
    return render(request, "app/cadastro.html")