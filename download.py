from datetime import datetime
import dukascopy_python as duka

from dukascopy_python.instruments import (
    INSTRUMENT_FX_METALS_XAU_USD
)

start = datetime(2010, 1, 1)
end = datetime.now()

df = duka.fetch(
    instrument=INSTRUMENT_FX_METALS_XAU_USD,
    interval=duka.INTERVAL_HOUR_4,
    offer_side=duka.OFFER_SIDE_BID,
    start=start,
    end=end,
)

df.to_csv(f"XAUUSD_M5_4H_{start}.csv")

print(df.head())
print(f"Downloaded {len(df)} candles")