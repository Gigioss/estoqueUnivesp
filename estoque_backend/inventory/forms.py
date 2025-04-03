from django import forms
from .models import Item, Manutencao, ItemManutencao
from django.forms import inlineformset_factory

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['descricao', 'quantidade', 'tipo', 'estoque_minimo']

class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = ['nome_cliente', 'status']

class ItemManutencaoForm(forms.ModelForm):
    class Meta:
        model = ItemManutencao
        fields = ['item', 'quantidade_utilizada']

    def clean_quantidade_utilizada(self):
        quantidade_utilizada = self.cleaned_data.get('quantidade_utilizada')
        item = self.cleaned_data.get('item')

        if quantidade_utilizada is not None and quantidade_utilizada < 0:
            raise forms.ValidationError("A quantidade utilizada não pode ser negativa.")

        if item and quantidade_utilizada and quantidade_utilizada > item.quantidade:
            raise forms.ValidationError(f"Não há estoque suficiente para o item {item.descricao}.")

        return quantidade_utilizada

# Cria o formset para os itens utilizados
ItemManutencaoFormSet = inlineformset_factory(
    Manutencao,  # Modelo principal
    ItemManutencao,  # Modelo relacionado
    form=ItemManutencaoForm,  # Formulário do modelo relacionado
    extra=1,  # Número de formulários extras exibidos
    can_delete=True  # Permite excluir itens
)