# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 02/12/2018

import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
try:
    import _pickle as pickle # for serialization, _pickle == cPickle (faster than pickle)
except:
    import pickle # alternative
    
class DataHandler:
    
    def __init__(self, dbname='DataFrames'):
        try:
            self.dbname = dbname
            self.engine = create_engine('sqlite:///..//data/cleaned/{}.db'.format(self.dbname))
            self.symbols = []
        except:
            pass
    
    
    # Database
    def save_to_db(self, df, symbol, index=False, if_exists='replace'):
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            
        try:
            # save the dataframe as a table in the DataFrames.db
            df.to_sql(symbol, self.engine, index=index, if_exists=if_exists)
        except:
            raise Exception("No Connection to Database available.")


    def load_from_db(self, symbol):
        try:
            return pd.read_sql_table(symbol, con=self.engine)
        except:
            raise Exception("No Connection to Database available.")
    
    
    # Machine Learning Format
    def save_to_npz(self, X, y, symbol, save_dir=''):
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            
        # save the arrays
        if save_dir == '':
            path = '../data/ml_format/{}.npz'.format(symbol)
        else:
            path = save_dir + '/{}.npz'.format(symbol)
        np.savez(path, X=X, y=y)

        
    def load_from_npz(self, symbol, path='', max=None):
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
       
    
    def serialize(self, path='serialized_tool_objects/datahandler.p'):
        with open(path, 'wb') as file:
            pickle.dump([self.dbname, self.symbols], file)
    
    
    def initialize(self, path='serialized_tool_objects/datahandler.p'):
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
        if self.symbols is None:
            symbols = []
            for file in os.listdir(data_dir):
                if file.endswith(".csv"):
                    print(file)
        else:
            return self.symbols

            
    def __repr__(self):
        return "DataHandler('{}')".format(self.dbname)