from trbox.event import SystemEvent


class Start(SystemEvent):
    pass


class Exit(SystemEvent):
    pass


class TimeLapse(SystemEvent):
    '''
    Ideally, an event-driven Strategy should not act too much differently
    between backtesting and live trading. However, in live trading
    the data stream usually comes with irregular time interval, in contrast,
    in backtesting the market simulator shoot out event with zero delay.
    As a result, it is hard to simulate the sequence of event simular to
    live trading. For example, in backtesting the Market simulator may send
    MarketData event too fast, such that the Strategy may make a trade `days`
    after normally when it should be, therefore failed to simulate reality.

    I propose to add a TimeLapse event that the Market is listening to only
    in backtesting mode. When strategy decided it has done its research and
    trading actions on the last received data, it can send out the TimeLapse
    event to ask the Market simulator to skip the remaining idle time. When
    in live trading, runner will simple discard this event, and Strategy will
    behave exactly like in backtest mode. By listening to the TimeLapse
    event, Market simulator can ensure the timing of the next MarketData
    will not front run the Order event from Broker.

    In short, during backtest, Strategy can tell runner to skip the remaining
    time, and start simulation again on the next data point. It is simular to
    live trading with paper money but you have the ability to fast forward
    time.
    '''
    # TODO it is time to implement TimeLapse
