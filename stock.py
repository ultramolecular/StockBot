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
    def __init__(self, ticker: str, price: float, vol: str, curr_time: datetime):
        self.TICKER = ticker
        self.price = price
        self.base_price = price
        self.OG_PRICE = price
        self.abs_pct_chg = 0.0
        self.pct_chg_after = 0.0
        self.met_crit = False
        self.TIME_ENTERED = curr_time
        self.age = 0
        self.past_prices = [price]
        self.one_min_pct_chg = 0.0
        self.five_min_pct_chg = 0.0
        self.ten_min_pct_chg = 0.0
        self.twenty_min_pct_chg = 0.0
        self.crit_time = None
        self.crit_price = None
        self.max_price = price
        self.time_max_price = None
        self.volume_at_max_price = vol

    def get_ticker(self) -> str:
        return self.TICKER

    def get_new_abs(self, price: float) -> float:
        """Calculate the new absolute percent change relative to OG_PRICE."""
        return ((price - self.OG_PRICE) / self.OG_PRICE) * 100

    def set_new_after(self, new_price: float):
        """Sets the relative % change if user criteria is already met."""
        if self.met_crit:
            self.pct_chg_after = ((new_price - self.base_price) / self.base_price) * 100
        else:
            self.pct_chg_after = 0.0

    def get_after(self) -> float:
        return self.pct_chg_after

    def get_abs(self) -> float:
        return self.abs_pct_chg

    def set_abs(self, new_abs: float):
        self.abs_pct_chg = new_abs

    def get_age(self) -> int:
        return self.age

    def has_met_crit(self) -> bool:
        return self.met_crit

    def did_meet_crit(self):
        """
        Flags that the stock has met user criteria, and records the time/price
        if not already set.
        """
        self.met_crit = True
        if self.crit_time is None:
            self.crit_time = datetime.now()
            self.crit_price = self.price
            self.max_price = self.price
            self.time_max_price = datetime.now()

    def set_price(self, new_price: float):
        self.price = new_price

    def set_base_price(self, new_price: float):
        self.base_price = new_price

    def get_max_price(self) -> float:
        return self.max_price

    def get_time_max_price(self) -> Optional[datetime]:
        return self.time_max_price

    def get_vol_at_max_price(self) -> str:
        return self.volume_at_max_price

    def get_crit_time(self) -> Optional[datetime]:
        return self.crit_time

    def get_crit_price(self) -> Optional[float]:
        return self.crit_price

    def get_peak_change(self) -> float:
        """
        Compute how much the max_price is, in percent change, relative to the
        price when stock hit criteria (crit_price).
        """
        if self.crit_price is not None and self.crit_price != 0.0:
            return ((self.max_price - self.crit_price) / self.crit_price) * 100
        return 0.0

    def get_1m_pct(self) -> float:
        return self.one_min_pct_chg

    def get_5m_pct(self) -> float:
        return self.five_min_pct_chg

    def get_10m_pct(self) -> float:
        return self.ten_min_pct_chg

    def get_20m_pct(self) -> float:
        return self.twenty_min_pct_chg

    def update_intervals(
        self, price: float, vol: str, curr_time: datetime, ref_rate_mins: float = 1.0
    ):
        """
        Update the stock's intervals based on the refresh rate (in minutes).
        E.g., if ref_rate_mins=0.5 (30s), '1m' is 2 intervals, '5m' is 10 intervals, etc.
        If ref_rate_mins=2.0, then the '1m' slot might be 0 or 1 iteration away.
        """
        self.age = (curr_time - self.TIME_ENTERED).seconds // 60
        self.past_prices.append(price)

        intervals = [1, 5, 10, 20]
        steps_for = []
        for minutes in intervals:
            steps_float = minutes / ref_rate_mins
            steps = round(steps_float)
            steps_for.append(steps if steps > 0 else 1)

        q_len = len(self.past_prices)

        def get_price_n_steps_ago(n: int) -> float:
            idx = q_len - 1 - n
            if idx < 0:
                idx = 0
            return self.past_prices[idx]

        # 1m
        steps_1 = steps_for[0]
        price_1m_ago = get_price_n_steps_ago(steps_1)
        self.one_min_pct_chg = (
            ((price - price_1m_ago) / price_1m_ago) * 100 if price_1m_ago else 0
        )

        # 5m
        steps_5 = steps_for[1]
        price_5m_ago = get_price_n_steps_ago(steps_5)
        self.five_min_pct_chg = (
            ((price - price_5m_ago) / price_5m_ago) * 100 if price_5m_ago else 0
        )

        # 10m
        steps_10 = steps_for[2]
        price_10m_ago = get_price_n_steps_ago(steps_10)
        self.ten_min_pct_chg = (
            ((price - price_10m_ago) / price_10m_ago) * 100 if price_10m_ago else 0
        )

        # 20m
        steps_20 = steps_for[3]
        price_20m_ago = get_price_n_steps_ago(steps_20)
        self.twenty_min_pct_chg = (
            ((price - price_20m_ago) / price_20m_ago) * 100 if price_20m_ago else 0
        )

        if len(self.past_prices) > 200:
            self.past_prices.pop(0)

        if self.met_crit and price > self.max_price:
            self.max_price = price
            self.time_max_price = curr_time
            self.volume_at_max_price = vol
