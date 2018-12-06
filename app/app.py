from machine_learning.sp500 import SP500Predictor

if __name__ == '__main__':
    sp500_predictor = SP500Predictor()
    sp500_predictor.activate()

    print(sp500_predictor.predict('AAPL'))