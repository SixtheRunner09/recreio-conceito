from django.db import models

CATEGORIA_CHOICES = [
    ('Camisas', 'Camisas'),
    ('Vestidos', 'Vestidos'),
    ('Alfaiataria', 'Alfaiataria'),
    ('Saias', 'Saias'),
]

class Produto(models.Model):
    nome = models.CharField(max_length=120)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    preco_antigo = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Preencha só se o produto estiver em oferta."
    )
    imagem = models.ImageField(upload_to='produtos/', blank=True)
    destaque = models.BooleanField(
        default=False,
        help_text="Marque para este produto aparecer na seção 'Mais Vendidos'."
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

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome

    @property
    def desconto_percentual(self):
        if self.preco_antigo and self.preco_antigo > self.preco:
            return round((1 - self.preco / self.preco_antigo) * 100)
        return None

class Colecao(models.Model):
    nome = models.CharField(max_length=120)
    descricao = models.CharField(max_length=150, blank=True)
    imagem = models.ImageField(upload_to='colecoes/', blank=True)
    ordem = models.PositiveIntegerField(default=0, help_text="Números menores aparecem primeiro no carrossel.")

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Coleção'
        verbose_name_plural = 'Coleções'

    def __str__(self):
        return self.nome