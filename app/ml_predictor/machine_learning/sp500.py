"""
- author: Johannes Hötter (https://github.com/johannes-hoetter)
- version: 1.0
- last updated on: 08/12/2018

This script embeds the several models for a single SP500 Predictor.
"""

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

# the saved statistics will be needed to determine whether a model is good enough to use it
with open('stats/training_stats.p', 'rb') as stats_file:
    statistics = pickle.load(stats_file)

# Load data for single inputs
data_handler = DataHandler()
data_handler.initialize('../tools/serialized_tool_objects/datahandler.p')


class SP500Predictor:
    """
    Wrapper for all the models. Can be used to predict prices for selected stocks in the Standard & Poor's 500 Index.
    Technically, this predictor is just a big dictionary encapsulating all the models. At runtime, it'll determine which
    stock the user wants to predict and uses the specific model for prediction.

    CAUTION: the model can only make predictions, if the method activate is called after the object has been created.
    """

    def __init__(self):
        """
        Initialize the Predictor.

        CAUTION: the model can only make predictions, if the method activate is called after the object has been created.
        """
        self.models = {}
        self.useable_models = {}


    def activate(self, model_dir='models'):
        """
        Activate the model so that it loads all the Neural Networks into Main Memory. If this isn't called,
        the SP500Predictor can't make any predictions at all!
        :param model_dir (string): name of the directory where all the neural networks are
        """

        for symbol in statistics.keys():
            model = NeuralNetwork(15)  # if features get added, this needs to change
            try:
                # Store the "good" models in the dictionary, so that they can be used
                model.initialize('{}/{}_regressor.pth'.format(model_dir, symbol))
                self.models[symbol] = model
                if statistics[symbol]['near_real_price'] == 'X':
                    self.useable_models[symbol] = model
            except:
                continue

    def predict(self, *symbols, timerange='D'):
        """
        Predict for a number of symbols
        :param symbols (string):    contains the symbols of the companies which the models tries to predict the price for.
                                    the stock names are separated by whitespaces (e.g. "AMZN FE GOOG")
        :param timerange (char, possible values: 'D', 'W', 'M', 'Y'): NOT ADDED AT THE MOMENT, TODO!
        :return OrderedDict: containing the predictions for each company the model was able to make a prediction for
        """

        predictions = OrderedDict()
        for symbol in symbols:
            if statistics[symbol]['near_real_price'] == 'X':
                try:
                    # Input values get inferred, the model uses the latest information it had (taken from the dataloader)
                    # The user can only input the Stock Symbol
                    x = self.get_todays_values(symbol)
                    pred = self.models[symbol].predict([x])
                    predictions[symbol] = pred
                except:
                    continue
            else:
                predictions[symbol] = None  # model is not "sure" enough
        return predictions
        # note: timeranges will be implemented next


    def predict_history(self, *symbols, path='', max=None):
        """
        Get predictions for each of the already past days. Those values can be compared to actual values
        :param symbols (string):    contains the symbols of the companies which the models tries to predict the price for.
                                    the stock names are separated by whitespaces (e.g. "AMZN FE GOOG")
        :param path (string):       path where the stock data lies
        :param max (int):           number of values which get predicted (from now to past days)
        :return OrderedDict: containing the predictions for each company the model was able to make a prediction for
        """

        predictions = OrderedDict()
        for symbol in symbols:
            if statistics[symbol]['near_real_price'] == 'X':
                preds = []
                if path == '':
                    X, _ = data_handler.load_from_npz(symbol)
                else:
                    X, _ = data_handler.load_from_npz(symbol, path=path)
                if max:
                    X = X[-max:] # only get the most recent ones
                    for idx, x in enumerate(X):
                        if idx == max: break
                        pred = self.models[symbol].predict([x])
                        preds.append(pred)
                else:
                    for x in X:
                        pred = self.models[symbol].predict([x])
                        preds.append(pred)
                predictions[symbol] = preds
            else:
                predictions[symbol] = None  # model is not "sure" enough
        return predictions


    def get_todays_values(self, symbol):
        """
        Get the model inputs for the last day which was found in the training data
        :param symbol (string): stock symbol of the company
        :return numpy-array: containing the input values for the model
        """
        # needs to be changed sometime in the future into an optimized solution!
        path = os.path.join(os.getcwd(), 'ml_predictor', 'data', 'ml_format')
        x, _ = data_handler.load_from_npz(symbol, path)
        return x[-1]

    def get_todays_prices(self, symbol):
        """
        Get the model label for the last day which was found in the training data
        :param symbol (string): stock symbol of the company
        :return numpy-array: containing the label values for the model
        """
        # needs to be changed sometime in the future into an optimized solution!
        path = os.path.join(os.getcwd(), 'ml_predictor', 'data', 'ml_format')
        _, y = data_handler.load_from_npz(symbol, path)
        return y[-1]

os.chdir(owd) # really important, otherwise server can't be started!
if __name__ == '__main__': # testwise

    sp500_predictor = SP500Predictor()
    sp500_predictor.activate()
    print(sp500_predictor.predict('AAPL'))