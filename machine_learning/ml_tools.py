# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 02/12/2018

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import SubsetRandomSampler

class DataWrapper(Dataset):
    
    def __init__(self, data, target):
        self.data = torch.from_numpy(data)
        self.target = target
        self.shape = data.shape
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx], self.target[idx]
    
    def get_dataloader(self, test_size_ratio=0.25, shuffle_dataset=True, train_batch_size=64, test_batch_size=32):
        indices = list(range(len(self)))
        split = int(np.floor(test_size_ratio * len(self)))
        if shuffle_dataset :
            np.random.shuffle(indices)
        train_indices, test_indices = indices[split:], indices[:split]

        trainsampler = SubsetRandomSampler(train_indices)
        testsampler = SubsetRandomSampler(test_indices)

        traindataloader = DataLoader(self, batch_size=train_batch_size, sampler=trainsampler)
        testdataloader = DataLoader(self, batch_size=test_batch_size, sampler=testsampler)

        dataloader = {'train': traindataloader, 'test': testdataloader}
        return dataloader