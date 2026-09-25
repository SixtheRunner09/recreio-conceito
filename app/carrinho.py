from decimal import Decimal
from .models import Produto

CART_SESSION_ID = "carrinho"


class Carrinho:
    def __init__(self, request):
        self.session = request.session
        self.itens = self.session.setdefault(CART_SESSION_ID, {})

    def _salvar(self):
        self.session.modified = True

    def adicionar(self, produto, tamanho, cor, quantidade=1):
        chave = f"{produto.id}|{tamanho}|{cor}"
        item = self.itens.setdefault(chave, {
            "produto_id": produto.id,
            "tamanho": tamanho,
            "cor": cor,
            "quantidade": 0,
        })
        item["quantidade"] += quantidade
        self._salvar()

    def remover(self, chave):
        if chave in self.itens:
            del self.itens[chave]
            self._salvar()

    def limpar(self):
        self.session[CART_SESSION_ID] = {}
        self._salvar()

    def __iter__(self):
        produtos = Produto.objects.in_bulk([i["produto_id"] for i in self.itens.values()])
        for chave, item in self.itens.items():
            produto = produtos.get(item["produto_id"])
            if produto is None:
                continue
            yield {
                "chave": chave,
                "produto": produto,
                "tamanho": item["tamanho"],
                "cor": item["cor"],
                "quantidade": item["quantidade"],
                "subtotal": produto.preco * item["quantidade"],
            }

    def __len__(self):
        return sum(i["quantidade"] for i in self.itens.values())

    def total(self):
        return sum((i["subtotal"] for i in self), Decimal("0"))