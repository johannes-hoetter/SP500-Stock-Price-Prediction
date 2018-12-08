from django import forms

class StockInputForm(forms.Form):
    stock_names = forms.CharField(label='Stock', required=True)
