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
        self.max_price = price
        self.time_max_price = None
        self.volume_at_max_price = vol
        self.float_shares: Optional[float] = None
        self.last_volume_str: str = vol
        self.last_rvol: Optional[float] = None
        self.last_rsi: Optional[float] = None
        self.last_vol_float_ratio: Optional[float] = None
        # Snapshot at criteria 
        self.crit_time = None
        self.crit_price = None
        self.crit_rvol: Optional[float] = None
        self.crit_rsi: Optional[float] = None
        self.crit_vol_float_ratio: Optional[float] = None
        self.crit_score: Optional[int] = None
        self.crit_tier: Optional[str] = None

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

    def get_time_entered(self) -> datetime:
        return self.TIME_ENTERED

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

    def get_crit_rvol(self) -> Optional[float]:
        return self.crit_rvol

    def get_crit_rsi(self) -> Optional[float]:
        return self.crit_rsi

    def get_crit_vol_float_ratio(self) -> Optional[float]:
        return self.crit_vol_float_ratio 

    def get_float_shares(self) -> Optional[float]:
        return self.float_shares

    def get_crit_score(self) -> Optional[int]:
        return self.crit_score
    
    def get_crit_tier(self) -> Optional[str]:
        return self.crit_tier

    def get_peak_change(self) -> float:
        """
        Compute how much the max_price is, in percent change, relative to the
        price when stock hit criteria (crit_price).
        """
        if self.crit_price is not None and self.crit_price != 0.0:
            return ((self.max_price - self.crit_price) / self.crit_price) * 100
        return 0.0

    def get_peak_change_spot(self) -> float:
        """
        % change from OG_PRICE (time spotted) to max_price
        """
        if self.OG_PRICE:
            return ((self.max_price - self.OG_PRICE) / self.OG_PRICE) * 100
        return 0.0

    def get_time_peak_alert(self) -> Optional[int]:
        """
        Minutes from crit time to the time of max price
        """
        if self.crit_time and self.time_max_price:
            delta = self.time_max_price - self.crit_time
            return int(delta.total_seconds() // 60)
        return None

    def update_intervals(
        self,
        price: float,
        vol: str,
        curr_time: datetime,
        volume_str: str,
        rvol: Optional[float],
        rsi: Optional[float],
    ):
        """Updates the indicators every loop"""
        self.age = (curr_time - self.TIME_ENTERED).seconds // 60
        self.last_volume_str = volume_str
        self.last_rvol = rvol
        self.last_rsi = rsi

        vol_shares = Stock.parse_volume_to_shares(volume_str)
        if self.float_shares and self.float_shares > 0 and vol_shares:
            self.last_vol_float_ratio = vol_shares / self.float_shares
        else:
            self.last_vol_float_ratio = None

        if self.met_crit and price > self.max_price:
            self.max_price = price
            self.time_max_price = curr_time
            self.volume_at_max_price = vol
            

    @staticmethod
    def parse_volume_to_shares(vol: str) -> Optional[float]:
        """
        Convert TradingView volume strings to raw number of shares.
        """
        if not vol:
            return None
        s = vol.strip().upper().replace(",", "")
        mult = 1.0
        if s.endswith("K"):
            mult = 1_000
            s = s[:-1]
        elif s.endswith("M"):
            mult = 1_000_000
            s = s[:-1]
        try:
            return float(s) * mult
        except ValueError:
            return None

    def snapshot_crit_technicals(self, score: int, tier: str) -> None:
        """Snapshots the technicals at the time criteria is met."""
        self.crit_rvol = self.last_rvol
        self.crit_rsi = self.last_rsi
        self.crit_vol_float_ratio = self.last_vol_float_ratio
        self.crit_score = score
        self.crit_tier = tier
