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
            self.oneMinPctChg = ((price - self.pastPrices[qLen - 2]) / self.pastPrices[qLen - 2]) * 100
        if self.age >= 5:
            self.fiveMinPctChg = ((price - self.pastPrices[qLen - 6]) / self.pastPrices[qLen - 6]) * 100
        if self.age >= 10:
            self.tenMinPctChg = ((price - self.pastPrices[qLen - 11]) / self.pastPrices[qLen - 11]) * 100
        if self.age >= 20:
            self.twentyMinPctChg = ((price - self.pastPrices[qLen - 21]) / self.pastPrices[qLen - 21]) * 100
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
            s += f"\t1m Pct-Chg: {self.oneMinPctChg:.2f}%"
        if self.age >= 5:
            s += f"\t5m Pct-Chg: {self.fiveMinPctChg:.2f}%"
        if self.age >= 10:
            s += f"\t10m Pct-Chg: {self.tenMinPctChg:.2f}%"
        if self.age >= 20:
            s += f"\t20m Pct-Chg: {self.twentyMinPctChg:.2f}%"
        s += f"\tPast Prices: {self.pastPrices}"
        return s