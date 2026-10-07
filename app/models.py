from django.db import models

CATEGORIA_CHOICES = [
    ('Camisas', 'Camisas'),
    ('Calças', 'Calças'),
    ('Sapatos', 'Sapatos'),
    ('Bonés', 'Bonés'),
]


class Colecao(models.Model):
    nome = models.CharField(max_length=120)
    descricao = models.CharField(max_length=150, blank=True)
    imagem = models.ImageField(upload_to='colecoes/', blank=True)
    ordem = models.PositiveIntegerField(
        default=0,
        help_text="Números menores aparecem primeiro no carrossel."
    )

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Coleção'
        verbose_name_plural = 'Coleções'

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=120)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    preco_antigo = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Preencha só se o produto estiver em oferta."
    )
    estoque = models.PositiveIntegerField(
        'Quantidade em estoque',
        default=10,
        help_text="Quando chegar a 0, o produto aparece como indisponível."
    )

    imagem = models.ImageField(upload_to='produtos/', blank=True)
    destaque = models.BooleanField(
        default=False,
        help_text="Marque para este produto aparecer na seção 'Mais Vendidos'."
    )
    colecoes = models.ManyToManyField(
        Colecao, blank=True, related_name='produtos',
        verbose_name='Coleções'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome

    @property
    def desconto_percentual(self):
        if self.preco_antigo and self.preco_antigo > self.preco:
            return round((1 - self.preco / self.preco_antigo) * 100)
        return None

    @property
    def esgotado(self):
        return self.estoque <= 0


class ProdutoImagem(models.Model):
    produto = models.ForeignKey(
        Produto, related_name='imagens', on_delete=models.CASCADE
    )
    imagem = models.ImageField(upload_to='produtos/')
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'id']
        verbose_name = 'Foto do produto'
        verbose_name_plural = 'Fotos do produto'

    def __str__(self):
        return f"Foto de {self.produto.nome}"