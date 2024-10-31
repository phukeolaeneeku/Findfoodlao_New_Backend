from .models import ReviewModel
from django.forms import ModelForm, TextInput, PasswordInput, EmailInput, Textarea, NumberInput

# from django.contrib.auth import get_user_model


class ReviewForm(ModelForm):
    class Meta:
        model = ReviewModel
        fields = ['review', 'star', ]

        widgets = {
            'review': Textarea(attrs={
                'placeholder': 'Please write at least 10 characters.'
            }),
            'star': NumberInput(attrs={
                'class': "form-control",
                'placeholder': 'Email'
            }),
        }

