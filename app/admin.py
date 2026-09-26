from django.contrib import admin
from .models import Produto, Colecao

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'preco_antigo', 'destaque')
    list_filter = ('categoria', 'destaque')
    search_fields = ('nome',)

@admin.register(Colecao)
class ColecaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem')