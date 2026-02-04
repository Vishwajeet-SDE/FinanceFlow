from django import forms
from .models import Budget


class BudgetForm(forms.ModelForm):
    """Form for creating and editing budgets"""

    class Meta:
        model = Budget
        fields = [
            'category',
            'amount',
            'frequency',
            'start_date',
            'end_date',
            'alert_threshold',
            'is_active',
            'notes'
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['amount'].widget.attrs.update({
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
        self.fields['frequency'].widget.attrs.update({'class': 'form-select'})
        self.fields['start_date'].widget.attrs.update({
            'class': 'form-control',
            'type': 'date'
        })
        self.fields['end_date'].widget.attrs.update({
            'class': 'form-control',
            'type': 'date'
        })
        self.fields['alert_threshold'].widget.attrs.update({
            'class': 'form-control',
            'min': '1',
            'max': '100'
        })
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['notes'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Budget notes (optional)'
        })

        # Filter categories for the current user
        if user:
            from transactions.models import Category
            self.fields['category'].queryset = Category.objects.filter(
                user=user,
                category_type='expense',
                is_active=True
            )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        amount = cleaned_data.get('amount')

        if amount and amount <= 0:
            raise forms.ValidationError("Budget amount must be greater than 0")

        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date")

        return cleaned_data


class BudgetFilterForm(forms.Form):
    """Form for filtering budgets"""

    FREQUENCY_CHOICES = [
        ('', 'All Frequencies'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    frequency = forms.ChoiceField(
        choices=FREQUENCY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.NullBooleanField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}, choices=[
            ('', 'All Budgets'),
            (True, 'Active Only'),
            (False, 'Inactive Only'),
        ])
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by category name...'
        })
    )