import numpy as np
import numpy.typing as npt
import pandas as pd
from sparse_table import SparseTable
from trade import Trade
import plotly.graph_objects as go

class CandleData:
    def __init__(self, file_name: str):
        df = pd.read_csv(file_name)

        timestamps = pd.to_datetime(df["timestamp"], utc=True)
        self.timestamps: npt.NDArray[np.datetime64] = timestamps.to_numpy(
            dtype="datetime64[ns]"
        )
        self.open: npt.NDArray[np.float64] = df["open"].to_numpy(dtype=np.float64)
        self.high: npt.NDArray[np.float64] = df["high"].to_numpy(dtype=np.float64)
        self.low: npt.NDArray[np.float64] = df["low"].to_numpy(dtype=np.float64)
        self.close: npt.NDArray[np.float64] = df["close"].to_numpy(dtype=np.float64)

        assert len(self.timestamps) >= 2, "Data too short"
        delta = self.timestamps[1] - self.timestamps[0]
        self.resolution = int(delta / np.timedelta64(1, "s"))

        self.range_min = SparseTable(self.low, np.minimum)
        self.range_max = SparseTable(self.high, np.maximum)

    def _get_range(
        self,
        timestamp: np.datetime64,
        candle_width: int,
        time_is_open_time: bool,
    ) -> tuple[int, int]:
        """
        Return [l, r), the indices of the candles covered by the
        requested time range.
        """

        assert self.resolution is not None
        assert candle_width > 0
        assert candle_width % self.resolution == 0

        width = np.timedelta64(candle_width, "s")

        if time_is_open_time:
            start_time = timestamp
            end_time = timestamp + width
        else:
            end_time = timestamp
            start_time = timestamp - width

        l = int(np.searchsorted(self.timestamps, start_time, side="left"))
        r = l + candle_width // self.resolution

        assert self.timestamps[l] < end_time, "Asked for candle when market is closed during the while duration"

        while self.timestamps[l] < start_time:
            l += 1
        while self.timestamps[r - 1] >= end_time:
            r -= 1
        return l, r

    def get_ohlc(
        self,
        timestamp: np.datetime64,
        candle_width: int,
        time_is_open_time: bool = True,
    ) -> tuple[float, float, float, float]:
        """
        Return (open, high, low, close) for the requested time range.
        """

        l, r = self._get_range(
            timestamp,
            candle_width,
            time_is_open_time,
        )

        return (
            float(self.open[l]),
            float(self.high[l:r].max()),
            float(self.low[l:r].min()),
            float(self.close[r - 1]),
        )

    def get_low(
        self,
        timestamp: np.datetime64,
        candle_width: int,
        time_is_open_time: bool = True,
    ) -> float:
        l, r = self._get_range(
            timestamp,
            candle_width,
            time_is_open_time,
        )

        return float(self.range_min[l, r - 1])

    def get_high(
        self,
        timestamp: np.datetime64,
        candle_width: int,
        time_is_open_time: bool = True,
    ) -> float:
        l, r = self._get_range(
            timestamp,
            candle_width,
            time_is_open_time,
        )

        return float(self.range_max[l, r - 1])

    def get_open(
        self,
        timestamp: np.datetime64,
        candle_width: int,
        time_is_open_time: bool = True,
    ) -> float:
        l, _ = self._get_range(
            timestamp,
            candle_width,
            time_is_open_time,
        )

        return float(self.open[l])

    def get_close(
        self,
        timestamp: np.datetime64,
        candle_width: int,
        time_is_open_time: bool = True,
    ) -> float:
        _, r = self._get_range(
            timestamp,
            candle_width,
            time_is_open_time,
        )

        return float(self.close[r - 1])
    def run_strategy(self,
            starting_amount: float,
            start_time: np.datetime64,
            end_time: np.datetime64, # exclusive
            on_tick: callable,
            indicators: dict[str, object],
            params,
        ):
        # print(f"started : {start_time}")
        current_amount = starting_amount
        l = int(np.searchsorted(self.timestamps, start_time))
        r = min(len(self.timestamps), int(np.searchsorted(self.timestamps, end_time)))
        trades: list[Trade] = []
        i = l
        while i < r:
            if trades and trades[-1].end_time is None:
                op, high, low, cl = self.get_ohlc(self.timestamps[i - 1], self.resolution, True)
                if trades[-1].is_long_trade:
                    mx = trades[-1].target
                    mn = trades[-1].stop_loss
                else:
                    mx = trades[-1].stop_loss
                    mn = trades[-1].target
                if high >= mx or low <= mn:
                    if (high >= mx):
                        trades[-1].sell(mx, self.timestamps[i])
                    else:
                        trades[-1].sell(mn, self.timestamps[i])
                    current_amount += trades[-1].profit

            if not trades or trades[-1].end_time is not None:
                on_tick(self, current_amount, self.timestamps[i], trades, indicators, params)

            if trades and trades[-1].end_time is None:
                if trades[-1].is_long_trade:
                    mx = trades[-1].target
                    mn = trades[-1].stop_loss
                else:
                    mx = trades[-1].stop_loss
                    mn = trades[-1].target
                lo = i
                hi = r - 1
                while lo < hi:
                    mid = (lo + hi) // 2
                    if (self.range_max[i, mid] >= mx):
                        hi = mid
                    else:
                        lo = mid + 1
                jump_to = lo + 1
                lo = i
                hi = r - 1
                while lo < hi:
                    mid = (lo + hi) // 2
                    if (self.range_min[i, mid] <= mn):
                        hi = mid
                    else:
                        lo = mid + 1
                jump_to = min(jump_to, lo + 1)
                i = jump_to
            else:
                i += 1
        profit = current_amount - starting_amount
        return profit, trades
    
    def plot_candles(
        self,
        start_time: np.datetime64,
        end_time: np.datetime64,
        candle_width: int,
    ):
        assert start_time < end_time
        assert candle_width > 0
        assert candle_width % self.resolution == 0

        candles_per_bar = candle_width // self.resolution

        l = int(np.searchsorted(self.timestamps, start_time, side="left"))
        r = int(np.searchsorted(self.timestamps, end_time, side="left"))

        n = (r - l) // candles_per_bar
        r = l + n * candles_per_bar

        if n == 0:
            return

        opens = self.open[l:r].reshape(n, candles_per_bar)
        highs = self.high[l:r].reshape(n, candles_per_bar)
        lows = self.low[l:r].reshape(n, candles_per_bar)
        closes = self.close[l:r].reshape(n, candles_per_bar)

        o = opens[:, 0]
        h = highs.max(axis=1)
        low = lows.min(axis=1)
        c = closes[:, -1]

        times = self.timestamps[l:r:candles_per_bar]

        fig = go.Figure(
            go.Candlestick(
                x=times,
                open=o,
                high=h,
                low=low,
                close=c,
            )
        )

        fig.update_layout(
            title=f"{candle_width}s Candles",
            xaxis_title="Time",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
        )

        fig.show()