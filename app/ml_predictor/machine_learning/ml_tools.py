"""
- author: Johannes Hötter (https://github.com/johannes-hoetter)
- version: 1.0
- last updated on: 04/12/2018

This module contains various tools which can be used for general machine learning tasks.
File will be incrementally updated. Right now it contains:
- MLDataWrapper -> provides machine learning data i.e. in a dataloader (batched, train/test ratio, ...)
- MLData        -> dataset which is used from the MLDataWrapper. mostly internal use in this class.
"""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import SubsetRandomSampler

class MLDataWrapper():
    """
    use this class to wrap data for machine learning tasks. Provide the data which contains the input features and the
    according labels, the rest will be handled by the class. You can get the dataloader through an extra function which
    encapsulates logic within parameters.
    """


    def __init__(self, data, target):
        """
        Initialize the DataWrapper.
        :param data (numpy array):     Input Features for the Machine Learning Model (scientific notation: X)
        :param target (numpy array):   Labels for the Machine Learning Model (scientific notation: Y)
        """
        self.dataset = MLData(data, target)
        self.shape = self.dataset.shape


    def __len__(self):
        """
        Get the Number of Rows in the Dataset
        :return int:  number of rows
        """
        return len(self.dataset)


    def __getitem__(self, idx):
        """
        Get the Row of the Dataset at the given index. Starts Counting from 0.
        :param idx (int):   index of the row
        :return np.array:   row at the given idx
        """
        return self.dataset.__getitem__(idx)


    def get_dataloader(self, test_size_ratio=0.25, shuffle_dataset=True, train_batch_size=64, test_batch_size=32):
        """
        Get a DataLoader which can be used to iterate through the data while training/testing.
        :param test_size_ratio (int):   value between 0 and 1, determines the relative ratio of data which will be used for testing
        :param shuffle_dataset (int):   shuffle the data so that indices for train/test split will be randomized. For most cases, shuffling makes sense.
        :param train_batch_size (int):  number of rows each train batch should contain
        :param test_batch_size (int):   number of rows each test batch should contain
        :return dataloader dictionary:  dictionary which contains the dataloaders for training and testing (keys: ['train', 'test'])
        """

        indices = list(range(len(self))) # create all indices (practically enumerate each row)
        split = int(np.floor(test_size_ratio * len(self))) # find the index at which we will split the data into train/test subset
        if shuffle_dataset :
            np.random.shuffle(indices)  # shuffle the indices (e.g. [1, 2, 3, ...] -> [12, 4235, 4, ...])
        train_indices, test_indices = indices[split:], indices[:split]

        traindata = self.dataset.get_subset(train_indices) # get a subset for training
        testdata = self.dataset.get_subset(test_indices) # get a subset for testing
                
        traindataloader = DataLoader(traindata, batch_size=train_batch_size)
        testdataloader = DataLoader(testdata, batch_size=test_batch_size)
        
        dataloader = {'train': traindataloader, 'test': testdataloader}
        return dataloader


class MLData(Dataset):
    """
    This class represents the Data which is being used by the MLDataWrapper. Has initially been developed due to errors
    which occured when keeping both the dataloader logic and the dataset logic in one class. Therefore mostly only
    internal usage in the MLDataWrapper, but still can be used for several purposes.
    """


    def __init__(self, data, target, is_pytorch_tensor=True):
        """
        Initialize the Dataset
        :param data (numpy array):          Input Features for the Machine Learning Model (scientific notation: X)
        :param target (numpy array):        Labels for the Machine Learning Model (scientific notation: Y)
        :param is_pytorch_tensor (bool):    given data is in pytorch format
        """

        if not is_pytorch_tensor:
            self.data = torch.from_numpy(data)
        else:
            # data is already in correct format, therefore no more conversion needed
            self.data = data
        self.target = target
        self.shape = data.shape # e.g. 1000 rows, 15 columns: [1000, 15]


    def __len__(self):
        """
        Get the Number of Rows in the Dataset
        :return int:  number of rows
        """
        return len(self.data)


    def __getitem__(self, idx):
        """
        Get the Row of the Dataset at the given index. Starts Counting from 0.
        :param idx (int):   index of the row
        :return np.array:   row at the given idx
        """
        return self.data[idx], self.target[idx]


    def get_subset(self, indices):
        """
        get a subset of the data for a list of given indices, e.g. for train/test subsets
        :param indices (list of int): indices for the subset
        :return MLData: subset of the own data
        """
        return MLData(self.data[indices], self.target[indices])