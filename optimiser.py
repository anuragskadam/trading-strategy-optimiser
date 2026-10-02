import numpy as np
from scipy.optimize import differential_evolution
from candle_data import CandleData
from trade import Trade
import random

def optimise(
    start_month: int,  # jan is 1
    start_year: int,
    in_months: int,
    out_months: int,
    on_tick: callable,
    objective_function: callable,
    data: CandleData,
    bounds: list[tuple[object]],
    integrality: list[bool],
    indicators: dict,
    seed: int = 42,
):
    random.seed(seed)
    np.random.seed(seed)
    amount = 10000.0
    out_sample_trades: list[list[Trade]] = [] # stores trades for out data in each optimisation window
    in_sample_trades: list[list[Trade]] = [] # stores trades for out data in each optimisation window
    current_time = np.datetime64(f"{start_year:04d}-{start_month:02d}", "M")
    x0 = np.array([random.uniform(bounds[i][0], bounds[i][1]) if not integrality[i] else random.randint(bounds[i][0], bounds[i][1]) for i in range(len(integrality))])
    res = None
    while True:
        in_start = current_time
        in_end = in_start + np.timedelta64(in_months, "M")
        out_start = in_end
        out_end = out_start + np.timedelta64(out_months, "M")

        in_start = in_start.astype("datetime64[ns]")
        in_end = in_end.astype("datetime64[ns]")
        out_start = out_start.astype("datetime64[ns]")
        out_end = out_end.astype("datetime64[ns]")
        print(in_start)
        resolution_td = np.timedelta64(data.resolution, "s").astype("timedelta64[ns]")

        if data.timestamps[-1] < in_end - resolution_td:
            break
        
        def OF(params) -> float:
            _, trades_res = data.run_strategy(10000.0, in_start, in_end, on_tick, indicators, params)
            return objective_function(amount, trades_res)
        res = differential_evolution(OF, bounds, integrality=integrality, x0=x0, maxiter=5, popsize=2, polish=False, workers=1)
        # res = differential_evolution(OF, bounds, integrality=integrality, x0=x0, 
        #                              maxiter=20, # Maximum iteraitions
        #                              popsize=20, # Population Size
        #                              polish=False, # Polish
        #                              workers=4
        #                              )
        x0 = res.x
        profit, trades_res_out_sample = data.run_strategy(amount, out_start, out_end, on_tick, indicators, x0)
        _, trades_res_in_sample = data.run_strategy(amount, in_start, in_end, on_tick, indicators, x0)
        out_sample_trades.append(trades_res_out_sample)
        in_sample_trades.append(trades_res_in_sample)
        amount += profit

        current_time += np.timedelta64(out_months, "M")

    assert res is not None

    return res, out_sample_trades, in_sample_trades


def objective_function(starting_amount: float, trades: list[Trade]):
    # to be given by user
    pass


def on_tick(
    data: CandleData,
    current_amount: float,
    timestamp: np.datetime64,
    trades: list[Trade],
    indicators: dict[str, object],
    params
) -> float:
    # to be given by user
    # returns change in current_amount
    pass
