# Market

## basic structure of market data

- kline: single point ohlcv
    - CandleStick(time,o,h,l,c,v,)
- trade: single point trade
    - Trade(time,price)
- historical: multiple points ohlcv window
    - CandleStick[] / Rolling[CandleStick]

## backtest
- local: one time fetch, then generate multiple
- restful: one time fetch, then generate multiple 

## paper/live
- websocket: one time fetch, then streaming


## implementation
1. streaming trade/kline
    - no history
    - accumulate past N tick in memory on strategy side
2. rolling window
    - when backtest, read historical ohlcv dataframe, generate array 
      of windows and send
    - when live, need to do a restful fetch for rolling window first,
      then keep going for new data for on going new windows

## e.g.

1. classify by data structure
KlineTick.Binance('BTC')
TradeTick.Binance('BTC')
RollingWindows.Binance('BTC', streaming=True)

2. classify by source
Market.Local.Binance.KlineTick('BTC')
Market.Historical.Binance.KlineTick('BTC')
Market.Historical.Binance.RollingWindows('BTC', streaming=True)

3. compact class
KlineTick('BTC')
TradeTick('BTC')
RollingWindows('BTC', streaming=True)
