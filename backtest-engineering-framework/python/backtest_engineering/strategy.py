from __future__ import annotations

import numpy as np
import pandas as pd


def build_signals(prices: pd.DataFrame, short_window: int, long_window: int, volatility_lookback: int, target_gross_leverage: float) -> pd.DataFrame:
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window")

    df = prices.copy()
    df["ret"] = df.groupby("ticker")["close"].pct_change().fillna(0.0)
    df["ma_short"] = df.groupby("ticker")["close"].transform(lambda s: s.rolling(short_window).mean())
    df["ma_long"] = df.groupby("ticker")["close"].transform(lambda s: s.rolling(long_window).mean())
    df["vol"] = df.groupby("ticker")["ret"].transform(lambda s: s.rolling(volatility_lookback).std()).replace(0.0, np.nan)
    raw_signal = np.sign(df["ma_short"] - df["ma_long"]).fillna(0.0)
    inverse_vol = (1.0 / df["vol"]).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    df["score"] = raw_signal * inverse_vol
    gross_by_day = df.groupby("date")["score"].transform(lambda s: s.abs().sum()).replace(0.0, np.nan)
    df["weight"] = (df["score"] / gross_by_day).fillna(0.0) * target_gross_leverage
    return df[["date", "ticker", "close", "ret", "weight"]]
