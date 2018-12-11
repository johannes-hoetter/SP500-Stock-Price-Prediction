"""
- author: Johannes Hötter (https://github.com/johannes-hoetter)
- version: 1.0
- last updated on: 05/12/2018

This file contains several User Input Forms for the SP500 Predictor Application
"""

from django import forms
from django.forms import Form, TextInput, CharField

# Input Form for when the User gives Stock Data as a String
class StockInputForm(forms.Form):
    stock_names = forms.CharField(label='Stock', required=False)
    stock_names.label = ""

# Input Form for when the User wants a number of recommendations
class StockNumForm(forms.Form):
    num_stocks = forms.CharField(label='Number of Recommendations', required=False,  widget=TextInput(attrs={'type':'number'}))
    num_stocks.label = ""