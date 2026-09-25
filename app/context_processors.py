from .carrinho import Carrinho


def carrinho_contador(request):
    return {"carrinho_qtd": len(Carrinho(request))}