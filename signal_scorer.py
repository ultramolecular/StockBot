from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SignalFeatures:
    ticker: str
    price: float
    abs_pct: float
    volume: float
    float_shares: Optional[float]
    rvol: Optional[float]
    rsi: Optional[float]
    vol_float_ratio: Optional[float]
    time: datetime


@dataclass
class SignalScore:
    score: int
    tier: str


class SignalScorer:
    @staticmethod
    def score(f: SignalFeatures) -> SignalScore:
        score = 0

        # Float - smaller is better
        if f.float_shares:
            m = f.float_shares / 1_000_000
            if m < 1:
                score += 4
            elif m < 3:
                score += 3
            elif m < 10:
                score += 2
            elif m < 20:
                score += 1

        # Relative Volume - higher is better
        if f.rvol:
            if f.rvol >= 10:
                score += 3
            elif f.rvol >= 5:
                score += 2
            elif f.rvol >= 3:
                score += 1

        # Volume/Float Rotation - higher is better
        if f.vol_float_ratio:
            if f.vol_float_ratio >= 2:
                score += 3
            elif f.vol_float_ratio >= 1:
                score += 2
            elif f.vol_float_ratio >= 0.5:
                score += 1
        
        # RSI - ranges
        if f.rsi:
            # Early momentum
            if 35 <= f.rsi < 60:
                score += 2
            # Confirmed momentum
            elif 60 <= f.rsi < 75:
                score += 3
            # Hot but not overbought
            elif 75 <= f.rsi < 85:
                score += 1
            # Overbought - penalize
            elif f.rsi >= 90:
                score -= 2
        
        # Raw % move (bump)
        if f.abs_pct >= 20:
            score += 1
        if f.abs_pct >= 30:
            score += 1

        # Map to tiers
        if score >= 11:
            tier = "A"
        elif score >= 8:
            tier = "B"
        elif score >= 5:
            tier = "C"
        else:
            tier = "D"
        
        return SignalScore(score, tier)
