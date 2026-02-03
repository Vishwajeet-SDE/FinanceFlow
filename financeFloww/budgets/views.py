from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Budget, BudgetAlert
from .forms import BudgetForm, BudgetFilterForm


@login_required
def budget_list(request):
    """List all budgets"""
    budgets = Budget.objects.filter(user=request.user).select_related('category')
    
    # Apply filters
    frequency = request.GET.get('frequency')
    if frequency:
        budgets = budgets.filter(frequency=frequency)
    
    is_active = request.GET.get('is_active')
    if is_active == 'true':
        budgets = budgets.filter(is_active=True)
    elif is_active == 'false':
        budgets = budgets.filter(is_active=False)
    
    search = request.GET.get('search')
    if search:
        budgets = budgets.filter(category__name__icontains=search)
    
    # Calculate spent and percentage for each budget
    budget_details = []
    for budget in budgets:
        spent = budget.get_spent_amount()
        remaining = budget.get_remaining_amount()
        percentage = budget.get_percentage_used()
        is_over = budget.is_over_budget()
        should_alert = budget.should_alert()
        
        budget_details.append({
            'budget': budget,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage,
            'is_over': is_over,
            'should_alert': should_alert,
        })
    
    filter_form = BudgetFilterForm(request.GET)
    
    context = {
        'budget_details': budget_details,
        'filter_form': filter_form,
    }
    return render(request, 'budgets/budget_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def budget_create(request):
    """Create a new budget"""
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'budgets/budget_form.html', context)


@login_required
def budget_detail(request, pk):
    """View budget details"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    spent = budget.get_spent_amount()
    remaining = budget.get_remaining_amount()
    percentage = budget.get_percentage_used()
    is_over = budget.is_over_budget()
    
    # Get recent transactions for this budget category
    from transactions.models import Transaction
    recent_transactions = Transaction.objects.filter(
        user=request.user,
        category=budget.category,
        transaction_type='expense',
        status='completed'
    ).order_by('-transaction_date')[:10]
    
    context = {
        'budget': budget,
        'spent': spent,
        'remaining': remaining,
        'percentage': percentage,
        'is_over': is_over,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'budgets/budget_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def budget_edit(request, pk):
    """Edit a budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budget_detail', pk=pk)
    else:
        form = BudgetForm(instance=budget, user=request.user)
    
    context = {'form': form, 'budget': budget, 'action': 'Edit'}
    return render(request, 'budgets/budget_form.html', context)


@login_required
@require_http_methods(["POST"])
def budget_delete(request, pk):
    """Delete a budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    budget.delete()
    messages.success(request, 'Budget deleted successfully!')
    return redirect('budget_list')


@login_required
def budget_alerts(request):
    """View budget alerts"""
    alerts = BudgetAlert.objects.filter(user=request.user).select_related('budget').order_by('-triggered_at')
    
    context = {'alerts': alerts}
    return render(request, 'budgets/budget_alerts.html', context)


@login_required
@require_http_methods(["POST"])
def acknowledge_alert(request, pk):
    """Acknowledge a budget alert"""
    alert = get_object_or_404(BudgetAlert, pk=pk, user=request.user)
    alert.status = 'acknowledged'
    alert.save()
    messages.success(request, 'Alert acknowledged!')
    return redirect('budget_alerts')