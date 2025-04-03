from django.db import models

# Modelo para os itens no estoque
class Item(models.Model):
    TIPO_CHOICES = [
        ('Cabo', 'Cabo'),
        ('Peça de Computador', 'Peça de Computador'),
        ('Outro', 'Outro'),
    ]
    descricao = models.CharField(max_length=255)
    quantidade = models.IntegerField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estoque_minimo = models.IntegerField()

    def __str__(self):
        return self.descricao

# Modelo para as manutenções
class Manutencao(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Em andamento', 'Em andamento'),
        ('Concluído', 'Concluído'),
    ]
    nome_cliente = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome_cliente} - {self.status}"

# Modelo para associar os itens utilizados em cada manutenção
class ItemManutencao(models.Model):
    manutencao = models.ForeignKey(Manutencao, on_delete=models.CASCADE, related_name="itens_utilizados")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantidade_utilizada = models.IntegerField()

    def __str__(self):
        return f"{self.item.descricao} - {self.quantidade_utilizada} unidades"

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)
