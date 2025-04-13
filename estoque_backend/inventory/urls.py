# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),  # Lista de itens (página inicial do inventory)
    path('add/', views.item_add, name='item_add'),  # Adicionar um novo item
    path('edit/<int:pk>/', views.item_edit, name='item_edit'),  # Editar um item existente
    path('delete/<int:pk>/', views.item_delete, name='item_delete'),  # Excluir um item
    path('relatorios/', views.relatorios_view, name='relatorios'),
    path('manutencao/', views.manutencao_list, name='manutencao_list'),
    path('manutencao/add/', views.manutencao_add, name='manutencao_add'),
    path('manutencao/edit/<int:pk>/', views.manutencao_edit, name='manutencao_edit'),
    path('manutencao/delete/<int:pk>/', views.manutencao_delete, name='manutencao_delete'),
]
