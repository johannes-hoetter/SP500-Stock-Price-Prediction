# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 02/12/2018

import torch
from torch import nn
import torch.nn.functional as F

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
    
    
    def fit(self, dataloader, symbol, optimizer, criterion, num_epochs, print_every=100, lr_decay=0.99, path=''):
        if path == '':
            path = 'models/{}_regressor.pth'.format(symbol)
        print("Start Training...")
        start = timeit.default_timer()
        self.to(self.device)
        self.train() # put model into train mode (dropout activated)
        best_test_rmse = float('inf')
        for epoch in range(num_epochs):
            optimizer.param_groups[0]['lr'] *= lr_decay # adapt learning rate 
            for batch_idx, (inputs, targets) in enumerate(dataloader['train']):
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
                    if test_rmse < best_test_rmse:
                        best_test_rmse = test_rmse
                        self.serialize(path)
                        is_checkpoint = 'X'
                    else:
                        is_checkpoint = ''
                    print('Train Epoch: {}/{} [{}/{} ({:.0f}%)] .. Train RMSE: {:.2f} .. Test RMSE: {:.2f} .. Checkpoint: {}'.
                          format(epoch + 1, 
                                 num_epochs, 
                                 batch_idx * len(inputs), 
                                 len(dataloader['train']) * dataloader['train'].batch_size,
                                 100. * batch_idx / len(dataloader['train']), 
                                 rmse.item(),
                                 test_rmse, 
                                 is_checkpoint))
        stop = timeit.default_timer()
        seconds = stop - start
        print("Time needed for Training: {}".format(np.round(seconds,2)))
        print("Finished Training!")
        self.eval() # put model into evaluation mode (no dropout)
    
   
    def validate(self, testloader, criterion):
        rmse = 0
        accuracy = 0
        n = len(testloader)
        with torch.no_grad():
            for inputs, targets in testloader:
                inputs, targets  = inputs.to(self.device).float(), targets.to(self.device).float() # gpu/cpu
                outputs = self.forward(inputs)
                outputs = outputs.view(outputs.numel()) # [32 x 1] -> [32]
                rmse += torch.sqrt(criterion(outputs, targets)).item()
        return rmse / n
    
    
    def predict(self, x, device='cpu'):
        tensor = torch.from_numpy(np.array(x)).float()
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