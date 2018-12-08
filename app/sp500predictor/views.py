from django.shortcuts import render
from .forms import StockInputForm

# make the sp500 module available
import sys
sys.path.append("..")
from ml_predictor.machine_learning.sp500 import SP500Predictor #if underlined, ignore

import os
sp500predictor = SP500Predictor()
path = os.path.join(os.getcwd(), 'ml_predictor', 'machine_learning', 'models')
print("Activating Model...")
sp500predictor.activate(path)
print("Model has been activated. Ready for Predictive Analytics.")


def index(request):


    preds = None
    if request.method == 'POST':
        form = StockInputForm(request.POST)
        if form.is_valid():
            stocks = form.cleaned_data['stock_names'].split()
            print(stocks)
            for stock in stocks:
                try:
                    print(sp500predictor.predict(stock))
                except:
                    print("Tried prediction for {}, which isn't contained in Model.".format(stock))

    else:
        form = StockInputForm()

    return render(request, 'sp500predictor/index.html', {'form': form, 'preds': preds})

def go(request):
    print("!!!")
    return render(request, 'sp500predictor/go.html')