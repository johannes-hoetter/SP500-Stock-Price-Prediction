from django.shortcuts import render
from .forms import StockInputForm, StockNumForm

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
    # TODO:
    # application logic out of views!
    preds = {}
    if request.method == 'POST':
        if 'stock_names' in request.POST:
            stock_form = StockInputForm(request.POST)
            num_form = StockNumForm()
            if stock_form.is_valid():
                stocks = stock_form.cleaned_data['stock_names'].split()
                for stock in stocks:
                    try:
                        pred = [val for val in sp500predictor.predict(stock).values()][0] # convert from ODict to Value
                        preds[stock]= pred
                    except:
                        print("Tried prediction for {}, which isn't contained in Model.".format(stock))
                print(preds)
        elif 'num_stocks' in request.POST:
            num_form = StockNumForm(request.POST)
            stock_form = StockInputForm()
            if num_form.is_valid():
                try:
                    num = int(num_form.cleaned_data['num_stocks'])
                    stocks = [symbol for symbol in sp500predictor.models.keys()]
                    pred = sp500predictor.predict(*stocks)
                    for stock in pred:
                        try:
                            val_today = sp500predictor.get_todays_prices(stock)
                            preds[stock] = pred[stock] / val_today
                        except:
                            continue
                    preds = [key for key, value in sorted(preds.items(), key=lambda x: x[1])]
                    if num > 0:
                        preds = preds[-num:]
                    preds = {stock: pred[stock] for stock in reversed(preds)}
                    print(preds)
                except:
                    print("No Input given for num_form even though submitted")
    else:
        stock_form = StockInputForm()
        num_form = StockNumForm()

    request_dict = {
        'stock_form': stock_form,
        'num_form': num_form,
        'preds': preds
    }
    return render(request, 'sp500predictor/index.html', request_dict)

def go(request):
    print("!!!")
    return render(request, 'sp500predictor/go.html')