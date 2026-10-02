def carrinho(request):
    """Quantidade de itens da sacola. Fica 0 até o backend preencher
    request.session['carrinho'] no formato {produto_id: quantidade}."""
    itens = request.session.get('carrinho', {})
    total = sum(itens.values()) if isinstance(itens, dict) else 0
    return {'carrinho_qtd': total}


# mesmo nome que o settings.py já usa
def carrinho(request):
    """Quantidade de itens da sacola. Fica 0 até o backend preencher
    request.session['carrinho'] no formato {produto_id: quantidade}."""
    itens = request.session.get('carrinho', {})
    total = sum(itens.values()) if isinstance(itens, dict) else 0
    return {'carrinho_qtd': total}


# mesmo nome que o settings.py já usa
carrinho_contador = carrinho