"""
- author: Johannes Hötter (https://github.com/johannes-hoetter)
- version: 1.0
- last updated on: 02/12/2018

The DataHandler is used to save and store data in several formats. This is the somewhat the "single point of access" for data
"""


import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
try:
    import _pickle as pickle # for serialization, _pickle == cPickle (faster than pickle)
except:
    import pickle # alternative
    
class DataHandler:
    """
    Handles Data Requests like Save and Load in several formats
    """
    
    def __init__(self, dbname='DataFrames'):
        """
        Initialize the DataHandler
        :param dbname (string): name of the Database which gets used
        """

        try:
            self.dbname = dbname
            self.engine = create_engine('sqlite:///..//data/cleaned/{}.db'.format(self.dbname))
            self.symbols = []
        except:
            pass
    
    
    # Database
    def save_to_db(self, df, symbol, index=False, if_exists='replace'):
        """
        save a DataFrame for a given stock symbol to the database
        :param df (pandas dataframe):   holds the values (datasource)
        :param symbol (string):         name of the stock symbol, e.g. "AMZN" for Amazon
        :param index (bool):            write DataFrame index as a column
        :param if_exists (bool):        how to behave if the table already exists:
                                        - fail: Raise a ValueError
                                        - replace: Drop the table before inserting new values
                                        - append: Insert new values to the existing table
        """

        if symbol not in self.symbols:
            self.symbols.append(symbol)
            
        try:
            # save the dataframe as a table in the DataFrames.db
            df.to_sql(symbol, self.engine, index=index, if_exists=if_exists)
        except:
            raise Exception("No Connection to Database available.")


    def load_from_db(self, symbol):
        """
        load a DataFrame from the Database for a stock symbol
        :param symbol (string): name of the stock symbol, e.g. "AMZN" for Amazon
        :return pandas dataframe: contains the finance data for the given stock
        """

        try:
            return pd.read_sql_table(symbol, con=self.engine)
        except:
            raise Exception("No Connection to Database available.")

    
    # Machine Learning Format
    def save_to_npz(self, X, y, symbol, save_dir=''):
        """
        save the numpy-array versions of X and y to a .npz file
        :param X (numpy array):     Input Features for a Machine Learning model
        :param y (numpy array):     Labels for a Machine Learning model
        :param symbol (string):     name of the stock symbol, e.g. "AMZN" for Amazon
        :param save_dir (string):   path to the directory where the files get saved to
        """

        if symbol not in self.symbols:
            self.symbols.append(symbol)
            
        # save the arrays
        if save_dir == '':
            path = '../data/ml_format/{}.npz'.format(symbol)
        else:
            path = save_dir + '/{}.npz'.format(symbol)
        np.savez(path, X=X, y=y)

        
    def load_from_npz(self, symbol, path='', max=None):
        """
        load X and y from a .npz file
        :param symbol (string):     name of the stock symbol, e.g. "AMZN" for Amazon
        :param path (string):       name of the path where the .npz file is
        :param max (int):           number of rows the arrays at most contain
        :return numpy array, numpy array: X, y
        """

        if path == '':
            path = '../data/ml_format/{}.npz'.format(symbol)
        else:
            path = os.path.join(path, '{}.npz'.format(symbol))
        try:
            with np.load(path) as data:
                X = data['X']
                y = data['y']
            if max:
                return X[-max:], y[-max:]
            return X, y
        except:
            raise Exception("Can't load from path {}.".format(path))


    def load_from_csv(self, symbol, path=''):
        """
        load data from a .csv file
        :param symbol (string):     name of the stock symbol, e.g. "AMZN" for Amazon
        :param path (string):       name of the path where the .csv file is
        :return pandas dataframe: contains the values of the .csv file
        """
        if path == '':
            path = '../data/raw/{}.csv'.format(symbol)
        else:
            path = os.path.join(path, '{}.csv'.format(symbol))
        return pd.read_csv(path)


    def serialize(self, path='serialized_tool_objects/datahandler.p'):
        """
        Store the DataHandler to a given path as a pickle file
        :param path (string): path where the DataHandler gets stored at
        """
        with open(path, 'wb') as file:
            pickle.dump([self.dbname, self.symbols], file)
    
    
    def initialize(self, path='serialized_tool_objects/datahandler.p'):
        """
        load the DataHandler's attributes
        :param path (string): path where the DataHandler pickle file exists.
        """
        engine_path = None
        if '\\' in path:
            engine_path = os.path.join('\\'.join(path.split('\\')[:-3]), 'data', 'cleaned', '{}.db'.format(self.dbname))
        with open(path, 'rb') as file:
            self.dbname, self.symbols = pickle.load(file)
            if engine_path:
                self.engine = create_engine('sqlite:///{}'.format(engine_path))
            else:
                self.engine = create_engine('sqlite:///..//data/cleaned/{}.db'.format(self.dbname))
   
    def get_symbols(self, data_dir='../data/raw'):
        """
        get the symbols which are available for stock price prediction
        :param data_dir (string): path to the directory where all stock price .csv files exist.
        :return list of strings: contains all stock symbols
        """
        if self.symbols is None:
            symbols = []
            for file in os.listdir(data_dir):
                if file.endswith(".csv"):
                    print(file)
        else:
            return self.symbols

            
    def __repr__(self):
        """
        :return (string): string representation of the Object
        """
        return "DataHandler('{}')".format(self.dbname)