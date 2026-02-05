from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TradeResult:
    action: str  # "BUY", "SELL", "HOLD", "STOP"
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
    *,
    breakout_lookback: int = 20,  # recent high window (previous N days)
    vol_lookback: int = 20,       # average volume window
    short_window: int = 5,        # short MA window
    long_window: int = 15,        # long MA window
    momentum_days: int = 5,       # momentum = current - price N days ago
) -> TradeResult:
    """
    Strategy (matches your pseudocode):
    - Need enough data
    - BUY ALL-IN when:
        current_price > recent_high_prev_N
        AND last_volume > 2 * avg_volume_N
        AND momentum_N > 0
        AND shares_held == 0
    - SELL ALL when:
        shares_held > 0 AND short_ma < long_ma
    - Else HOLD
    """

    # Basic validation
    if len(prices) != len(volumes):
        return TradeResult(
            action="STOP",
            message="Prices and volumes must be the same length",
            cash_balance=cash_balance,
            shares_held=shares_held,
        )
    if cash_balance < 0 or shares_held < 0:
        return TradeResult(
            action="STOP",
            message="cash_balance and shares_held must be non-negative",
            cash_balance=cash_balance,
            shares_held=shares_held,
        )

    # To compare current_price to the *previous* breakout_lookback prices,
    # we need breakout_lookback + 1 price points (because we exclude current).
    min_prices_needed = max(breakout_lookback + 1, long_window, short_window, momentum_days + 1)
    min_vols_needed = max(vol_lookback, 1)

    if len(prices) < min_prices_needed or len(volumes) < min_vols_needed:
        return TradeResult(
            action="STOP",
            message=f"Not enough data (need at least {min_prices_needed} prices and {min_vols_needed} volumes)",
            cash_balance=cash_balance,
            shares_held=shares_held,
        )

    current_price = prices[-1]
    last_volume = volumes[-1]

    # Indicators
    avg_volume_n = average(volumes[-vol_lookback:])
    recent_high_prev_n = max(prices[-(breakout_lookback + 1):-1])  # excludes current price

    short_ma = average(prices[-short_window:])
    long_ma = average(prices[-long_window:])

    momentum_n = current_price - prices[-(momentum_days + 1)]

    # BUY condition (ALL-IN)
    if (
        shares_held == 0
        and current_price > recent_high_prev_n
        and last_volume > 2 * avg_volume_n
        and momentum_n > 0
    ):
        if current_price <= 0:
            return TradeResult(
                action="STOP",
                message="Invalid current price (must be > 0) for buying",
                cash_balance=cash_balance,
                shares_held=shares_held,
            )

        shares_to_buy = cash_balance / current_price
        cash_balance = 0.0
        shares_held = shares_to_buy

        return TradeResult(
            action="BUY",
            message="ALL-IN BUY on breakout",
            shares_traded=shares_to_buy,
            cash_balance=cash_balance,
            shares_held=shares_held,
        )

    # SELL condition (ALL-OUT)
    if shares_held > 0 and short_ma < long_ma:
        shares_sold = shares_held
        cash_balance = shares_held * current_price
        shares_held = 0.0

        return TradeResult(
            action="SELL",
            message="SELL due to trend reversal",
            shares_traded=shares_sold,
            cash_balance=cash_balance,
            shares_held=shares_held,
        )

    # HOLD
    return TradeResult(
        action="HOLD",
        message="Holding position",
        cash_balance=cash_balance,
        shares_held=shares_held,
    )


def main() -> None:
    # Example data (you should replace with real historical data)
    prices = [
        100, 101, 99, 102, 103, 104, 103, 105, 106, 107,
        108, 109, 110, 111, 110, 112, 113, 114, 115, 116, 118
    ]
    volumes = [
        1000, 1100, 900, 1200, 1300, 1250, 1400, 1500, 1600, 1550,
        1700, 1800, 1750, 1900, 1850, 2000, 2100, 2200, 2300, 2400, 6000
    ]

    cash_balance = 1000.0
    shares_held = 0.0

    result = run_strategy(prices, volumes, cash_balance, shares_held)

    print(f"Action: {result.action}")
    print(f"Message: {result.message}")
    print(f"Shares traded: {result.shares_traded:.6f}")
    print(f"Cash balance: {result.cash_balance:.2f}")
    print(f"Shares held: {result.shares_held:.6f}")


if __name__ == "__main__":
    main()
