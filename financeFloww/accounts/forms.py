from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class UserProfileForm(forms.ModelForm):
    """Form for user profile updates"""

    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'phone', 'currency', 'monthly_income_goal', 'monthly_savings_goal']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].widget.attrs.update({
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell us about yourself'
        })
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
        self.fields['currency'].widget.attrs.update({'class': 'form-select'})
        self.fields['monthly_income_goal'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Monthly Income Goal',
            'step': '0.01'
        })
        self.fields['monthly_savings_goal'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Monthly Savings Goal',
            'step': '0.01'
        })


class UserUpdateForm(UserChangeForm):
    """Form for updating user information"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})