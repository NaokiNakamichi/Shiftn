from django import forms
from django.forms import formset_factory
from .models import Topic, Post, Department, Shift, Management,ShiftDetail,ManagementDetail,ManagementNeed

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
        fields = ['message']

class GroupCreateForm(forms.ModelForm):
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    class Meta:
        model = Department
        fields = ['name', 'password']

class ShiftSubmitForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['hope','year','month','date','part']
        widgets = {
                'year': forms.HiddenInput(),
                'month': forms.HiddenInput(),
                'date': forms.HiddenInput(),
                'part': forms.HiddenInput(),
        }
ShiftSubmitFormSet = forms.modelformset_factory(Shift,form=ShiftSubmitForm,extra=0)


class ShiftManagementForm(forms.ModelForm):
    class Meta:
        model = Management
        fields = ['year','month','date','part']
        widgets = {
                'year': forms.HiddenInput(),
                'month': forms.HiddenInput(),
                'date': forms.HiddenInput()
        }
ShiftManagementFormSet = forms.modelformset_factory(Management,form=ShiftManagementForm,extra=0)

class ManagementNeedForm(forms.ModelForm):
    class Meta:
        model = ManagementNeed
        fields = ['year','month','date','need','part']
        widgets = {
            'year': forms.HiddenInput(),
            'month': forms.HiddenInput(),
            'date': forms.HiddenInput(),
            'part': forms.HiddenInput(),
        }
ManagementNeedFormSet = forms.modelformset_factory(ManagementNeed,form=ManagementNeedForm,extra=0)

class ShiftDetailForm(forms.ModelForm):
    class Meta:
        model = ShiftDetail
        fields = ['degree','year','month','comment','department','user']
        widgets = {
                'year': forms.HiddenInput(),
                'month': forms.HiddenInput(),
                'department': forms.HiddenInput(),
                'user': forms.HiddenInput(),
        }

class ManageDetailForm(forms.ModelForm):
    class Meta:
        model = ManagementDetail
        fields = ['relation','min_women','max0','min0','max1','min1','max2','min2','min_veteran','renkin_max']
        widgets = {
                'relation': forms.HiddenInput(),
                'year': forms.HiddenInput(),
                'month': forms.HiddenInput(),
        }
