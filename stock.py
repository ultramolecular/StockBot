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
            self.oneMinPctChg = ((self.pastPrices[qLen - 2] - price) / price) * 100
        if self.age >= 5:
            self.fiveMinPctChg = ((self.pastPrices[qLen - 6] - price) / price) * 100
        if self.age >= 10:
            self.tenMinPctChg = ((self.pastPrices[qLen - 11] - price) / price) * 100
        if self.age >= 20:
            self.twentyMinPctChg = ((self.pastPrices[qLen - 21] - price) / price) * 100
            # Make sure that once we are at the 20 price limit, to pop the first price.
            self.pastPrices.pop(0)
        
    #---------------------------------------------------------------#
    # Stringifies a stock to its ticker, price, and percent change. #
    # Returns:                                                      #
    #     (str): string that represents a stock object.             #
    #---------------------------------------------------------------#
    def __str__(self):
        qLen = len(self.pastPrices)
        s = f"{self.TICKER}\t${self.price}\tAbs Pct-Chg: {self.absPctChg:.2f}%"
        # Check for age to add appropriate interval pct chgs.
        if self.age >= 1:
            s += f"\t1m Pct-Chg: {self.oneMinPctChg}%"
        if self.age >= 5:
            s += f"\t5m Pct-Chg: {self.fiveMinPctChg}%"
        if self.age >= 10:
            s += f"\t10m Pct-Chg: {self.tenMinPctChg}%"
        if self.age >= 20:
            s += f"\t20m Pct-Chg: {self.twentyMinPctChg}%"
        return s