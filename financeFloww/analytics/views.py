from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, date
from calendar import monthrange
from .models import FinancialSummary, SavingsGoal, MonthlyReport
from transactions.models import Transaction, Category


@login_required
def dashboard(request):
    """Main dashboard"""
    today = timezone.now().date()
    
    # Get current month dates
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])
    
    # Monthly stats
    monthly_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        transaction_date__gte=first_day,
        transaction_date__lte=last_day,
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    monthly_expense = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        transaction_date__gte=first_day,
        transaction_date__lte=last_day,
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    monthly_net = monthly_income - monthly_expense
    
    # This month transactions
    this_month_transactions = Transaction.objects.filter(
        user=request.user,
        transaction_date__gte=first_day,
        transaction_date__lte=last_day,
        status='completed'
    ).order_by('-transaction_date')[:5]
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-transaction_date')[:10]
    
    # Expense breakdown by category
    expense_by_category = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        transaction_date__gte=first_day,
        transaction_date__lte=last_day,
        status='completed'
    ).values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:5]
    
    # Income breakdown by category
    income_by_category = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        transaction_date__gte=first_day,
        transaction_date__lte=last_day,
        status='completed'
    ).values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:5]
    
    # Budget summary
    from budgets.models import Budget
    active_budgets = Budget.objects.filter(user=request.user, is_active=True)
    budget_summary = []
    for budget in active_budgets:
        spent = budget.get_spent_amount()
        percentage = min(budget.percentage, 100)
        budget_summary.append({
            'budget': budget,
            'spent': spent,
            'percentage': percentage,
            'is_over': budget.is_over_budget(),
        })
    
    # Savings goals
    savings_goals = SavingsGoal.objects.filter(
        user=request.user,
        status='active'
    ).order_by('target_date')[:3]
    
    # Financial summary
    try:
        financial_summary = FinancialSummary.objects.get(
            user=request.user,
            summary_date=today
        )
    except FinancialSummary.DoesNotExist:
        financial_summary = None
    
    # Savings rate calculation
    if monthly_income > 0:
        savings_rate = round(((monthly_income - monthly_expense) / monthly_income) * 100, 2)
    else:
        savings_rate = 0
    
    context = {
        'today': today,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'monthly_net': monthly_net,
        'savings_rate': savings_rate,
        'this_month_transactions': this_month_transactions,
        'recent_transactions': recent_transactions,
        'expense_by_category': expense_by_category,
        'income_by_category': income_by_category,
        'budget_summary': budget_summary,
        'savings_goals': savings_goals,
        'financial_summary': financial_summary,
    }
    return render(request, 'analytics/dashboard.html', context)


@login_required
def spending_breakdown(request):
    """Detailed spending breakdown"""
    today = timezone.now().date()
    
    # Default to current month
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    first_day = date(year, month, 1)
    last_day = first_day.replace(day=monthrange(year, month)[1])
    
    # Get all expense categories with amounts
    categories = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        transaction_date__gte=first_day,
        transaction_date__lte=last_day,
        status='completed'
    ).values('category__name', 'category__id').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Calculate percentages
    total_expenses = sum(cat['total'] for cat in categories)
    for cat in categories:
        if total_expenses > 0:
            cat['percentage'] = round((cat['total'] / total_expenses) * 100, 2)
        else:
            cat['percentage'] = 0
    
    context = {
        'categories': categories,
        'total_expenses': total_expenses,
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B %Y'),
    }
    return render(request, 'analytics/spending_breakdown.html', context)


@login_required
def financial_report(request):
    """Monthly financial report"""
    today = timezone.now().date()
    
    # Get last 6 months
    reports = MonthlyReport.objects.filter(
        user=request.user
    ).order_by('-month')[:6]
    
    # Calculate current month if not in database
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])
    
    current_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        transaction_date__gte=first_day,
        transaction_date__lte=last_day,
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    current_expense = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        transaction_date__gte=first_day,
        transaction_date__lte=last_day,
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    current_net = current_income - current_expense
    
    if current_income > 0:
        current_savings_rate = round(((current_income - current_expense) / current_income) * 100, 2)
    else:
        current_savings_rate = 0
    
    context = {
        'reports': reports,
        'current_income': current_income,
        'current_expense': current_expense,
        'current_net': current_net,
        'current_savings_rate': current_savings_rate,
    }
    return render(request, 'analytics/financial_report.html', context)


@login_required
def savings_goals_list(request):
    """List savings goals"""
    goals = SavingsGoal.objects.filter(user=request.user).order_by('target_date')
    
    context = {'goals': goals}
    print("Vishwajeeeeeeeeeeeeett")
    return render(request, 'analytics/savings_goals_list.html', context)


@login_required
def savings_goal_detail(request, pk):
    """View savings goal details"""
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    context = {'goal': goal}
    return render(request, 'analytics/savings_goal_detail.html', context)