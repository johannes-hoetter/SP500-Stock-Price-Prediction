from django.shortcuts import render
from .forms import StockInputForm, StockNumForm

# make the sp500 module available
import sys
sys.path.append("..")
from ml_predictor.machine_learning.sp500 import SP500Predictor #if underlined, ignore
from ml_predictor.tools.data_handler import DataHandler #if underlined, ignore

from datetime import datetime as dt

import os
sp500predictor = SP500Predictor()
path = os.path.join(os.getcwd(), 'ml_predictor', 'machine_learning', 'models')
print("Activating Model...")
sp500predictor.activate(path)
print("Model has been activated. Ready for Predictive Analytics.")
data_handler = DataHandler()
path = os.path.join(os.getcwd(), 'ml_predictor', 'tools', 'serialized_tool_objects', 'datahandler.p')
print("Initializing DataHandler...")
data_handler.initialize(path)
print("DataHandler has been initialized.")


def index(request):
    # TODO:
    # application logic out of views!
    preds = {}
    data_prices, data_predictions, data_dates, symbol = get_data_for_chart('AMZN')
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
                try:
                    data_prices, data_predictions, data_dates, symbol = get_data_for_chart(list(preds)[0])
                except:
                    pass
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
                except:
                    print("No Input given for num_form even though submitted")
                try:
                    data_prices, data_predictions, data_dates, symbol = get_data_for_chart(list(preds)[0])
                except:
                    pass
    else:
        stock_form = StockInputForm()
        num_form = StockNumForm()


    request_dict = {
        'stock_form': stock_form,
        'num_form': num_form,
        'preds': preds,
        'models': sp500predictor.useable_models.keys(),
        'data_prices': data_prices,
        'data_preds': data_predictions,
        'data_dates': data_dates,
        'data_symbol': symbol
    }
    return render(request, 'sp500predictor/index.html', request_dict)

def get_data_for_chart(symbol):
    path = os.path.join(os.getcwd(), 'ml_predictor', 'data', 'ml_format')
    pred_prices = list(sp500predictor.predict_history(symbol, path=path, max=365).values())[0]
    _, real_prices = data_handler.load_from_npz(symbol, path=path, max=365)
    real_prices = real_prices.tolist()
    path = os.path.join(os.getcwd(), 'ml_predictor', 'data', 'raw')
    df = data_handler.load_from_csv(symbol, path)
    dates = [int("{}".format(date.replace('-', ''))) for date in df['Date']]
    dates = sorted(dates[:365])
    return real_prices, pred_prices, dates, symbol