from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from datetime import timedelta
from django.utils import timezone

class FinancialSummary(models.Model):
    """Daily financial summary for quick access and analytics"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_summaries')
    
    summary_date = models.DateField(unique_for_date=True)
    
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    transaction_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Financial Summary'
        verbose_name_plural = 'Financial Summaries'
        indexes = [
            models.Index(fields=['user', '-summary_date']),
        ]
        unique_together = ['user', 'summary_date']

    def __str__(self):
        return f"{self.user.username} - {self.summary_date}"


class SpendingTrend(models.Model):
    """Track spending trends over time"""
    
    TREND_PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spending_trends')
    category = models.ForeignKey('transactions.Category', on_delete=models.CASCADE)
    
    period = models.CharField(max_length=20, choices=TREND_PERIOD_CHOICES)
    period_start_date = models.DateField()
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Spending Trend'
        verbose_name_plural = 'Spending Trends'
        indexes = [
            models.Index(fields=['user', 'period', '-period_start_date']),
        ]
        unique_together = ['user', 'category', 'period', 'period_start_date']

    def __str__(self):
        return f"{self.user.username} - {self.category.name} ({self.period})"


class SavingsGoal(models.Model):
    """Track savings goals"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    category = models.ForeignKey('transactions.Category', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Savings Goal'
        verbose_name_plural = 'Savings Goals'
        ordering = ['target_date']

    def __str__(self):
        return f"{self.name} - {self.current_amount}/{self.target_amount}"

    def get_percentage_complete(self):
        """Calculate percentage towards goal"""
        if self.target_amount == 0:
            return 0
        return round((float(self.current_amount) / float(self.target_amount)) * 100, 2)

    def is_completed(self):
        """Check if goal is completed"""
        return self.current_amount >= self.target_amount

    def days_remaining(self):
        """Calculate days until target date"""
        today = timezone.now().date()
        if today > self.target_date:
            return 0
        return (self.target_date - today).days


class MonthlyReport(models.Model):
    """Generated monthly financial reports"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_reports')
    
    month = models.DateField(help_text="First day of the month")
    
    total_income = models.DecimalField(max_digits=12, decimal_places=2)
    total_expense = models.DecimalField(max_digits=12, decimal_places=2)
    net_savings = models.DecimalField(max_digits=12, decimal_places=2)
    
    savings_rate = models.FloatField(help_text="Percentage of income saved")
    
    top_expense_category = models.ForeignKey(
        'transactions.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='monthly_reports_as_top'
    )
    top_expense_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    insights = models.TextField(blank=True, null=True)
    
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Monthly Report'
        verbose_name_plural = 'Monthly Reports'
        unique_together = ['user', 'month']
        ordering = ['-month']

    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%B %Y')}"