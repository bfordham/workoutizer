from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class UserProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('public_profile',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the checkbox properly
        self.fields['public_profile'].widget.attrs['class'] = 'form-check-input'


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user