"""
- author: Johannes Hötter (https://github.com/johannes-hoetter)
- version: 1.0
- last updated on: 05/12/2018

Class for the Neural Networks which will be used to infer stock prices. For the SP500 Predictor, multiple models (one per
company) will be developed.
"""
import torch
from torch import nn
import torch.nn.functional as F

import numpy as np
import timeit

class NeuralNetwork(nn.Module):
    """
    Class for the Neural Network, one object of this class represents an Artificial Neural Network.
    """

    def __init__(self, num_inputs, drop_p=0.1):
        """
        Initialize the Neural Network
        :param num_inputs (int):    Number of Features which the model gets in the input layer
        :param drop_p (float):      value between 0 and 1 which give the ratio for each neuron during
                                    training phase, that the neuron gets ignored. Usually, this provides
                                    a better result and reduces overfitting
        """

        super().__init__()
        self.num_inputs = num_inputs
        self.fc1 = nn.Linear(self.num_inputs, 128)
        self.bn1 = nn.BatchNorm1d(128) # add BatchNormalization (values will be scaled in the batch)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)
        self.dropout = nn.Dropout(p=drop_p) # activate possibility to use Dropout
        
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu') # infer if the model
        # needs to use a cpu or can use a gpu for training
        
    def forward(self, x):
        """
        Forward Pass through the neural network
        :param x (tensor array): input for the neural network
        :return float: value which the model predicts for the input (scientific notation: ^y)
        """

        # Input Layer
        x = self.fc1(x)
        x = self.bn1(F.relu(x))
        x = self.dropout(x)
        
        # Hidden Layer
        x = self.fc2(x)
        x = self.dropout(x)
        
        # Output Layer
        return self.fc3(x)
    
    
    def fit(self, dataloader, symbol, optimizer, criterion, num_epochs, print_every=100, lr_decay=0.95, path='', eval=True, return_stats=True):
        """
        Train the model on a given data.
        :param dataloader (dictionary):         Contains the Training/Testing Data in batches, normally shuffled
        :param symbol (string):                 String Representation of the Stock, e.g. 'AMZN' for Amazon
        :param optimizer (pytorch optimizer):   Optimizer to use for Model Upgrading
        :param criterion (pytorch criterion):   Criterion to use for Model Evaluation
        :param num_epochs (int):                Number of times the whole Dataset gets iterated through
        :param print_every (int):               Defines when to print the training log for the current situation, e.g.
                                                print_every = 100 -> after 100 batches, the current situation will be logged
        :param lr_decay (float):                number near 1 but a little smaller (e.g. 0.99), which will be used a factor
                                                for the learning rate each epoch. As a result, the learning rate will get
                                                smaller after each epoch
        :param path (string):                   path where the model gets serialized to
        :param eval (bool):                     if true, the model gets evaluated with training logs
        :param return_stats (bool):             if true, several return values for statistical purpose will be given
        :return bool, float, float, float:  model has improved significantly; first test RMSE; best test RMSE; time needed for training
        """

        # Default dir for saved models: 'models/'
        if path == '':
            path = 'models/{}_regressor.pth'.format(symbol)
            
        # Begin of Training (init screen, prepare variables etc.)    
        print("----------------------------------------------------------------------------")
        print("|START TRAINING FOR SYMBOL: [{:>4}]                                         |".format(symbol))
        print("| TRAIN EPOCH | PROCESSED DATA      | TRAIN RMSE | TEST RMSE  | CHECKPOINT |")
        print("----------------------------------------------------------------------------")
        self.to(self.device) # cpu / gpu
        self.train() # put model into train mode (dropout activated)
        best_test_rmse = float('inf')
        first_test_rmse = None # needed if training gets evaluated
        start = timeit.default_timer()
            
        # Training Process
        for epoch in range(num_epochs):
            optimizer.param_groups[0]['lr'] *= lr_decay # adapt learning rate 
            for batch_idx, (inputs, targets) in enumerate(dataloader['train']):
                if len(inputs) == 1: # exception handling (due to Batch Normalization)
                    break # as the only possible case for this is at the end of the loop, we can stop the loop at all
                inputs, targets = inputs.to(self.device).float() , targets.to(self.device).float()

                # Update Weights
                optimizer.zero_grad()
                outputs = self(inputs)
                outputs = outputs.view(outputs.numel())
                rmse = torch.sqrt(criterion(outputs, targets))
                rmse.backward()
                optimizer.step()

                # Print Logs & Test on testing data
                if batch_idx % print_every == 0:
                    test_rmse = self.validate(dataloader['test'], criterion)
                    if first_test_rmse is None:
                        first_test_rmse = test_rmse
                    if test_rmse < best_test_rmse:
                        best_test_rmse = test_rmse
                        self.serialize(path) # save the model in the given directory
                        is_checkpoint = 'X'
                    else:
                        is_checkpoint = ''
                    print('| {:4}/{:4}   | {:6}/{:6} ({:2.0f}%) |  {:7.2f}   |  {:7.2f}   |     {:1}      |'.
                          format(epoch + 1, 
                                 num_epochs, 
                                 batch_idx * len(inputs), 
                                 len(dataloader['train']) * dataloader['train'].batch_size,
                                 100. * batch_idx / len(dataloader['train']), 
                                 rmse.item(),
                                 test_rmse, 
                                 is_checkpoint))
                    
        # End of Training            
        stop = timeit.default_timer()
        seconds = round(stop - start)
        self.eval() # put model into evaluation mode (no dropout)
        
        # print statistics
        print("----------------------------------------------------------------------------")
        if eval:
            print("|TIME NEEDED FOR TRAINING: {:5.0f} SEC.                                      |".format(np.round(seconds,2)))
            if best_test_rmse <= (first_test_rmse / 8): 
                # model has improved significantly (value 8 for division is arbitrary, seemed to be a good threshold while training)
                print("|FINISHED TRAINING. MODEL HAS IMPROVED SIGNIFICANTLY.                      |")
                improved = True
            else:
                print("|FINISHED TRAINING. MODEL HAS NOT IMPROVED SIGNIFICANTLY.                  |")
                improved = False
        else:
            print("|FINISHED TRAINING.                                                        |")
        print("----------------------------------------------------------------------------")
        print()
        if eval and return_stats:
            return improved, first_test_rmse, best_test_rmse, seconds
    
   
    def validate(self, testloader, criterion):
        """
        Validate the model results on a test dataset on a given criterion
        :param testloader (pytorch dataloader):     Contains the Dataset
        :param criterion (pytorch criterion):       Criterion which is being used for Model Evaluation
        :return float: Test RMSE
        """

        rmse = 0
        n = len(testloader)
        # if the testloader is empty, return np.nan
        if n == 0:
            return np.nan
        with torch.no_grad():
            for inputs, targets in testloader:
                if len(inputs) == 1: # error handling (due to BatchNormalization)
                    n -= 1
                    break
                inputs, targets  = inputs.to(self.device).float(), targets.to(self.device).float() # gpu/cpu
                outputs = self.forward(inputs)
                outputs = outputs.view(outputs.numel()) # [32 x 1] -> [32]
                rmse += torch.sqrt(criterion(outputs, targets)).item() # calculate the error
        return rmse / n # return mean error
    
    
    def predict(self, x):
        """
        Use the model on a single input (for production usage)
        :param x (numpy array): numpy array containing a single input row
        :return float: predicted value
        """

        tensor = torch.from_numpy(np.array(x)).float() # model needs the tensor in this format

        # cpu or gpu available?
        tensor = tensor.to(self.device)
        self.to(self.device)
        output = self.forward(tensor).item()
        return abs(output) # negative values don't make sense

    
    def serialize(self, path):
        """
        Save the model to a given path
        :param path (string): Path where the model gets saved to
        """

        state = {'state_dict': self.state_dict(), # weights between neurons (what gets learned)
                 'num_inputs': self.num_inputs}
        torch.save(state, path)
    
    
    def initialize(self, path):
        """
        Initialize a model from a saved file (.pth)
        :param path (string): Path where the model has been saved
        :return NeuralNetwork: Neural Network which contains the trained neuron-connections (weights)
        """

        if torch.cuda.is_available():
            self.device = torch.device('cuda:0')
            ckpt = torch.load(path)
        else:
            self.device = torch.device('cpu')
            ckpt = torch.load(path, map_location='cpu')
        self.num_inputs = ckpt['num_inputs']
        self.load_state_dict(ckpt['state_dict'])
        self.to(self.device) # using the model on gpu/cpu
        self.eval() # don't use dropout!