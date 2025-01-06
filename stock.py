#-------------------------------------------------------------------------------------------------------#
# Author:             Josiah Valdez                                                                     #
# Began Development:  March 16, 2021                                                                    #
#                                                                                                       #
# Stock class that keeps track of each individual stock's ticker,price, original price (@ 8:30 am CDT), #
# absolute pct chg, the time it entered the gainers list and its age, and a queue/list of its past      #
# prices up to the last 20 minutes.                                                                     #
#-------------------------------------------------------------------------------------------------------#

class Stock:
    def __init__(self, ticker, price, vol, currTime):
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
        self.critTime = None
        self.critPrice = None
        self.maxPrice = price
        self.timeMaxPrice = None
        self.volumeAtMaxPrice = vol

    def getTicker(self):
        return self.TICKER

    def getNewAbs(self, price):
        """Calculate the new absolute percent change relative to OG_PRICE."""
        return ((price - self.OG_PRICE) / self.OG_PRICE) * 100

    def setNewAfter(self, newPrice):
        """Sets the relative % change if user criteria is already met."""
        self.pctChgAfter = ((newPrice - self.basePrice) / self.basePrice) * 100 if self.metCrit else 0

    def getAfter(self):
        return self.pctChgAfter

    def getAbs(self):
        return self.absPctChg

    def setAbs(self, newAbs):
        self.absPctChg = newAbs

    def hasMetCrit(self):
        return self.metCrit

    def didMeetCrit(self):
        """
        Flags that the stock has met user criteria, and records the time/price
        if not already set.
        """
        self.metCrit = True
        # Only record the first time we met criteria
        if self.critTime is None:
            from datetime import datetime
            self.critTime = datetime.now()
            self.critPrice = self.price
            # Initialize max tracking to current
            self.maxPrice = self.price
            self.timeMaxPrice = datetime.now()

    def setPrice(self, newPrice):
        self.price = newPrice

    def setBasePrice(self, newPrice):
        self.basePrice = newPrice

    def setMaxPrice(self, newMaxPrice):
        self.maxPrice = newMaxPrice

    def setTimeMaxPrice(self, newTimeMaxPrice):
        self.timeMaxPrice = newTimeMaxPrice

    def setVolAtMaxPrice(self, newVolAtMax):
        self.volumeAtMaxPrice = newVolAtMax

    def getMaxPrice(self):
        return self.maxPrice

    def getTimeMaxPrice(self):
        return self.timeMaxPrice

    def getVolAtMaxPrice(self):
        return self.volumeAtMaxPrice

    def getCritTime(self):
        return self.critTime

    def getCritPrice(self):
        return self.critPrice

    def getPeakChange(self):
        """
        Compute how much the maxPrice is, in percent change, relative to the
        price when stock hit criteria (critPrice).
        """
        return ((self.maxPrice - self.critPrice) / self.critPrice) * 100

    def updateIntervals(self, price, vol, currTime):
        """
        Update the 1m, 5m, 10m, 20m intervals, age of the stock, as well as criteria
        stats once stock has met criteria. Called from the main loop in stockBot.py.
        """
        self.age = (currTime - self.TIME_ENTERED).seconds // 60
        self.pastPrices.append(price)
        qLen = len(self.pastPrices)

        # 1-minute interval
        if self.age >= 1:
            i = qLen - 2 if qLen - 2 >= 0 else 0
            self.oneMinPctChg = ((price - self.pastPrices[i]) / self.pastPrices[i]) * 100
        
        # 5-minute interval
        if self.age >= 5:
            i = qLen - 6 if qLen - 6 >= 0 else 0
            self.fiveMinPctChg = ((price - self.pastPrices[i]) / self.pastPrices[i]) * 100
        
        # 10-minute interval
        if self.age >= 10:
            i = qLen - 11 if qLen - 11 >= 0 else 0
            self.tenMinPctChg = ((price - self.pastPrices[i]) / self.pastPrices[i]) * 100
        
        # 20-minute interval
        if self.age >= 20:
            i = qLen - 21 if qLen - 21 >= 0 else 0
            self.twentyMinPctChg = ((price - self.pastPrices[i]) / self.pastPrices[i]) * 100
            # Keep queue size limited
            self.pastPrices.pop(0)

        # If we've already met criteria, see if price is a new maximum
        if self.metCrit and price > self.maxPrice:
            self.maxPrice = price
            self.timeMaxPrice = currTime 
            self.volumeAtMaxPrice = vol

    def __str__(self):
        """
        Print the stock's main line: TICKER, Price, Abs % change, and interval changes.
        We'll rely on the main script to optionally print the second line if hasMetCrit().
        """
        s = f"{self.TICKER}\t${self.price}\tAbs Pct-Chg: {self.absPctChg:.2f}%"
        if self.age >= 1:
            s += f"\t1m Pct-Chg: {self.oneMinPctChg:.2f}%"
        if self.age >= 5:
            s += f"\t5m Pct-Chg: {self.fiveMinPctChg:.2f}%"
        if self.age >= 10:
            s += f"\t10m Pct-Chg: {self.tenMinPctChg:.2f}%"
        if self.age >= 20:
            s += f"\t20m Pct-Chg: {self.twentyMinPctChg:.2f}%"
        return s
