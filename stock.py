#-------------------------------------------------------------------------------------------------------#
# Author:             Josiah Valdez                                                                     #
# Began Development:  March 16, 2021                                                                    #
#                                                                                                       #
# Stock class that keeps track of each individual stock's ticker,price, original price (@ 8:30 am CDT), #
# absolute pct chg, the time it entered the gainers list and its age, and a queue/list of its past      #
# prices up to the last 20 minutes.                                                                     #
#-------------------------------------------------------------------------------------------------------#
from datetime import datetime
from typing import Optional


class Stock:
    def __init__(self, ticker: str, price: float, vol: str, currTime: datetime):
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

    def getTicker(self) -> str:
        return self.TICKER

    def getNewAbs(self, price: float) -> float:
        """Calculate the new absolute percent change relative to OG_PRICE."""
        return ((price - self.OG_PRICE) / self.OG_PRICE) * 100

    def setNewAfter(self, newPrice: float):
        """Sets the relative % change if user criteria is already met."""
        if self.metCrit:
            self.pctChgAfter = ((newPrice - self.basePrice) / self.basePrice) * 100
        else:
            self.pctChgAfter = 0.0

    def getAfter(self) -> float:
        return self.pctChgAfter

    def getAbs(self) -> float:
        return self.absPctChg

    def setAbs(self, newAbs: float):
        self.absPctChg = newAbs

    def getAge(self) -> int:
        return self.age

    def hasMetCrit(self) -> bool:
        return self.metCrit

    def didMeetCrit(self):
        """
        Flags that the stock has met user criteria, and records the time/price
        if not already set.
        """
        self.metCrit = True
        if self.critTime is None:
            self.critTime = datetime.now()
            self.critPrice = self.price
            self.maxPrice = self.price
            self.timeMaxPrice = datetime.now()

    def setPrice(self, newPrice: float):
        self.price = newPrice

    def setBasePrice(self, newPrice: float):
        self.basePrice = newPrice

    def getMaxPrice(self) -> float:
        return self.maxPrice

    def getTimeMaxPrice(self) -> Optional[datetime]:
        return self.timeMaxPrice

    def getVolAtMaxPrice(self) -> str:
        return self.volumeAtMaxPrice

    def getCritTime(self) -> Optional[datetime]:
        return self.critTime

    def getCritPrice(self) -> Optional[float]:
        return self.critPrice

    def getPeakChange(self) -> float:
        """
        Compute how much the maxPrice is, in percent change, relative to the
        price when stock hit criteria (critPrice).
        """
        if self.critPrice is not None and self.critPrice != 0.0:
            return ((self.maxPrice - self.critPrice) / self.critPrice) * 100
        return 0.0

    def get1mPct(self) -> float:
        return self.oneMinPctChg

    def get5mPct(self) -> float:
        return self.fiveMinPctChg

    def get10mPct(self) -> float:
        return self.tenMinPctChg

    def get20mPct(self) -> float:
        return self.twentyMinPctChg

    def updateIntervals(
        self, price: float, vol: str, currTime: datetime, refRateMins: float = 1.0
    ):
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
            steps = round(steps_float)
            steps_for.append(steps if steps > 0 else 1)

        qLen = len(self.pastPrices)

        def get_price_n_steps_ago(n: int) -> float:
            idx = qLen - 1 - n
            if idx < 0:
                idx = 0
            return self.pastPrices[idx]

        # 1m
        steps_1 = steps_for[0]
        price_1m_ago = get_price_n_steps_ago(steps_1)
        self.oneMinPctChg = (
            ((price - price_1m_ago) / price_1m_ago) * 100 if price_1m_ago else 0
        )

        # 5m
        steps_5 = steps_for[1]
        price_5m_ago = get_price_n_steps_ago(steps_5)
        self.fiveMinPctChg = (
            ((price - price_5m_ago) / price_5m_ago) * 100 if price_5m_ago else 0
        )

        # 10m
        steps_10 = steps_for[2]
        price_10m_ago = get_price_n_steps_ago(steps_10)
        self.tenMinPctChg = (
            ((price - price_10m_ago) / price_10m_ago) * 100 if price_10m_ago else 0
        )

        # 20m
        steps_20 = steps_for[3]
        price_20m_ago = get_price_n_steps_ago(steps_20)
        self.twentyMinPctChg = (
            ((price - price_20m_ago) / price_20m_ago) * 100 if price_20m_ago else 0
        )

        if len(self.pastPrices) > 200:
            self.pastPrices.pop(0)

        if self.metCrit and price > self.maxPrice:
            self.maxPrice = price
            self.timeMaxPrice = currTime
            self.volumeAtMaxPrice = vol
