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
    #                                                                            #
    # Args:                                                                      #
    #     TICKER (str): is the name of the stock, or ticker.                     #
    #     price (float): price of the stock.                                     #
    #     OG_PRICE (float): original price of stock, i.e price of stock @ 8:30am #
    #     pctChg (float): current percent change from last t minutes price.      #
    #----------------------------------------------------------------------------#
    def __init__(self, TICKER, price, OG_PRICE, pctChg):
        self.TICKER = TICKER
        self.price = price
        self.OG_PRICE = OG_PRICE
        self.pctChg = pctChg
    
    #-----------------------------------------#
    # Gets the ticker.                        #
    # Returns:                                #
    #     TICKER (str): ticker of the stock.  #
    #-----------------------------------------#
    def getTick(self):
        return self.TICKER
        
    #------------------------------------------------#
    # Gets the current price.                        #
    # Returns:                                       #
    #     price (float): price of stock.             #
    #------------------------------------------------#
    def getPrice(self):
        return self.price
    
    #-----------------------------------------------#
    # Updates stock's price.                        #
    # Args:                                         #
    #     newPrice (float): the new price of stock. #
    #-----------------------------------------------#
    def setPrice(self, newPrice):
        self.price = newPrice

    #--------------------------------------------#
    # Gets the original price.                   #
    # Returns:                                   #
    #     OG_PRICE (float): base price of stock.  #
    #--------------------------------------------#
    def getOGPrice(self):
        return self.OG_PRICE
    
    #------------------------------------------------------#
    # Gets the current percent change.                     #
    # Returns:                                             #
    #     pctChg (float): current percent change of stock. #
    #------------------------------------------------------#
    def getPctChg(self):
        return self.pctChg
        
    #---------------------------------------------------------#
    # Updates stock's percent change.                         #
    # Args:                                                   #
    #     newPctChg (float): the new percent change of stock. #
    #---------------------------------------------------------#
    def setPctChg(self, newPctChg):
        self.pctChg = newPctChg