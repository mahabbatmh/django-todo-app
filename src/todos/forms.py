from django import forms
from django.contrib.auth.models import User

from .models import Todo


class TodoForm(forms.ModelForm):
    client_time_zone = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Todo
        fields = ('title', 'description', 'complete_date', 'client_time_zone')
