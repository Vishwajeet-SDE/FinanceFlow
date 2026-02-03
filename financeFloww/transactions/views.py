from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Transaction, Category, PaymentMethod
from .forms import TransactionForm, CategoryForm, PaymentMethodForm, TransactionFilterForm


@login_required
def transaction_list(request):
    """List all transactions with filtering"""
    transactions = Transaction.objects.filter(user=request.user).select_related('category', 'payment_method')
    
    # Apply filters
    filter_form = TransactionFilterForm(request.GET, user=request.user)
    
    transaction_type = request.GET.get('transaction_type', 'all')
    if transaction_type == 'income':
        transactions = transactions.filter(transaction_type='income')
    elif transaction_type == 'expense':
        transactions = transactions.filter(transaction_type='expense')
    
    category = request.GET.get('category')
    if category:
        transactions = transactions.filter(category_id=category)
    
    payment_method = request.GET.get('payment_method')
    if payment_method:
        transactions = transactions.filter(payment_method_id=payment_method)
    
    date_from = request.GET.get('date_from')
    if date_from:
        transactions = transactions.filter(transaction_date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        transactions = transactions.filter(transaction_date__lte=date_to)
    
    amount_min = request.GET.get('amount_min')
    if amount_min:
        transactions = transactions.filter(amount__gte=amount_min)
    
    amount_max = request.GET.get('amount_max')
    if amount_max:
        transactions = transactions.filter(amount__lte=amount_max)
    
    # Calculate summary
    income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net = income - expenses
    
    context = {
        'transactions': transactions,
        'filter_form': filter_form,
        'income': income,
        'expenses': expenses,
        'net': net,
    }
    return render(request, 'transactions/transaction_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def transaction_create(request):
    """Create a new transaction"""
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction created successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'transactions/transaction_form.html', context)


@login_required
def transaction_detail(request, pk):
    """View transaction details"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    context = {'transaction': transaction}
    return render(request, 'transactions/transaction_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def transaction_edit(request, pk):
    """Edit a transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_detail', pk=pk)
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    context = {'form': form, 'transaction': transaction, 'action': 'Edit'}
    return render(request, 'transactions/transaction_form.html', context)


@login_required
@require_http_methods(["POST"])
def transaction_delete(request, pk):
    """Delete a transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    messages.success(request, 'Transaction deleted successfully!')
    return redirect('transaction_list')


# Category Views

@login_required
def category_list(request):
    """List all categories"""
    categories = Category.objects.filter(user=request.user).order_by('category_type', 'name')
    context = {'categories': categories}
    return render(request, 'transactions/category_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'transactions/category_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def category_edit(request, pk):
    """Edit a category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {'form': form, 'category': category, 'action': 'Edit'}
    return render(request, 'transactions/category_form.html', context)


@login_required
@require_http_methods(["POST"])
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('category_list')


# Payment Method Views

@login_required
def payment_method_list(request):
    """List all payment methods"""
    payment_methods = PaymentMethod.objects.filter(user=request.user).order_by('name')
    context = {'payment_methods': payment_methods}
    return render(request, 'transactions/payment_method_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def payment_method_create(request):
    """Create a new payment method"""
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.save(commit=False)
            payment_method.user = request.user
            payment_method.save()
            messages.success(request, 'Payment method created successfully!')
            return redirect('payment_method_list')
    else:
        form = PaymentMethodForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'transactions/payment_method_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def payment_method_edit(request, pk):
    """Edit a payment method"""
    payment_method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment method updated successfully!')
            return redirect('payment_method_list')
    else:
        form = PaymentMethodForm(instance=payment_method)
    
    context = {'form': form, 'payment_method': payment_method, 'action': 'Edit'}
    return render(request, 'transactions/payment_method_form.html', context)


@login_required
@require_http_methods(["POST"])
def payment_method_delete(request, pk):
    """Delete a payment method"""
    payment_method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    payment_method.delete()
    messages.success(request, 'Payment method deleted successfully!')
    return redirect('payment_method_list')