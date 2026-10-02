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

    # Login e cadastro
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),

    # Logout
    path('sair/', views.sair, name='logout'),

    # Google / django-allauth
    path('accounts/', include('allauth.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )