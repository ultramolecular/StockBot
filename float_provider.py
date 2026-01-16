from dotenv import load_dotenv
import os
from pathlib import Path
import requests
from typing import Optional

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
FMP_KEY = os.getenv("FMP_KEY")


class FloatProvider:
    def __init__(self):
        self.cache: dict[str, float] = {}  # ticker -> shares

    def get_float_shares(self, ticker: str) -> Optional[float]:
        tick = ticker.upper()
        if tick in self.cache:
            return self.cache[tick]
        if not FMP_KEY:
            return None

        url = (
            "https://financialmodelingprep.com/stable/shares-float"
            f"?symbol={tick}&apikey={FMP_KEY}"
        )
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()
            if not data:
                return None
            float_shares = data[0].get("floatShares")
            if float_shares:
                self.cache[tick] = float_shares
            return float_shares
        except Exception as e:
            print(f"\n\033[1;33m[WARNING]\033[0m Failed to fetch float for {tick}: {e}")
            return None
