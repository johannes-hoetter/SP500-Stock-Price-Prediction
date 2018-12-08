# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 05/12/2018

import torch
try:
    import _pickle as pickle
except:
    import pickle
from neuralnet import NeuralNetwork
from tools.data_handler import DataHandler

with open('stats/training_stats.p', 'rb') as stats_file:
    statistics = pickle.load(stats_file)
    
data_handler = DataHandler()
data_handler.initialize('../tools/serialized_tool_objects/datahandler.p')
    
class SP500Predictor:
    
    def __init__(self):
        self.models = {}

    
    def activate(self, model_dir='models'):
        for symbol in statistics.keys():
            model = NeuralNetwork(15) # if features get added, this needs to change
            try:
                model.initialize('{}/{}_regressor.pth'.format(model_dir, symbol))
                self.models[symbol] = model
            except:
                continue
    
    
    def predict(self, *symbols):
        predictions = {}
        for symbol in symbols:
            try:
                x = self.get_todays_values(symbol)
                pred = self.models[symbol].predict([x])
                predictions[symbol] = pred
            except:
                continue
        return predictions
                
        
    def get_todays_values(self, symbol):
        # needs to be changed sometime in the future into an optimized solution!
        x, _ = data_handler.load_from_npz(symbol)
        return x[-1]