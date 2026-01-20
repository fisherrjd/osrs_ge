def ge_margin(high_price: int, low_price: int) -> int:
    """
    Calculate the OSRS GE margin between a buy and sell offer.

    Args:
        high_price (int): The sell price (what you'd sell for).
        low_price (int): The buy price (what you'd buy for).

    Returns:
        tuple[int, int]: (tax, profit)
            tax: Coins lost to GE tax when selling
            profit: Net profit per item
    """
    # Calculate tax on the high price
    tax = min(high_price // 100, 5_000_000)

    # Net profit per item
    profit = (high_price - tax) - low_price
    return profit
