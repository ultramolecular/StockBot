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
    def __init__(self,
         ticker: str,
         price: float,
         vol: str,
         rvol: float,
         rsi: float,
         curr_time: datetime,
    ):
        # Entry snapshot constants
        self.TICKER = ticker
        self.OG_PRICE = price
        self.TIME_ENTERED = curr_time
        self.OG_VOL = vol
        self.OG_RVOL = rvol
        self.OG_RSI = rsi

        # Crit snapshot constants
        self.CRIT_TIME = None
        self.CRIT_PRICE = None
        self.CRIT_VOL = None
        self.CRIT_RVOL = None
        self.CRIT_RSI = None
        self.CRIT_VOL_FLOAT_RATIO: Optional[float] = None
        self.CRIT_SCORE: Optional[int] = None
        self.CRIT_TIER: Optional[str] = None

        # Rolling attributes
        self.price = price
        self.base_price = price
        self.abs_pct_chg = 0.0
        self.pct_chg_after = 0.0
        self.met_crit = False
        self.age = 0
        self.past_prices = [price]
        self.max_price = price
        self.time_max_price = None
        self.volume_at_max_price = vol
        self.rvol_at_max_price: Optional[float] = None
        self.rsi_at_max_price: Optional[float] = None
        self.float_shares: Optional[float] = None
        self.last_volume_str: str = vol
        self.last_rvol: Optional[float] = None
        self.last_rsi: Optional[float] = None
        self.last_vol_float_ratio: Optional[float] = None

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
        if self.CRIT_TIME is None:
            self.CRIT_TIME = datetime.now()
            self.CRIT_PRICE = self.price
            self.max_price = self.price
            self.time_max_price = datetime.now()

    def set_price(self, new_price: float):
        self.price = new_price

    def get_og_price(self) -> float:
        return self.OG_PRICE

    def set_base_price(self, new_price: float):
        self.base_price = new_price

    def set_float_shares(self, new_float_shares: Optional[float]):
        self.float_shares = new_float_shares

    def get_og_vol(self) -> str:
        return self.OG_VOL

    def get_og_rvol(self) -> float:
        return self.OG_RVOL

    def get_og_rsi(self) -> float:
        return self.OG_RSI

    def get_max_price(self) -> float:
        return self.max_price

    def get_time_max_price(self) -> Optional[datetime]:
        return self.time_max_price

    def get_vol_at_max_price(self) -> str:
        return self.volume_at_max_price

    def get_crit_time(self) -> Optional[datetime]:
        return self.CRIT_TIME

    def get_crit_price(self) -> Optional[float]:
        return self.CRIT_PRICE

    def get_crit_rvol(self) -> Optional[float]:
        return self.CRIT_RVOL

    def get_crit_rsi(self) -> Optional[float]:
        return self.CRIT_RSI

    def get_crit_vol_float_ratio(self) -> Optional[float]:
        return self.CRIT_VOL_FLOAT_RATIO 

    def get_float_shares(self) -> Optional[float]:
        return self.float_shares

    def get_crit_score(self) -> Optional[int]:
        return self.CRIT_SCORE
    
    def get_crit_tier(self) -> Optional[str]:
        return self.CRIT_TIER

    def get_crit_vol(self) -> Optional[str]:
        return self.CRIT_VOL

    def get_peak_rvol(self) -> Optional[float]:
        return self.rvol_at_max_price

    def get_peak_rsi(self) -> Optional[float]:
        return self.rsi_at_max_price

    def get_peak_change(self) -> float:
        """
        Compute how much the max_price is, in percent change, relative to the
        price when stock hit criteria (CRIT_PRICE).
        """
        if self.CRIT_PRICE is not None and self.CRIT_PRICE != 0.0:
            return ((self.max_price - self.CRIT_PRICE) / self.CRIT_PRICE) * 100
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
        if self.CRIT_TIME and self.time_max_price:
            delta = self.time_max_price - self.CRIT_TIME
            return int(delta.total_seconds() // 60)
        return None

    def update_technicals(
        self,
        price: float,
        vol: str,
        curr_time: datetime,
        rvol: Optional[float],
        rsi: Optional[float],
    ):
        """Updates the indicators every loop"""
        self.age = (curr_time - self.TIME_ENTERED).seconds // 60
        self.last_volume_str = vol
        self.last_rvol = rvol
        self.last_rsi = rsi

        vol_shares = Stock.parse_volume_to_shares(vol)
        if self.float_shares and self.float_shares > 0 and vol_shares:
            self.last_vol_float_ratio = vol_shares / self.float_shares
        else:
            self.last_vol_float_ratio = None

        if self.met_crit and price > self.max_price:
            self.max_price = price
            self.time_max_price = curr_time
            self.volume_at_max_price = vol
            self.rvol_at_max_price = rvol
            self.rsi_at_max_price = rsi

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
        self.CRIT_VOL = self.last_volume_str
        self.CRIT_RVOL = self.last_rvol
        self.CRIT_RSI = self.last_rsi
        self.CRIT_VOL_FLOAT_RATIO = self.last_vol_float_ratio
        self.CRIT_SCORE = score
        self.CRIT_TIER = tier
