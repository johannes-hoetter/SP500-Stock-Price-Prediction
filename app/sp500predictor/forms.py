from django import forms
from django.forms import Form, TextInput, CharField

class StockInputForm(forms.Form):
    stock_names = forms.CharField(label='Stock', required=False)

class StockNumForm(forms.Form):
    num_stocks = forms.CharField(label='Number of Recommendations', required=False,  widget=TextInput(attrs={'type':'number'}))