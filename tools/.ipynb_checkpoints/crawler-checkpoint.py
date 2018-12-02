# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 25/11/2018

import pandas as pd
import urllib.request
import requests
import os

class StockDataCrawler():
    
    def __init__(self, df):
        self.df = df
    
    def download_data(self, directory='../data/raw'):
        for symbol in data['Symbol']:
            csv_path = os.path.join(directory, '{}.csv'.format(symbol))
            url = "https://www.quandl.com/api/v3/datasets/WIKI/{}.csv".format(symbol)
            try:
                download = requests.get(url)
                csv_text = download.content.decode("utf-8")
                with open(csv_path,'w') as csv_f:
                    csv_f.write(download.content.decode("utf-8") ) 
            except:
                continue