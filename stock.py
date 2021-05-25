#------------------------------------------------------------#
# Author:             Josiah Valdez                          #
# Began Development:  March 16, 2021                         #
#                                                            #
# File for the stock class used in stockBot.py, which will   #
# keep track of each stock's individual name, current price, #
# baseline price (price it started off as @ 8:30am CDT) and  #
# percent change. This should streamline the process.        # 
#------------------------------------------------------------#
from datetime import datetime as dt

class Stock:
    #----------------------------------------------------------------------------#
    # Creates a new stock and sets ticker, current price, original price,        #
    # and percent change.                                                        #
    # Args:                                                                      #
    #     TICKER (str): is the name of the stock, or ticker.                     #
    #     price (float): price of the stock.                                     #
    #     basePrice (float): baseline price of stock to compare and get pct chg. #
    #     OG_PRICE (float): original price, will be the absolute for day (8:30). #
    #----------------------------------------------------------------------------#
    def __init__(self, TICKER, price, basePrice, OG_PRICE):
        self.TICKER = TICKER
        self.price = price
        self.basePrice = basePrice
        self.OG_PRICE = OG_PRICE
        self.absPctChg = 0.0
        self.pctChgAfter = 0.0
        self.metCrit = False
        self.timeEntered = dt.now()
        self.pastPrices = []

    #-----------------------------------------------------#
    # Returns the time the stock has been in the gainers. #
    #-----------------------------------------------------#
    def getAge(self, currTime):
        mins = (currTime - timeEntered).seconds // 60

    #---------------------------------------------------------------#
    # Stringifies a stock to its ticker, price, and percent change. #
    # Returns:                                                      #
    #     (str): string that represents a stock object.             #
    #---------------------------------------------------------------#
    def __str__(self):
        return f"{self.TICKER}\t${self.price}\t{self.absPctChg:.2f}%"