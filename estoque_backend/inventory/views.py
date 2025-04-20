import json
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Count, Sum,Q
from django.http import JsonResponse
from .models import Item, ItemManutencao, Manutencao
from .forms import ItemForm, ManutencaoForm, ItemManutencaoFormSet

def item_list(request):
    query = request.GET.get('q', '')
    items = Item.objects.all().order_by('id')
    
    if query:
        items = items.filter(
            Q(descricao__icontains=query) |
            Q(tipo__icontains=query) |
            Q(id__icontains=query)
        )
    
    return render(request, 'inventory/item_list.html', {
        'items': items,
        'search_query': query  # Adicionei isso para manter o termo de busca no template
    })

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
    query = request.GET.get('q', '')
    manutencoes = Manutencao.objects.all().order_by('-data_criacao')  # Ordena por data mais recente
    
    if query:
        manutencoes = manutencoes.filter(
            Q(nome_cliente__icontains=query) |
            Q(status__icontains=query) |
            Q(id__icontains=query)
            # Removi a busca por 'equipamento' que não existe no modelo
        )
    
    return render(request, 'inventory/manutencao_list.html', {
        'manutencoes': manutencoes,
        'search_query': query
    })

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
            # 1. Primeiro devolve os itens ao estoque
            for item_manutencao in manutencao.itens_utilizados.all():
                item = item_manutencao.item
                item.quantidade += item_manutencao.quantidade_utilizada
                item.save()
            
            # 2. Salva a manutenção (sem itens ainda)
            manutencao = form.save()
            
            # 3. Processa os itens do formset
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    item = item_form.cleaned_data.get('item')
                    quantidade = item_form.cleaned_data.get('quantidade_utilizada')
                    
                    if item and quantidade:
                        # Verifica estoque
                        if item.quantidade >= quantidade:
                            item.quantidade -= quantidade
                            item.save()
                        else:
                            # Se não tiver estoque, devolve tudo e mostra erro
                            form.add_error(None, f"Estoque insuficiente para {item.descricao}")
                            return render(request, 'inventory/manutencao_form.html', {
                                'form': form,
                                'formset': formset
                            })
            
            # 4. Salva o formset depois de todas as validações
            formset.save()
            return redirect('manutencao_list')
    
    else:
        form = ManutencaoForm(instance=manutencao)
        formset = ItemManutencaoFormSet(instance=manutencao)
    
    return render(request, 'inventory/manutencao_form.html', {
        'form': form,
        'formset': formset,
        'manutencao': manutencao
    })
    
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

@transaction.atomic
def relatorios_view(request):
    # Filtros básicos
    itens_utilizados = ItemManutencao.objects.all().select_related('manutencao', 'item')
    mensagem = None

    if request.method == 'POST':
        nome_cliente = request.POST.get('nome_cliente', '').strip()
        status = request.POST.get('status', '').strip()

        if nome_cliente:
            itens_utilizados = itens_utilizados.filter(
                manutencao__nome_cliente__icontains=nome_cliente
            )
        
        if status:
            itens_utilizados = itens_utilizados.filter(
                manutencao__status=status
            )

        if not nome_cliente and not status:
            mensagem = "Nenhum filtro aplicado - mostrando todos os itens"

    # Preparação dos dados para gráficos
    dados_grafico = {
        'por_status': list(
            itens_utilizados.values('manutencao__status')
            .annotate(total=Count('id'))
            .order_by('-total')
        ),
        'por_item': list(
            itens_utilizados.values('item__descricao')
            .annotate(total=Sum('quantidade_utilizada'))
            .order_by('-total')[:10]  # Top 10 itens
        )
    }

    # Dados para gráficos - CORRIGIDO para usar 'item__descricao'
    dados_grafico = {
        'por_status': list(
            itens_utilizados.values('manutencao__status')
            .annotate(total=Count('id'))
            .order_by('-total')
        ),
        'por_item': list(
            itens_utilizados.values('item__descricao')  # Alterado para descricao
            .annotate(total=Sum('quantidade_utilizada'))
            .order_by('-total')[:10]
        )
    }

    context = {
        'itens_utilizados': itens_utilizados,
        'mensagem': mensagem,
        'total_itens': itens_utilizados.count(),
        'dados_grafico_json': json.dumps(dados_grafico),
    }
    return render(request, 'inventory/relatorios.html', context)
