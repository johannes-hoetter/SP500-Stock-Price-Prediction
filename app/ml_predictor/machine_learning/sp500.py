# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 08/12/2018

import torch
import numpy as np
try:
    import _pickle as pickle
except:
    import pickle
from collections import OrderedDict

from .neuralnet import NeuralNetwork
from ..tools.data_handler import DataHandler

# this way the files can be opened from other modules
import os
owd = os.getcwd()
cwd = os.path.join(os.getcwd(), 'ml_predictor', 'machine_learning')
os.chdir(cwd)

with open('stats/training_stats.p', 'rb') as stats_file:
    statistics = pickle.load(stats_file)

data_handler = DataHandler()
data_handler.initialize('../tools/serialized_tool_objects/datahandler.p')


class SP500Predictor:

    def __init__(self):
        self.models = {}
        self.useable_models = {}


    def activate(self, model_dir='models'):
        for symbol in statistics.keys():
            model = NeuralNetwork(15)  # if features get added, this needs to change
            try:
                model.initialize('{}/{}_regressor.pth'.format(model_dir, symbol))
                self.models[symbol] = model

                # added testwise!
                if statistics[symbol]['near_real_price'] == 'X':
                    self.useable_models[symbol] = model
            except:
                continue

    def predict(self, *symbols, timerange='D'):
        predictions = OrderedDict()
        for symbol in symbols:
            if statistics[symbol]['near_real_price'] == 'X':
                try:
                    x = self.get_todays_values(symbol)
                    pred = self.models[symbol].predict([x])
                    predictions[symbol] = pred
                except:
                    continue
            else:
                predictions[symbol] = None  # model is not "sure" enough
        return predictions
        # note: timeranges will be implemented next


    def predict_history(self, *symbols):
        predictions = OrderedDict()
        for symbol in symbols:
            if statistics[symbol]['near_real_price'] == 'X':
                preds = []
                X, _ = data_handler.load_from_npz(symbol)
                for x in X:
                    pred = self.models[symbol].predict([x])
                    preds.append(pred)
                predictions[symbol] = preds
            else:
                predictions[symbol] = None  # model is not "sure" enough
        return predictions


    def get_todays_values(self, symbol):
        # needs to be changed sometime in the future into an optimized solution!
        path = os.path.join(os.getcwd(), 'ml_predictor', 'data', 'ml_format')
        x, _ = data_handler.load_from_npz(symbol, path)
        return x[-1]

    def get_todays_prices(self, symbol):
        # needs to be changed sometime in the future into an optimized solution!
        path = os.path.join(os.getcwd(), 'ml_predictor', 'data', 'ml_format')
        _, y = data_handler.load_from_npz(symbol, path)
        return y[-1]

os.chdir(owd)
if __name__ == '__main__':

    sp500_predictor = SP500Predictor()
    sp500_predictor.activate()
    print(sp500_predictor.predict('AAPL'))