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

    def getAge(self):
        return self.age

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

    def get1mPct(self):
        return self.oneMinPctChg

    def get5mPct(self):
        return self.fiveMinPctChg

    def get10mPct(self):
        return self.tenMinPctChg

    def get20mPct(self):
        return self.twentyMinPctChg

    def updateIntervals(self, price, vol, currTime, refRateMins=1.0):
        """
        Update the stock's intervals based on the refresh rate (in minutes).
        E.g., if refRateMins=0.5 (30s), '1m' is 2 intervals, '5m' is 10 intervals, etc.
        If refRateMins=2.0, then the '1m' slot might be 0 or 1 iteration away.
        """
        self.age = (currTime - self.TIME_ENTERED).seconds // 60
        self.pastPrices.append(price)

        intervals = [1, 5, 10, 20]
        steps_for = []
        for minutes in intervals:
            steps_float = minutes / refRateMins
            # We'll round to nearest int so we do our best guess
            steps = round(steps_float)
            steps_for.append(steps if steps > 0 else 1)
            # We ensure at least 1 step, so we don't skip an interval altogether

        # Now steps_for = [steps_1m, steps_5m, steps_10m, steps_20m]
        qLen = len(self.pastPrices)
        # Helper to get the price from 'n steps' ago
        def get_price_n_steps_ago(n):
            idx = qLen - 1 - n  # '-1' because the last is our current price
            if idx < 0:
                # we don't have enough data, fallback to first known price
                idx = 0
            return self.pastPrices[idx]

        # 1-minute interval
        steps_1 = steps_for[0]
        price_1m_ago = get_price_n_steps_ago(steps_1)
        self.oneMinPctChg = ((price - price_1m_ago) / price_1m_ago) * 100 if price_1m_ago else 0

        # 5-minute interval
        steps_5 = steps_for[1]
        price_5m_ago = get_price_n_steps_ago(steps_5)
        self.fiveMinPctChg = ((price - price_5m_ago) / price_5m_ago) * 100 if price_5m_ago else 0

        # 10-minute interval
        steps_10 = steps_for[2]
        price_10m_ago = get_price_n_steps_ago(steps_10)
        self.tenMinPctChg = ((price - price_10m_ago) / price_10m_ago) * 100 if price_10m_ago else 0

        # 20-minute interval
        steps_20 = steps_for[3]
        price_20m_ago = get_price_n_steps_ago(steps_20)
        self.twentyMinPctChg = ((price - price_20m_ago) / price_20m_ago) * 100 if price_20m_ago else 0

        # Keep queue size limited to e.g. 40 or 80 to avoid unbounded growth
        if len(self.pastPrices) > 200:
            self.pastPrices.pop(0)

        # If we've already met criteria, see if price is a new maximum
        if self.metCrit and price > self.maxPrice:
            self.maxPrice = price
            self.timeMaxPrice = currTime 
            self.volumeAtMaxPrice = vol
