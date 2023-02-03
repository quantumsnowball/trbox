from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Barrier, Event
from time import sleep


@dataclass
class Signal:
    start: Event
    bar: Barrier
    stop: Event


def backtest_party(name: str,
                   signal: Signal,
                   *,
                   delay: float = 0):
    def worker():
        signal.start.wait()
        for i in range(5):
            sleep(delay)
            signal.bar.wait()
            print(f'{name}: {i}')

            if signal.stop.is_set():
                break
    return worker


def live_party(signal):
    def worker():
        signal.start.wait()
        for _ in range(5):
            print(f'live: I do not care your barrier signal, I will just output randomly!')
            if signal.stop.is_set():
                break
    return worker


def main():
    signal = Signal(
        start=Event(),
        bar=Barrier(3),
        stop=Event(),
    )
    parties = [
        backtest_party('market', signal, delay=1),
        backtest_party('broker', signal),
        backtest_party('strategy', signal),
        live_party(signal),
    ]
    try:
        with ThreadPoolExecutor() as exe:
            for p in parties:
                exe.submit(p)

            print('ready!')
            sleep(2)
            print('set!')
            sleep(2)
            print('go!')
            signal.start.set()

            # blocked here until finish
    except KeyboardInterrupt:
        print('Hihi: keyboard interrupt')
        signal.stop.set()


if __name__ == '__main__':
    main()
