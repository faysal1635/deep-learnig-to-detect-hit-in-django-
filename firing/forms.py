from dataclasses import Field
from pyexpat import model
from attr import field
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from firing.models import Fire


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', ]


class FireForm(ModelForm):
    class Meta:
        model = Fire
        exclude = ['new_target', 'hits', 'detected', 'detected_hits', ]
