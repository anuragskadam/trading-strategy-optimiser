from trade import Trade
from matplotlib import pyplot as plt

def plot_equity(trades: list[Trade]):
    trades = [trade for trade in trades if trade.end_time is not None]

    if not trades:
        return

    trades.sort(key=lambda trade: trade.end_time)

    times = [trades[0].start_time]
    equity = [0.0]

    current_equity = 0.0

    for trade in trades:
        assert trade.profit is not None

        current_equity += trade.profit
        times.append(trade.end_time)
        equity.append(current_equity)

    plt.figure(figsize=(10, 5))
    plt.step(times, equity, where="post")
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.title("Equity Curve")
    plt.grid(True)
    plt.tight_layout()
    plt.show()