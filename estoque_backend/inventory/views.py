from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from .models import Item, ItemManutencao, Manutencao
from .forms import ItemForm, ManutencaoForm, ItemManutencaoFormSet

def item_list(request):
    items = Item.objects.all()
    print("Tentando carregar o template:", 'inventory/item_list.html')  # Debug
    return render(request, 'inventory/item_list.html', {'items': items})

def item_add(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'inventory/item_form.html', {'form': form})

def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {'form': form})

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'inventory/item_confirm_delete.html', {'item': item})

def manutencao_list(request):
    manutencoes = Manutencao.objects.all()
    return render(request, 'inventory/manutencao_list.html', {'manutencoes': manutencoes})

def manutencao_add(request):
    if request.method == 'POST':
        form = ManutencaoForm(request.POST)
        formset = ItemManutencaoFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            manutencao = form.save()  # Salva a manutenção principal
            formset.instance = manutencao  # Associa o formset à manutenção

            for item_form in formset:
                if item_form.cleaned_data:
                    quantidade_utilizada = item_form.cleaned_data.get('quantidade_utilizada')
                    item = item_form.cleaned_data.get('item')
               
                    if item and quantidade_utilizada:
                        print("aqui")
                        # Verifica se há estoque suficiente
                        if item.quantidade >= quantidade_utilizada:
                            item.quantidade -= quantidade_utilizada
                            item.save()  # Atualiza o estoque do item
                            
                        else:
                            # Adiciona um erro ao formulário principal
                            form.add_error(None, f"Não há estoque suficiente para o item {item.descricao}.")
                            return render(request, 'inventory/manutencao_form.html', {'form': form, 'formset': formset})

            formset.save()  # Salva os itens de manutenção
            return redirect('manutencao_list')  # Redireciona para a lista de manutenções
        else:
            print("Formulário principal inválido:", form.errors)
            print("Formset inválido:", formset.errors)
    else:
        form = ManutencaoForm()
        formset = ItemManutencaoFormSet()

    return render(request, 'inventory/manutencao_form.html', {'form': form, 'formset': formset})

@transaction.atomic
def manutencao_edit(request, pk):
    manutencao = get_object_or_404(Manutencao, pk=pk)
    if request.method == 'POST':
        form = ManutencaoForm(request.POST, instance=manutencao)
        formset = ItemManutencaoFormSet(request.POST, instance=manutencao)

        if form.is_valid() and formset.is_valid():
            manutencao = form.save()
            for item_form in formset:
                if item_form.cleaned_data.get('item') and item_form.cleaned_data.get('quantidade_utilizada'):
                    item = item_form.cleaned_data['item']
                    quantidade_utilizada = item_form.cleaned_data['quantidade_utilizada']

                    if item.quantidade >= quantidade_utilizada:
                        item.quantidade -= quantidade_utilizada
                        item.save()
                    else:
                        form.add_error(None, f"Não há estoque suficiente para o item {item.descricao}.")
                        return render(request, 'inventory/manutencao_form.html', {'form': form, 'formset': formset})

            formset.save()
            return redirect('manutencao_list')
    else:
        form = ManutencaoForm(instance=manutencao)
        formset = ItemManutencaoFormSet(instance=manutencao)

    return render(request, 'inventory/manutencao_form.html', {'form': form, 'formset': formset})

@transaction.atomic
def manutencao_delete(request, pk):
    manutencao = get_object_or_404(Manutencao, pk=pk)
    if request.method == 'POST':
        # Devolve a quantidade utilizada ao estoque
        for item_manutencao in manutencao.itens_utilizados.all():
            item = item_manutencao.item
            item.quantidade += item_manutencao.quantidade_utilizada  # Devolve a quantidade
            item.save()  # Salva o item atualizado

        # Exclui a manutenção
        manutencao.delete()
        return redirect('manutencao_list')
    return render(request, 'inventory/manutencao_confirm_delete.html', {'manutencao': manutencao})