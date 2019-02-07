from django import forms
from django.forms import formset_factory
from .models import Topic, Post, Department, Shift, Management

class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.'
    )

    class Meta:
        model = Topic
        fields = ['subject', 'message']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]

class GroupCreateForm(forms.ModelForm):
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    class Meta:
        model = Department
        fields = ['name', 'password']

class ShiftSubmitForm(forms.ModelForm):
    pass

class ShiftManagementForm(forms.ModelForm):
    class Meta:
        model = Management
        fields = ['need','year','month','date','part']
        widgets = {
                'year': forms.HiddenInput(),
                'month': forms.HiddenInput(),
                'date': forms.HiddenInput()
        }
ShiftManagementFormSet = forms.modelformset_factory(Management,form=ShiftManagementForm,extra=0)
