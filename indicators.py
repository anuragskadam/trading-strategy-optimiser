# indicators.py
import numpy as np
from candle_data import CandleData

class SMA:
    def __init__(self, candle_data: CandleData, candle_width: int, window_size: int):
        self.data = candle_data
        self.candle_width_sec = candle_width
        self.candle_width: np.timedelta64 = np.timedelta64(candle_width, 's')
        self.window_size = window_size

    def __call__(self, timestamp: np.datetime64) -> float:
        t = timestamp
        sum_of_closes = 0.0
        count = 0
        while count < self.window_size:
            close = self.data.get_close(t, self.candle_width_sec, False)
            if close is not None:
                sum_of_closes += close
                count += 1
            elif t < self.data.timestamps[0]:
                return
            t -= self.candle_width
        if count == 0:
            return 0.0;
        return sum_of_closes / count


class EMA:
    pass
