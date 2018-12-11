# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 02/12/2018

import torch
from torch import optim
from torch import nn

import numpy as np
import timeit

try:
    import _pickle as pickle
except:
    import pickle

import sys
sys.path.append("..")
sys.path.append(".")

# Custom Modules
from tools.data_handler import DataHandler
from ml_tools import MLDataWrapper
from neuralnet import NeuralNetwork

if __name__ == '__main__':

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    data_handler = DataHandler()
    data_handler.initialize(path='../tools/serialized_tool_objects/datahandler.p')
    data = {}
    mean_price = {}
    for symbol in data_handler.symbols:
        X, y = data_handler.load_from_npz(symbol)
        mean_price[symbol] = np.mean(y[-365:])  # avg price of the stock in last year
        ml_data_wrapper = MLDataWrapper(X, y)
        data_loader = ml_data_wrapper.get_dataloader(train_batch_size=64)  # default train/test size of 0.75 to 0.25
        data[symbol] = data_loader

    # Hyperparameter
    alpha = 0.01  # Learning Rate, model uses learning rate decay (95% of last alpha in each epoch)
    num_epochs = 100
    print_every = 30
    dropout_prob = 0.3

    num_inputs = ml_data_wrapper.shape[1]
    print("The models have {} input nodes".format(num_inputs))

    stats = {}
    start = timeit.default_timer()

    # for each symbol, train a new neural network and save it in a folder
    # for the final regressor, the models will be loaded into a dictionary
    # given on the input symbol for the model, a price will be calculated
    # on the symbol-model
    for symbol, dataloader in data.items():
        stats[symbol] = {}
        model = NeuralNetwork(num_inputs, drop_p=dropout_prob)
        model = model.to(device)

        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=alpha)

        improved, first_test_rmse, best_test_rmse, seconds = \
            model.fit(dataloader, symbol, optimizer, criterion, num_epochs, print_every=print_every)

        # Create some statistics (maybe used later on)
        if improved:
            stats[symbol]['learned_significantly'] = 'X'
        else:
            stats[symbol]['learned_significantly'] = '-'
        if best_test_rmse <= (mean_price[symbol] / 10):
            stats[symbol]['near_real_price'] = 'X'
        else:
            stats[symbol]['near_real_price'] = '-'
        stats[symbol]['first_test_rmse'] = first_test_rmse
        stats[symbol]['best_test_rmse'] = best_test_rmse
        stats[symbol]['avg_real_price_last_year'] = mean_price[symbol]
        stats[symbol]['seconds_trained'] = seconds
        stats[symbol]['num_data_train'] = len(dataloader['train'].dataset)
        stats[symbol]['num_data_test'] = len(dataloader['test'].dataset)

    stop = timeit.default_timer()
    seconds_total = stop - start
    print("TOTAL TIME NEEDED: {:2.0f} MIN.".format(seconds_total / 60))

    # Save the statistics
    with open('stats/training_stats.p', 'wb') as file:
        pickle.dump(stats, file)