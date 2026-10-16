from django.contrib import admin
from .models import Produto, Colecao, ProdutoImagem


class ProdutoImagemInline(admin.TabularInline):
    model = ProdutoImagem
    extra = 3  # campos de foto vazios que já aparecem


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'preco_antigo', 'estoque', 'destaque')
    list_filter = ('categoria', 'destaque')
    search_fields = ('nome',)
    inlines = [ProdutoImagemInline]


@admin.register(Colecao)
class ColecaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem')