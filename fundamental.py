import helper
import time

# === MEMORY ===

last_traded_news_id = None

eia_active_trade = {
    "entry_tick": None,
    "side": None,
    "quantity": 0
}

other_active_trade = {
    "entry_tick": None,
    "side": None,
    "quantity": 0
}

POSITION_LIMIT = 100
HOLD_TICKS = 20  # Number of ticks to hold after entry


# === FUNCTIONS ===

def EIA_trade(session):
    """
    Trading model based on EIA news report.
    """
    global last_traded_news_id, eia_active_trade

    news_items = helper.get_latest_news(session)

    if not news_items:
        print("No news available.")
        return

    latest_news = news_items[0]
    news_id = latest_news.get('news_id')
    headline = latest_news.get('headline', '').upper()

    if news_id == last_traded_news_id:
        print("Already processed this news. Skipping.")
        return

    if "ACTUAL" not in headline or "FORECAST" not in headline:
        print("Latest news is not EIA report. Skipping.")
        return

    difference = -1 * helper.fundamental_EIA_report(session)

    if difference is None:
        print("Failed to parse EIA report. Skipping.")
        return

    # Calculate expected price move
    expected_price_move = difference * 0.10  # dollars

    print(f"EIA report difference: {difference:.2f} million barrels")
    print(f"Expected price move in CL: {expected_price_move:.2f} dollars")

    # Check current position
    position_info = helper.get_positions(session)
    current_position = position_info.get('CL-2F', 0)  # Default 0 if not in positions

    TRADE_QUANTITY = 90

    if expected_price_move > 0.2:
        # Bullish → Buy
        max_allowed = POSITION_LIMIT/3 - current_position
        if max_allowed <= 0:
            print("Cannot buy more. Already at or above position limit.")
            return
        quantity = min(TRADE_QUANTITY, max_allowed)
        helper.place_order(session,'CL-2F', quantity/3, 'BUY', 'MARKET')
        helper.place_order(session,'CL-2F', quantity/3, 'BUY', 'MARKET')
        helper.place_order(session,'CL-2F', quantity/3, 'BUY', 'MARKET')
        print(f"Placed BUY order for {quantity} contracts of CL-2F.")

        eia_active_trade = {
            "entry_tick": helper.get_tick(session),
            "side": 'BUY',
            "quantity": quantity
        }

    elif expected_price_move < -0.2:
        # Bearish → Sell
        max_allowed = POSITION_LIMIT/3 + current_position  # current_position negative if short
        if max_allowed <= 0:
            print("Cannot sell more. Already at or below position limit.")
            return
        quantity = min(TRADE_QUANTITY, max_allowed)
        helper.place_order(session,'CL-2F', quantity/3, 'SELL', 'MARKET')
        helper.place_order(session,'CL-2F', quantity/3, 'SELL', 'MARKET')
        helper.place_order(session, 'CL-2F', quantity/3, 'SELL', 'MARKET')
        print(f"Placed SELL order for {quantity} contracts of CL-2F.")

        eia_active_trade = {
            "entry_tick": helper.get_tick(session),
            "side": 'SELL',
            "quantity": quantity
        }

    else:
        print("No significant price move expected. No trade executed.")

    # Mark news_id as processed
    last_traded_news_id = news_id


def other_news_trade(session):
    """
    Trading model based on other types of news.
    For now: very simple example based on keyword 'STRIKE' or 'HURRICANE'.
    """
    global other_active_trade

    news_items = helper.get_latest_news(session)

    if not news_items:
        print("No news available.")
        return

    latest_news = news_items[0]
    headline = latest_news.get('headline', '').upper()

    if 'STRIKE' in headline or 'HURRICANE' in headline:
        # Major supply disruption → bullish
        print(f"Important news detected: {headline}")

        # Check position
        position_info = helper.get_positions(session)
        current_position = position_info.get('CL-2F', 0)

        TRADE_QUANTITY = 50

        max_allowed = POSITION_LIMIT - current_position
        if max_allowed <= 0:
            print("Cannot buy more. Position limit hit.")
            return
        quantity = min(TRADE_QUANTITY, max_allowed)
        helper.place_order(session, ticker='CL-2F', quantity=quantity, action='BUY', order_type='MARKET')
        print(f"Placed BUY order for {quantity} contracts of CL-2F on other news.")

        other_active_trade = {
            "entry_tick": helper.get_tick(session),
            "side": 'BUY',
            "quantity": quantity
        }
    else:
        print("No tradable other news detected.")


def fundamental_model(session):
    """
    Main fundamental model function to call EIA and other news strategies,
    and manage closing positions.
    """
    global eia_active_trade, other_active_trade

    current_tick = helper.get_tick(session)

    # === Handle closing EIA trade ===
    if eia_active_trade["entry_tick"] is not None:
        if current_tick - eia_active_trade["entry_tick"] >= HOLD_TICKS:
            print("Closing EIA trade after 20 ticks.")

            pos_info = helper.get_positions(session)
            cl2f_pos = pos_info.get('CL-2F', 0)

            if cl2f_pos != 0:
                side = 'SELL' if cl2f_pos > 0 else 'BUY'
                helper.place_order(session,'CL-2F', eia_active_trade["quantity"]/3, action=side, order_type='MARKET')
                helper.place_order(session,'CL-2F', eia_active_trade["quantity"]/3, action=side, order_type='MARKET')
                helper.place_order(session,'CL-2F', eia_active_trade["quantity"]/3, action=side, order_type='MARKET')
                print(f"Closed EIA position: {side} {abs(cl2f_pos)} contracts of CL-2F.")

            eia_active_trade = {
                "entry_tick": None,
                "side": None,
                "quantity": 0
            }

    # === Handle closing other news trade ===
    if other_active_trade["entry_tick"] is not None:
        if current_tick - other_active_trade["entry_tick"] >= HOLD_TICKS:
            print("Closing Other News trade after 20 ticks.")

            pos_info = helper.get_positions(session)
            cl2f_pos = pos_info.get('CL-2F', 0)

            if cl2f_pos != 0:
                side = 'SELL' if cl2f_pos > 0 else 'BUY'
                helper.place_order(session, ticker='CL-2F', quantity=abs(cl2f_pos), action=side, order_type='MARKET')
                print(f"Closed Other News position: {side} {abs(cl2f_pos)} contracts of CL-2F.")

            other_active_trade = {
                "entry_tick": None,
                "side": None,
                "quantity": 0
            }

    # === Try to open new trades ===
    EIA_trade(session)
    other_news_trade(session)
