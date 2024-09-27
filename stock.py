#-------------------------------------------------------------------------------------------------------#
# Author:             Josiah Valdez                                                                     #
# Began Development:  March 16, 2021                                                                    #
#                                                                                                       #
# Stock class that keeps track of each individual stock's ticker,price, original price (@ 8:30 am CDT), #
# absolute pct chg, the time it entered the gainers list and its age, and a queue/list of its past      #
# prices up to the last 20 minutes.                                                                     #
#-------------------------------------------------------------------------------------------------------#

class Stock:
    #-----------------------------------------------------------------------------#
    # Creates a new stock and sets ticker, current price, original price,         #
    # and percent change.                                                         #
    # Args:                                                                       #
    #     ticker (str): is the name of the stock, or ticker.                      #
    #     price (float): price of the stock at the given moment.                  #
    #     currTime (datetime): the time this stock was introduced to the gainers. #
    #-----------------------------------------------------------------------------#
    def __init__(self, ticker, price, currTime):
        self.TICKER = ticker
        self.price = price
        self.basePrice = price
        self.OG_PRICE = price
        self.absPctChg = 0.0
        self.pctChgAfter = 0.0
        self.metCrit = False
        self.TIME_ENTERED = currTime
        self.age = 0
        self.pastPrices = [price]
        self.oneMinPctChg = 0.0
        self.fiveMinPctChg = 0.0
        self.tenMinPctChg = 0.0
        self.twentyMinPctChg = 0.0

    #--------------------------------------#
    # Retuns the name/ticker of the stock. #
    #--------------------------------------#
    def getTicker(self):
        return self.TICKER

    #---------------------------------------------------------------#
    # Calculate the stock's new absolute pct chg give the new price #
    # (potentially) of the stock.                                   #
    # Args:                                                         #
    #     price (float): current price of the stock.                #
    # Returns:                                                      #
    #     (float): the new absolute pct chg of stock.               #
    #-------------------------------------------------------------- #
    def getNewAbs(self, price):
        return ((price - self.OG_PRICE) / self.OG_PRICE) * 100

    #--------------------------------------------------------------#
    # Sets the new relative pct chg to a new updated percentage if #
    # it has already met and passed the user criteria.             #
    # Args:                                                        #
    #     price (float): current price of the stock.               #
    #--------------------------------------------------------------#
    def setNewAfter(self, newPrice):
        self.pctChgAfter = (newPrice - self.basePrice / self.basePrice) * 100 if self.metCrit else 0

    #--------------------------------------------#
    # Returns the relative pct chg of the stock. #
    #--------------------------------------------#
    def getAfter(self):
        return self.pctChgAfter

    #-----------------------------------------------------#
    # Returns the absolute pct chg of the stock the user. #
    #-----------------------------------------------------#
    def getAbs(self):
        return self.absPctChg
    
    #---------------------------------------------------------------#
    # Sets the absolute pct chg of the stock to a given percentage. #
    # Args:                                                         #
    #     newAbs (float): the new absolute pct chg of stock.        #
    #---------------------------------------------------------------#
    def setAbs(self, newAbs):
        self.absPctChg = newAbs

    #-------------------------------------------------------------#
    # Returns whether the stock has met the criteria of the user. #
    #-------------------------------------------------------------#
    def hasMetCrit(self):
        return self.metCrit

    #--------------------------------------------------#
    # Flags that the stock has met the user criteria.  #
    #--------------------------------------------------#
    def didMeetCrit(self):
        self.metCrit = True

    #---------------------------------------------------#
    # Sets the price of the stock to a given new price. #
    # Args:                                             #
    #     newPrice (float): the new price of the stock. #
    #---------------------------------------------------#
    def setPrice(self, newPrice):
        self.price = newPrice

    #----------------------------------------------------#
    # Sets the base price of the stock to a given price. #
    # Args:                                              #
    #     newPrice (float): the new price of the stock.  #
    #----------------------------------------------------#
    def setBasePrice(self, newPrice):
        self.basePrice = newPrice

    #------------------------------------------------------------------#
    # Checks for each interval and updates their pct chgs accordingly. #
    # Args:                                                            #
    #     price (float): current price of the stock.                   #
    #     currTime (datetime): current time used to measure age.       #
    #------------------------------------------------------------------#     
    def updateIntervals(self, price, currTime):
        # Set age of stock given the current time and the time it entered.
        self.age = (currTime - self.TIME_ENTERED).seconds // 60
        # Add the current price to the queue of past prices.
        self.pastPrices.append(price)
        qLen = len(self.pastPrices)
        if self.age >= 1:
            # This is just error prevention, sometimes it doesn't actually have enough prices held.
            i = qLen - 2 if qLen - 2 >= 0 else 0
            self.oneMinPctChg = ((price - self.pastPrices[i]) / self.pastPrices[i]) * 100
        if self.age >= 5:
            i = qLen - 6 if qLen - 6 >= 0 else 0
            self.fiveMinPctChg = ((price - self.pastPrices[i]) / self.pastPrices[i]) * 100
        if self.age >= 10:
            i = qLen - 11 if qLen - 11 >= 0 else 0
            self.tenMinPctChg = ((price - self.pastPrices[i]) / self.pastPrices[i]) * 100
        if self.age >= 20:
            i = qLen - 21 if qLen - 21 >= 0 else 0
            self.twentyMinPctChg = ((price - self.pastPrices[i]) / self.pastPrices[i]) * 100
            # Make sure that once we are at the 20 price limit, to pop the first price.
            self.pastPrices.pop(0)
        
    #-----------------------------------------------------------------------#
    # Stringifies a stock to its ticker, price, absolute pct chg, along     #
    # with its respective past 1-minute, 5-minute, 10-minute, and 20-minute #
    # pct chg.                                                              #
    # Returns:                                                              #
    #     (str): string that represents a stock object.                     #
    #-----------------------------------------------------------------------#
    def __str__(self):
        s = f"{self.TICKER}\t${self.price}\tAbs Pct-Chg: {self.absPctChg:.2f}%"
        # Check for age to add appropriate interval pct chgs.
        if self.age >= 1:
            s += f"\t1m Pct-Chg: {self.oneMinPctChg:.2f}%"
        if self.age >= 5:
            s += f"\t5m Pct-Chg: {self.fiveMinPctChg:.2f}%"
        if self.age >= 10:
            s += f"\t10m Pct-Chg: {self.tenMinPctChg:.2f}%"
        if self.age >= 20:
            s += f"\t20m Pct-Chg: {self.twentyMinPctChg:.2f}%"
        return s
