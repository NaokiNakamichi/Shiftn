from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from boards.models import GENDER_CHOICES
from .models import EXPERIENCE_CHOICE
class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    gendar =  forms.ChoiceField(label='性別', choices=GENDER_CHOICES, required=True)
    experience =  forms.ChoiceField(label='経験年数', choices=EXPERIENCE_CHOICE, required=False)
    class Meta:
        model = User
        fields = ('username', 'email','gendar','experience', 'password1', 'password2')
