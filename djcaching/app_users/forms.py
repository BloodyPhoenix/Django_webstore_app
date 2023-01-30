from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Address, BalanceModel


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    name = forms.CharField(min_length=3, max_length=50, help_text=_("Имя"))
    surname = forms.CharField(min_length=3, max_length=100, help_text=_("Фамилия"))
    country = forms.CharField(max_length=150, help_text=_('Страна'))
    town = forms.CharField(max_length=150, help_text=_("Город"))
    street = forms.CharField(max_length=200, help_text=_("Улица"))
    house = forms.CharField(max_length=25,  help_text=("Номер дома"))
    flat = forms.IntegerField(help_text=_('Номер квартиры'), required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class AddAddressForm(forms.ModelForm):

    class Meta:
        model = Address
        exclude = ['user']


class BalanceReplenishForm(forms.Form):
    cash_added = forms.FloatField(help_text=_("Сколько денег вы хотите внести?"))