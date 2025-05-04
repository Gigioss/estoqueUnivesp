from django import forms
from .models import Item, Manutencao, ItemManutencao
from django.forms import inlineformset_factory

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['descricao', 'quantidade', 'tipo', 'estoque_minimo']

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade is not None and quantidade < 0:
            raise forms.ValidationError("A quantidade em estoque não pode ser negativa.")
        return quantidade

    def clean_estoque_minimo(self):
        estoque_minimo = self.cleaned_data.get('estoque_minimo')
        if estoque_minimo is not None and estoque_minimo < 0:
            raise forms.ValidationError("O estoque mínimo não pode ser negativo.")
        return estoque_minimo

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
    Manutencao,
    ItemManutencao,
    form=ItemManutencaoForm,
    extra=1,
    can_delete=True
)
