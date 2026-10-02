# indicators.py
import numpy as np
from candle_data import CandleData

class SMA:
    def __init__(self, candle_data: CandleData, candle_width: int, window_size: int):
        self.data = candle_data
        self.candle_width = candle_width
        self.window_size = window_size

    def __call__(self, timestamp: np.datetime64) -> float:
        total_width = self.candle_width * self.window_size
        l, r = self.data._get_range(timestamp, total_width, time_is_open_time=False)
        step = self.candle_width // self.data.resolution
        # Take closes at each candle boundary
        closes = self.data.close[l + step - 1 : r : step]
        return float(np.mean(closes))


class EMA:
    pass