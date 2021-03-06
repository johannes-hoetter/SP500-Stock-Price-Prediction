# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 25/11/2018

try:
    import _pickle as pickle # for serialization, _pickle == cPickle (faster than pickle)
except:
    import pickle # alternative
import pandas as pd
import urllib.request
import requests
import os
from tqdm import tqdm

class StockDataCrawler():

    api_key = "5FUsN6kFzSxGtpx_unsq"
    def __init__(self, df):
        self.df = df
        self.dl_dir = None
        
        
    def download_data(self, directory='../data/raw'):
        self.dl_dir = directory
        print("Downloading Data from Quandl API...")
        for symbol in tqdm(self.df['Symbol']):
            csv_path = os.path.join(self.dl_dir, '{}.csv'.format(symbol))
            url = "https://www.quandl.com/api/v3/datasets/WIKI/{}.csv?api_key={}".format(symbol, StockDataCrawler.api_key)
            try:
                download = requests.get(url)
                csv_text = download.content.decode("utf-8")
                with open(csv_path,'w') as csv_f:
                    csv_f.write(download.content.decode("utf-8") ) 
            except:
                continue
                
    
    def serialize(self, path='serialized_tool_objects/stockdatacrawler.p'):
        with open(path, 'wb') as file:
            pickle.dump(self.df, file)
    
    
    def initialize(self, path='serialized_tool_objects/stockdatacrawler.p'):
        with open(path, 'rb') as file:
            self.df = pickle.load(file)
    
    def __repr__(self):
        return 'StockDataCrawler(data)'