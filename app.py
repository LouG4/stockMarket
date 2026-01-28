from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TradeResult:
    action: str                    # "BUY", "SELL", "HOLD", "STOP"
    message: str
    shares_traded: float = 0.0
    cash_balance: float = 0.0
    shares_held: float = 0.0


def average(nums: List[float]) -> float:
    if not nums:
        raise ValueError("Cannot average an empty list.")
    return sum(nums) / len(nums)


def run_strategy(
    prices: List[float],
    volumes: List[float],
    cash_balance: float,
    shares_held: float,
) -> TradeResult:
