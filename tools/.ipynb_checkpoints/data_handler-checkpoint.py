# author: Johannes Hötter (https://github.com/johannes-hoetter)
# version: 1.0
# last updated on: 02/12/2018

class DataHandler:
    
    def __init__(self, dbname='DataFrames'):
        try:
            self.engine = create_engine('sqlite:///..//data/cleaned/{}.db'.format(dbname))
        except:
            pass
    
    
    # Database
    def save_to_db(self, df, symbol, engine, index=False, if_exists='replace'):
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
    def save_to_npz(self, X, y, symbol, path=''):
        # save the arrays
        if path == '':
            path = '../data/ml_format/{}.npz'.format(symbol)
        else:
            path = os.join(path, '{}.npz'.format(symbol))
        np.savez(path, X=X, y=y)

        
    def load_from_npz(self, symbol, path=''):
        if path == '':
            path = '../data/ml_format/{}.npz'.format(symbol)
        else:
            path = os.join(path, '{}.npz'.format(symbol))
        try:
            with np.load(path) as data:
                X = data['X']
                y = data['y']
            return X, y
        except:
            raise Exception("Can't load from path {}.".path)
       
    
    def serialize(self, path='serialized_tool_objects/datahandler.p'):
        with open(path, 'wb') as file:
            pickle.dump(preparer.scalers, file)
    
    
    def initialize(self, path='serialized_tool_objects/datahandler.p'):
        with open(path, 'rb') as file:
            self.scalers = pickle.load(file)
            
            
    def __repr__(self):
        return 'DataHandler({})'.format(self.dbname)