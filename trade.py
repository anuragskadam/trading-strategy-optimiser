import numpy as np

class Trade:
    def __init__(
        self,
        start_time: np.datetime64,
        amount: float,
        buy_price: float,
        stop_loss: float,
        target: float,
    ):
        assert (stop_loss < buy_price < target) or (target < buy_price < stop_loss)
        self.amount = amount
        self.is_long_trade = stop_loss < target
        self.start_time = start_time
        self.end_time = None
        self.buy_price = buy_price
        self.stop_loss = stop_loss
        self.target = target
        self.profit = None

    def sell(self, price: float, sell_time: np.datetime64):
        assert self.end_time is None, "Trade has already been sold."
        self.end_time = sell_time
        self.profit = (
            (price - self.buy_price) * self.amount * (1 if self.is_long_trade else -1)
        )