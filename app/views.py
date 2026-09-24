from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

def index(request):
    return render(request, "app/index.html")

def produtos(request):
    return render(request,"app/produtos.html")

def carrinho(request):
    return render(request,"app/carrinho.html")