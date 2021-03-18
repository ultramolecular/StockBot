#------------------------------------------------------------#
# Author:             Josiah Valdez                          #
# Began Development:  March 16, 2021                         #
#                                                            #
# File for the stock class used in stockBot.py, which will   #
# keep track of each stock's individual name, current price, #
# baseline price (price it started off as @ 8:30am CDT) and  #
# percent change. This should streamline the process.        # 
#------------------------------------------------------------#

class Stock:
    #----------------------------------------------------------------------------#
    # Creates a new stock and sets ticker, current price, original price,        #
    # and percent change.                                                        #
    # Args:                                                                      #
    #     TICKER (str): is the name of the stock, or ticker.                     #
    #     price (float): price of the stock.                                     #
    #     basePrice (float): baseline price of stock to compare and get pct chg. #
    #     pctChg (float): current percent change from last t minutes price.      #
    #     metCrit (bool): tells if it hit desired pct chg already.               #
    #----------------------------------------------------------------------------#
    def __init__(self, TICKER, price, basePrice, pctChg, metCrit):
        self.TICKER = TICKER
        self.price = price
        self.basePrice = basePrice
        self.pctChg = pctChg
        self.metCrit = metCrit

    #---------------------------------------------------------------#
    # Stringifies a stock to its ticker, price, and percent change. #
    # Returns:                                                      #
    #     (str): string that represents a stock object.             #
    #---------------------------------------------------------------#
    def __str__(self):
        return f"{self.TICKER}\t${self.price}\t{self.pctChg:.2f}%"