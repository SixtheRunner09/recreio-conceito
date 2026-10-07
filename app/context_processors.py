def carrinho(request):
    """Quantidade total de itens da sacola.

    Aceita os dois formatos da sessão:
    {produto_id: {'quantidade': n}}  (atual)
    {produto_id: n}                  (antigo)
    """
    itens = request.session.get('carrinho', {})

    if not isinstance(itens, dict):
        return {'carrinho_qtd': 0}

    total = 0
    for dados in itens.values():
        if isinstance(dados, dict):
            total += dados.get('quantidade', 1)
        else:
            total += dados

    return {'carrinho_qtd': total}


# mesmo nome que o settings.py já usa
carrinho_contador = carrinho


def curtidos_contador(request):
    """Ids e total de produtos curtidos (disponível em todos os templates)."""
    ids = request.session.get('curtidos', [])
    return {
        'curtidos_ids': ids,
        'curtidos_qtd': len(ids),
    }