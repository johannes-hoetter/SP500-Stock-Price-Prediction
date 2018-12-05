# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 04/12/2018

import torch
from torch import nn
import torch.nn.functional as F

import numpy as np
import timeit

class NeuralNetwork(nn.Module):
        
    def __init__(self, num_inputs, drop_p=0.1):
        
        super().__init__()
        self.num_inputs = num_inputs
        self.fc1 = nn.Linear(self.num_inputs, 128)
        self.bn1 = nn.BatchNorm1d(128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)
        self.dropout = nn.Dropout(p=drop_p)
        
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        
    def forward(self, x):
        
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
        rmse = 0
        accuracy = 0
        n = len(testloader)
        if n == 0:
            return np.nan
        with torch.no_grad():
            for inputs, targets in testloader:
                if len(inputs) == 1:
                    n -= 1
                    break
                inputs, targets  = inputs.to(self.device).float(), targets.to(self.device).float() # gpu/cpu
                outputs = self.forward(inputs)
                outputs = outputs.view(outputs.numel()) # [32 x 1] -> [32]
                rmse += torch.sqrt(criterion(outputs, targets)).item()
        return rmse / n
    
    
    def predict(self, x):
        tensor = torch.from_numpy(np.array(x)).float()
        tensor = tensor.to(self.device)
        self.to(self.device)
        output = self.forward(tensor).item()
        return abs(output)

    
    def serialize(self, path):
        state = {'state_dict': self.state_dict(),
                 'num_inputs': self.num_inputs}
        torch.save(state, path)
    
    
    def initialize(self, path):
        ckpt = torch.load(path)
        self.num_inputs = ckpt['num_inputs']
        self.load_state_dict(ckpt['state_dict'])
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.to(self.device) # using the model on gpu/cpu
        self.eval()