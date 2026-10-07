from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from app import views


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Páginas principais
    path('', views.index, name='index'),
    path('produtos/', views.produtos, name='produtos'),
    path('produto/<int:pk>/', views.produto, name='produto'),

    # Coleções
    path('colecoes/', views.colecoes_lista, name='colecoes'),
    path('colecoes/<int:pk>/', views.colecao_detalhe, name='colecao_detalhe'),

    # Carrinho
    path('carrinho/', views.carrinho, name='carrinho'),
    path(
        'carrinho/adicionar/<int:produto_id>/',
        views.adicionar_ao_carrinho,
        name='adicionar_ao_carrinho'
    ),
    path(
        'carrinho/remover/<int:produto_id>/',
        views.remover_do_carrinho,
        name='remover_do_carrinho'
    ),

    # Curtidos
    path('curtidos/', views.curtidos, name='curtidos'),
    path(
        'curtidos/alternar/<int:produto_id>/',
        views.alternar_curtida,
        name='alternar_curtida'
    ),

    # Login e cadastro
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),

    # Logout
    path('sair/', views.sair, name='logout'),

    # Painel do administrador (is_staff)
    path('painel/', views.painel, name='painel'),
    path('painel/produtos/', views.painel_produtos, name='painel_produtos'),
    path('painel/produtos/novo/', views.painel_produto_form, name='painel_produto_novo'),
    path('painel/produtos/<int:pk>/editar/', views.painel_produto_form, name='painel_produto_editar'),
    path('painel/produtos/<int:pk>/excluir/', views.painel_produto_excluir, name='painel_produto_excluir'),
    path('painel/colecoes/', views.painel_colecoes, name='painel_colecoes'),
    path('painel/colecoes/<int:pk>/excluir/', views.painel_colecao_excluir, name='painel_colecao_excluir'),

    # Google / django-allauth
    path('accounts/', include('allauth.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )