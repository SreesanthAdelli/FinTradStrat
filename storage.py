import helper
from time import sleep

# Set the current round (1 or 2) at the top
round_num = 2  # Change to 2 after 600 ticks

def CL_future_arb(session, future, tick, threshold=0.15):
    if future == "CL-2F":
        expected_difference = 2 if round_num == 1 else 1
    elif future == "CL-1F":
        expected_difference = 1

    CL_bid, CL_ask = helper.ticker_bid_ask(session, "CL")
    CL_future_bid, CL_future_ask = helper.ticker_bid_ask(session, future)

    if not CL_bid or not CL_ask or not CL_future_bid or not CL_future_ask:
        print(f"Error fetching bid/ask prices for CL or {future}")
        return

    cl_price = (CL_bid + CL_ask) / 2
    cl_future_price = (CL_future_bid + CL_future_ask) / 2

    # Expected storage cost decays with time
    expected_difference = max(0, expected_difference - 0.05 * (tick / 30))
    spread = cl_future_price - cl_price - expected_difference
    print(f"[Tick {tick}] {future} storage spread: {spread:.2f}")

def storage_model(session):
    # Call for both futures
    tick = helper.get_tick(session)
    # In round 1, both futures exist
    if round_num == 1:
        CL_future_arb(session, "CL-1F", tick)
        CL_future_arb(session, "CL-2F", tick)
    # In round 2, CL-1F has expired
    elif round_num == 2:
        CL_future_arb(session, "CL-2F", tick)

