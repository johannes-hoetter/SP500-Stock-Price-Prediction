"""
- author: Johannes Hötter (https://github.com/johannes-hoetter)
- version: 1.0
- last updated on: 25/11/2018

Downloads Data from the Quandl Finance Data API for Companies from the SP500 Index.
"""

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
    """
    WebCrawler for Stock Data (-> Quandl API, csv data)
    """

    api_key = "yHcPTM9a_8P-fsnpdovx"
    def __init__(self, df):
        """
        Initialize the WebCrawler
        :param df (pandas dataframe): DataFrame which contains a column where all the stock names are listed
        """

        self.df = df
        self.dl_dir = None
        
        
    def download_data(self, directory='../data/raw'):
        """
        Download the data from the Quandl API into a directory. Each one gets saved as a .csv file.
        :param directory (string): path to the download directory
        """

        self.dl_dir = directory
        print("Downloading Data from Quandl API...")
        for symbol in tqdm(self.df['Symbol']):
            csv_path = os.path.join(self.dl_dir, '{}.csv'.format(symbol))
            # use the above api key
            url = "https://www.quandl.com/api/v3/datasets/WIKI/{}.csv?api_key={}".format(symbol, StockDataCrawler.api_key)
            try:
                # try to download the data as a csv file
                download = requests.get(url)
                with open(csv_path,'w') as csv_f:
                    csv_f.write(download.content.decode("utf-8") ) 
            except:
                continue
                
    
    def serialize(self, path='serialized_tool_objects/stockdatacrawler.p'):
        """
        Save the Crawler to a pickle file
        :param path (string): path to the location where the crawler gets serialized to
        """
        with open(path, 'wb') as file:
            pickle.dump(self.df, file)
    
    
    def initialize(self, path='serialized_tool_objects/stockdatacrawler.p'):
        """
        Load the crawlers attributes
        :param path (string): path where the crawler has been serialized to
        :return:
        """
        with open(path, 'rb') as file:
            self.df = pickle.load(file)
    
    def __repr__(self):
        """
        Caution: dataframe which contains the stock symbol names which is used for instantiation needs to be called data.
        :return (string): string representation of the Object
        """
        return 'StockDataCrawler(data)'