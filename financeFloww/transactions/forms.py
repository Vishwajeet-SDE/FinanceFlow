from django import forms
from .models import Transaction, Category, PaymentMethod


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories"""

    class Meta:
        model = Category
        fields = ['name', 'category_type', 'color', 'icon', 'description', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Category Name'
        })
        self.fields['category_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['color'].widget.attrs.update({
            'class': 'form-control',
            'type': 'color'
        })
        self.fields['icon'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'e.g., 🍔 or fas fa-utensils'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Category description'
        })
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})


class PaymentMethodForm(forms.ModelForm):
    """Form for creating and editing payment methods"""

    class Meta:
        model = PaymentMethod
        fields = ['name', 'payment_type', 'account_number', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Payment Method Name'
        })
        self.fields['payment_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['account_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Last 4 digits (optional)',
            'maxlength': '4'
        })
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})


class TransactionForm(forms.ModelForm):
    """Form for creating and editing transactions"""

    class Meta:
        model = Transaction
        fields = [
            'transaction_type',
            'category',
            'amount',
            'description',
            'payment_method',
            'transaction_date',
            'notes',
            'status',
            'is_recurring',
            'tags'
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['transaction_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['amount'].widget.attrs.update({
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Transaction description'
        })
        self.fields['transaction_date'].widget.attrs.update({
            'class': 'form-control',
            'type': 'date'
        })
        self.fields['notes'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes (optional)'
        })
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        self.fields['is_recurring'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['tags'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Separate tags with commas'
        })

        # Filter categories and payment methods for the current user
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user, is_active=True)
            self.fields['payment_method'].queryset = PaymentMethod.objects.filter(user=user, is_active=True)
            self.fields['category'].widget.attrs.update({'class': 'form-select'})
            self.fields['payment_method'].widget.attrs.update({'class': 'form-select'})

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0")
        
        return cleaned_data


class TransactionFilterForm(forms.Form):
    """Form for filtering transactions"""

    FILTER_CHOICES = [
        ('all', 'All Transactions'),
        ('income', 'Income Only'),
        ('expense', 'Expense Only'),
    ]

    transaction_type = forms.ChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    amount_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Amount',
            'step': '0.01'
        })
    )
    amount_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Amount',
            'step': '0.01'
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user, is_active=True)
            self.fields['payment_method'].queryset = PaymentMethod.objects.filter(user=user, is_active=True)