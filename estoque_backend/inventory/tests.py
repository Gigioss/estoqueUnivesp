from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Item, Manutencao, ItemManutencao

class ManutencaoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Cria um item para teste
        self.item = Item.objects.create(
            descricao='Item Teste',
            quantidade=10,
            tipo='Cabo',
            estoque_minimo=5
        )
        
        # Cria uma manutenção inicial
        self.manutencao = Manutencao.objects.create(
            nome_cliente='Cliente Teste',
            status='Pendente',
            data_criacao=timezone.now()
        )
        
        # Cria um item associado à manutenção
        self.item_manutencao = ItemManutencao.objects.create(
            manutencao=self.manutencao,
            item=self.item,
            quantidade_utilizada=2
        )

    def test_manutencao_add_view_post_valid(self):
        """Teste com dados válidos deve redirecionar (status 302)"""
        url = reverse('manutencao_add')
        data = {
            'nome_cliente': 'Novo Cliente',
            'status': 'Pendente',
            'itens_utilizados-TOTAL_FORMS': '1',
            'itens_utilizados-INITIAL_FORMS': '0',
            'itens_utilizados-0-item': self.item.pk,
            'itens_utilizados-0-quantidade_utilizada': 3,  # Dentro do estoque
            'itens_utilizados-MIN_NUM_FORMS': '0',
            'itens_utilizados-MAX_NUM_FORMS': '1000',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Item.objects.get(pk=self.item.pk).quantidade, 7)

    def test_manutencao_add_view_post_insufficient_stock(self):
        """Teste com estoque insuficiente deve mostrar erro"""
        url = reverse('manutencao_add')
        data = {
            'nome_cliente': 'Cliente Sem Estoque',
            'status': 'Pendente',
            'itens_utilizados-TOTAL_FORMS': '1',
            'itens_utilizados-INITIAL_FORMS': '0',
            'itens_utilizados-0-item': self.item.pk,
            'itens_utilizados-0-quantidade_utilizada': 15,  # Acima do estoque
            'itens_utilizados-MIN_NUM_FORMS': '0',
            'itens_utilizados-MAX_NUM_FORMS': '1000',
        }
        response = self.client.post(url, data)
        
        # Verifica se permanece na página (status 200) e mostra erro específico
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 
            "Não há estoque suficiente para o item Item Teste",  # Mensagem EXATA do seu form
            status_code=200
        )
        self.assertEqual(Item.objects.get(pk=self.item.pk).quantidade, 10)  # Estoque inalterado

    def test_manutencao_edit_view_post_valid(self):
        url = reverse('manutencao_edit', args=[self.manutencao.pk])
        data = {
            'nome_cliente': 'Cliente Editado',
            'status': 'Em andamento',
            'itens_utilizados-TOTAL_FORMS': '1',
            'itens_utilizados-INITIAL_FORMS': '1',
            'itens_utilizados-0-id': self.item_manutencao.pk,
            'itens_utilizados-0-item': self.item.pk,
            'itens_utilizados-0-quantidade_utilizada': 4,  # Aumentando de 2 para 4
            'itens_utilizados-MIN_NUM_FORMS': '0',
            'itens_utilizados-MAX_NUM_FORMS': '1000',
        }
        response = self.client.post(url, data)
    
        # Verificações
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
    
        # Verifica se a quantidade foi atualizada corretamente
        self.assertEqual(self.item.quantidade, 8)  # Ajustado para sua lógica