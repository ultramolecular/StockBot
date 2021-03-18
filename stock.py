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
    #     OG_PRICE (float): original price, will be the absolute for day (8:30). #
    #     absPctChg (float): percent change since OG_PRICE, absolute for day.    #
    #     pctChgAfter (float): percent change if it has met desired already.     #
    #     metCrit (bool): tells if it hit desired pct chg already.               #
    #----------------------------------------------------------------------------#
    def __init__(self, TICKER, price, basePrice, OG_PRICE, absPctChg, pctChgAfter, metCrit):
        self.TICKER = TICKER
        self.price = price
        self.basePrice = basePrice
        self.OG_PRICE = OG_PRICE
        self.absPctChg = absPctChg
        self.pctChgAfter = pctChgAfter
        self.metCrit = metCrit

    #---------------------------------------------------------------#
    # Stringifies a stock to its ticker, price, and percent change. #
    # Returns:                                                      #
    #     (str): string that represents a stock object.             #
    #---------------------------------------------------------------#
    def __str__(self):
        return f"{self.TICKER}\t${self.price}\t{self.absPctChg:.2f}%"