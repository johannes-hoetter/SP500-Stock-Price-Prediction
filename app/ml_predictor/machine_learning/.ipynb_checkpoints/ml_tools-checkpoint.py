# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 04/12/2018

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import SubsetRandomSampler

class MLDataWrapper():
    
    def __init__(self, data, target):
        self.dataset = MLData(data, target)
        self.shape = self.dataset.shape
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset.__getitem__(idx)
    
    def get_dataloader(self, test_size_ratio=0.25, shuffle_dataset=True, train_batch_size=64, test_batch_size=32):
        indices = list(range(len(self)))
        split = int(np.floor(test_size_ratio * len(self)))
        if shuffle_dataset :
            np.random.shuffle(indices)
        train_indices, test_indices = indices[split:], indices[:split]

        traindata = self.dataset.get_subset(train_indices)
        testdata = self.dataset.get_subset(test_indices)
                
        traindataloader = DataLoader(traindata, batch_size=train_batch_size)
        testdataloader = DataLoader(testdata, batch_size=test_batch_size)
        
        dataloader = {'train': traindataloader, 'test': testdataloader}
        return dataloader
    
class MLData(Dataset):
    
    def __init__(self, data, target, is_pytorch_tensor=True):
        if not is_pytorch_tensor:
            self.data = torch.from_numpy(data)
        else:
            self.data = data
        self.target = target
        self.shape = data.shape
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx], self.target[idx]
    
    def get_subset(self, indices):
        return MLData(self.data[indices], self.target[indices])