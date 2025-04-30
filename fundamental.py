import helper
import time
import globals
import re

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
    net = helper.get_net_position(session)

    
    TRADE_QUANTITY = 90


    

    if expected_price_move > 0.2:
        # Bullish → Buy
        max_allowed = (POSITION_LIMIT - net)
        quantity = min(TRADE_QUANTITY, max_allowed)
        quantity = quantity - quantity % 3

        
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
        
        max_allowed = (POSITION_LIMIT + net)
        quantity = min(TRADE_QUANTITY, max_allowed)
        quantity = quantity - quantity % 3

        

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



def pipeline_news(session):
    """
    Pipeline news model to check for any pipeline-related news.
    For now: very simple example based on keyword 'PIPELINE'.
    """

    news_items = helper.get_latest_news(session)

    

    latest_news = news_items[0]
    if latest_news.get('ticker') == "AK-CS-PIPE":
        print("Pipeline news detected.")
        headline = latest_news.get('headline', '').upper()
        match = re.search(r"\$?([\d,]+)", headline)
        number_str = match.group(1)
        number = int(number_str.replace(',', ''))
        print(f"AK-CS-PIPE lease price updated to {number}")
        globals.AK_CS_PIPE = number
    if  latest_news.get('ticker') == "CS-NYC-PIPE":
        print("Pipeline news detected.")
        headline = latest_news.get('headline', '').upper()
        match = re.search(r"\$?([\d,]+)", headline)
        number_str = match.group(1)
        number = int(number_str.replace(',', ''))
        print(f"CS-NYC-PIPE lease price updated to {number}")
        globals.CS_NYC_PIPE = number


        


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


            side = "BUY" if eia_active_trade["side"] == "SELL" else "SELL"
            quantity = eia_active_trade["quantity"]
            
            helper.place_order(session,'CL-2F', quantity/3, action=side, order_type='MARKET')
            helper.place_order(session,'CL-2F', quantity/3, action=side, order_type='MARKET')
            helper.place_order(session,'CL-2F', quantity/3, action=side, order_type='MARKET')
            print(f"Closed EIA position: {side} {quantity} contracts of CL-2F.")

            eia_active_trade = {
                "entry_tick": None,
                "side": None,
                "quantity": 0
            }


    # === Try to open new trades ===
    EIA_trade(session)
    pipeline_news(session)
