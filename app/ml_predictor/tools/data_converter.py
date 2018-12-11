"""
- author: Johannes Hötter (https://github.com/johannes-hoetter)
- version: 1.0
- last updated on: 05/12/2018

"""

import pandas as pd # for dataframe operations
import datetime # to convert columns in the dataframe
try:
    import _pickle as pickle # for serialization, _pickle == cPickle (faster than pickle)
except:
    import pickle # alternative
from sklearn.preprocessing import StandardScaler # for ml format
from collections import OrderedDict
import numpy as np

class DataConverter():
    
    
    def __init__(self):
        self.scalers = {}
    
    
    def convert_df(self, df):
        # replace whitespaces in columns with underscores
        df.columns = [col.replace(' ', '_') for col in df.columns]
        
        # convert datestring to dates 
        df['Date'] = df['Date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
        df['Year'] = df['Date'].apply(lambda x: x.year)
        df['Month'] = df['Date'].apply(lambda x: x.month)
        df['Day'] = df['Date'].apply(lambda x: x.day)
        df.drop('Date', axis=1, inplace=True)
        return df
    
    
    def fill_targets(self, df):
        # for each date (except the last one), get the adjusted close price from the next date
        df.sort_values(by=['Year', 'Month', 'Day'], inplace=True) # dates in right order
        next_day_adj_close = df['Adj._Close'].iloc[1:] # get the prices of the next day
        next_day_adj_close.index += 1
        df['Adj._Close_next'] = next_day_adj_close
        df.reset_index(drop=True, inplace=True) # reset index so that earliest date has index 0
        df.drop(df.index.max(), inplace=True) # get rid of the last row, as we don't know the target for this one
        return df
    
    
    def convert_ml_format(self, df, symbol, target='Adj._Close_next'):
        X = df.drop(target, axis=1).values # whole df except last column (which is the target)
        y = df[target].values # only target column
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        self.scalers[symbol] = scaler
        return X, y
    
    
    def convert_x(self, x, symbol):
        '''
        Example - MUST KEEP THE KEY-ORDER!:
        x = {
            'Open': 20.6,
            'High': 21.45,
            'Low': 20.22,
            'Close': 20.6,
            'Volume': 23402800.0,
            'Ex-Dividend': 0.0,
            'Split_Ratio': 1.0,
            'Adj._Open': 15.624619538007,
            'Adj._High': 16.269324713118998,
            'Adj._Low': 15.336398400897998,
            'Adj._Close': 15.624619538007,    
            'Adj._Volume': 23402800.0,
            'Year': 2008.0,
            'Month': 4.0,
            'Day': 23.0
        }
        '''
        x = OrderedDict(x) # don't change the value of the dict!
        try:
            scaler = self.scalers[symbol]
        except:
            raise Exception('Symbol {} not contained in Trainingset, therefore not possible to convert the input.'.format(symbol))
        
        x_values = np.array(list(x.values())).reshape(1, -1)
        ml_x = scaler.transform(x_values)
        return ml_x
    
    
    def serialize(self, path='serialized_tool_objects/dataconverter.p'):
        with open(path, 'wb') as file:
            pickle.dump(self.scalers, file)
    
    
    def initialize(self, path='serialized_tool_objects/dataconverter.p'):
        with open(path, 'rb') as file:
            self.scalers = pickle.load(file)

            
    def __repr__(self):
        """
        :return (string): string representation of the Object
        """
        return 'DataConverter()'