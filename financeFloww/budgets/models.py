from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from dateutil.relativedelta import relativedelta

class Budget(models.Model):
    """Budget tracking for categories"""
    
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey('transactions.Category', on_delete=models.CASCADE)
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    
    alert_threshold = models.IntegerField(
        default=80,
        validators=[MinValueValidator(1)],
        help_text="Alert when spending reaches this percentage (1-100)"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        unique_together = ['user', 'category', 'start_date']
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.category.name} - {self.amount} ({self.frequency})"

    def get_spent_amount(self):
        """Calculate total spent in this budget period"""
        from django.db.models import Sum
        from transactions.models import Transaction
        
        if self.frequency == 'monthly':
            start = self.start_date.replace(day=1)
            if self.start_date.month == 12:
                end = self.start_date.replace(year=self.start_date.year + 1, month=1, day=1)
            else:
                end = self.start_date.replace(month=self.start_date.month + 1, day=1)
        elif self.frequency == 'quarterly':
            quarter_start_month = ((self.start_date.month - 1) // 3) * 3 + 1
            start = self.start_date.replace(month=quarter_start_month, day=1)
            end = start + relativedelta(months=3)
        else:  # yearly
            start = self.start_date.replace(month=1, day=1)
            end = self.start_date.replace(year=self.start_date.year + 1, month=1, day=1)
        
        spent = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            transaction_type='expense',
            transaction_date__gte=start,
            transaction_date__lt=end,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return spent

    def get_remaining_amount(self):
        """Calculate remaining budget"""
        return self.amount - self.get_spent_amount()

    def get_percentage_used(self):
        """Calculate percentage of budget used"""
        if self.amount == 0:
            return 0
        spent = self.get_spent_amount()
        return round((float(spent) / float(self.amount)) * 100, 2)

    def is_over_budget(self):
        """Check if budget is exceeded"""
        return self.get_spent_amount() > self.amount

    def should_alert(self):
        """Check if alert threshold is reached"""
        return self.get_percentage_used() >= self.alert_threshold


class BudgetAlert(models.Model):
    """Alerts for budget thresholds"""
    
    ALERT_STATUS_CHOICES = [
        ('triggered', 'Triggered'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='alerts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budget_alerts')
    
    message = models.TextField()
    percentage_at_trigger = models.IntegerField()
    status = models.CharField(max_length=20, choices=ALERT_STATUS_CHOICES, default='triggered')
    
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Budget Alert'
        verbose_name_plural = 'Budget Alerts'
        ordering = ['-triggered_at']

    def __str__(self):
        return f"Alert for {self.budget.category.name} - {self.percentage_at_trigger}%"