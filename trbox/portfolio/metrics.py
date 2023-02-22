from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from btbox.share import RISK_FREE_RATE
from pandas import DataFrame, DatetimeIndex, Series, Timedelta, to_datetime

if TYPE_CHECKING:
    from trbox.portfolio import Portfolio


def detect_annualize_factor(ts: Series | DataFrame,
                            sample_size: int = 100) -> float:

    def cal_annualize_factor(ts: Series | DataFrame) -> float:
        timeline = ts.index
        time_diff = (timeline[-1] - timeline[0])
        year_diff = time_diff.total_seconds() / 60 / 60 / 24 / 365.25
        n_timeline = len(timeline) - 1
        annualize_factor = n_timeline / year_diff
        return float(annualize_factor)

    N = len(ts)
    len_trunk = min(N, sample_size)
    trunks = [trunk
              for i in range(-1, -N - 1, -len_trunk)
              if len(trunk := ts.iloc[i - len_trunk: i]) >= len_trunk * 0.9]
    stats = [cal_annualize_factor(trunk)
             for trunk in trunks]
    median = np.median(stats)
    assert isinstance(median, float)
    return median


def total_return(ts: Series) -> float:
    ans = ts.iloc[-1] / ts.iloc[0] - 1
    return float(ans)


def cagr(ts: Series) -> float:
    ydiff = (ts.index[-1] - ts.index[0]) / pd.Timedelta(days=365)
    ans = (ts.iloc[-1] / ts.iloc[0]) ** (1 / ydiff) - 1
    return float(ans)


def mu_sigma(ts: Series,
             annualize_factor: float) -> tuple[float, float]:
    chgs = ts.pct_change()
    mean = chgs.mean()
    std = chgs.std()
    assert isinstance(mean, float)
    assert isinstance(std, float)
    mu = mean * annualize_factor
    sigma = std * annualize_factor**0.5
    return mu, sigma


@dataclass
class DrawdownPoints:
    start: datetime
    end: datetime
    high: float
    low: float


@dataclass
class DrawdownResult:
    maxdrawdown: float
    points: DrawdownPoints
    bars: int
    duration: Timedelta


def drawdown(ts: Series) -> DrawdownResult:
    assert isinstance(ts, Series)
    assert isinstance(ts.index, DatetimeIndex)
    log_ts = Series(np.log(ts))
    run_max = Series(np.maximum.accumulate(log_ts))
    end = to_datetime((run_max - log_ts).idxmax())
    start = to_datetime((log_ts.loc[:end]).idxmax())
    log_low = log_ts.at[end]
    log_high = log_ts.at[start]
    norm_low = np.exp(log_low)
    norm_high = np.exp(log_high)
    maxdrawdown = norm_low / norm_high - 1
    bars = len(log_ts.loc[start:end])
    duration = end - start

    return DrawdownResult(
        maxdrawdown=maxdrawdown,
        points=DrawdownPoints(
            start=start,
            end=end,
            low=norm_low,
            high=norm_high),
        bars=bars,
        duration=duration)


def sharpe(ts: Series,
           annualize_factor: float,
           riskfree: float) -> float:
    mu, sigma = mu_sigma(ts, annualize_factor)
    sharpe = (mu - riskfree) / sigma
    return sharpe


def calmar(ts: Series,
           annualize_factor: float,
           riskfree: float) -> float:
    mu, _ = mu_sigma(ts, annualize_factor)
    mdd = abs(drawdown(ts).maxdrawdown)
    calmar = (mu - riskfree) / mdd
    return calmar


class Metrics:
    def __init__(self,
                 portfolio: Portfolio) -> None:
        self._portfolio = portfolio
        self._annualize_factor = detect_annualize_factor(
            self._portfolio.dashboard.navs)

    @cached_property
    def total_return(self) -> float:
        return total_return(self._portfolio.dashboard.navs)

    @cached_property
    def cagr(self) -> float:
        return cagr(self._portfolio.dashboard.navs)

    @cached_property
    def mu_sigma(self) -> tuple[float, float]:
        return mu_sigma(self._portfolio.dashboard.navs, self._annualize_factor)

    @cached_property
    def sharpe(self) -> float:
        return sharpe(self._portfolio.dashboard.navs, self._annualize_factor, RISK_FREE_RATE)

    @cached_property
    def drawdown(self) -> DrawdownResult:
        return drawdown(self._portfolio.dashboard.navs)

    @cached_property
    def calmar(self) -> float:
        return calmar(self._portfolio.dashboard.navs, self._annualize_factor, RISK_FREE_RATE)

    @property
    def df(self) -> DataFrame:
        return DataFrame(dict(
            total_return=self.total_return,
            cagr=self.cagr,
            mu=self.mu_sigma[0],
            sigma=self.mu_sigma[1],
            sharpe=self.sharpe,
            mdd_pct=self.drawdown.maxdrawdown,
            mdd_bars=self.drawdown.bars,
            mdd_days=self.drawdown.duration.days,
            calmar=self.calmar
        ), index=[self._portfolio.strategy.name, ])
