"""
test_helper.py

Basic tests for helper.py functions.
"""

import requests
import helper
from config import API_KEY
import time

def initialize_session():
    """
    Initialize an authenticated session.
    """
    session = requests.Session()
    session.headers.update({'X-API-Key': API_KEY})
    return session


def test_get_position(session):
    ticker = "CL"
    position = helper.get_position(session, ticker)
    print(f"Position for {ticker}: {position}")


def test_ticker_bid_ask(session):
    ticker = "CL"
    bid, ask = helper.ticker_bid_ask(session, ticker)
    print(f"Bid/Ask for {ticker}: {bid}/{ask}")


def test_get_tick(session):
    tick = helper.get_tick(session)
    print(f"Current tick: {tick}")


def test_get_orders(session):
    status = "OPEN"
    orders = helper.get_orders(session, status)
    print(f"Open orders: {orders}")


def test_get_nlv(session):
    nlv = helper.get_nlv(session)
    print(f"Net Liquidation Value (NLV): {nlv}")


def test_get_portfolio(session):
    portfolio = helper.get_portfolio(session)
    print(f"Portfolio snapshot: {portfolio}")


def test_place_order(session):
    ticker = "CL"
    quantity = 10
    action = "BUY"
    order_type = "MARKET"
    order_response = helper.place_order(session, ticker, quantity, action, order_type)
    print(f"Order placed: {order_response}")


def test_cancel_order(session):
    order_id = "12345"
    cancellation_response = helper.cancel_order(session, order_id)
    print(f"Order cancelled: {cancellation_response}")


def test_lease_storage(session):
    ticker = "CL-STORAGE"
    lease_response = helper.lease_storage(session, ticker)
    print(f"Storage leased: {lease_response}")


def test_lease_refinery(session):
    lease_response = helper.lease_refinery(session)
    print(f"Refinery leased: {lease_response}")


def test_use_refinery(session):
    from_ticker = "CL"
    quantity = 10
    helper.use_refinery(session, from_ticker, quantity)
    print(f"Refinery use initiated: {quantity}")


def test_close_unused_storage_leases(session):
    closed_leases = helper.close_unused_storage_leases(session)
    print(f"Closed unused leases: {closed_leases}")


def test_get_refinery_lease_info(session):
    lease_id, next_lease_tick = helper.get_refinery_lease_info(session)
    print(f"Refinery lease info - ID: {lease_id}, Next renewal tick: {next_lease_tick}")


def test_wait_and_close_refinery(session):
    lease_id = 1
    lease_finish_tick = 543
    close_refinery_response = helper.wait_and_close_refinery(session, lease_id, lease_finish_tick)
    print(f"Refinery lease closed: {close_refinery_response}")

def test_lease_use_transport(session):
    helper.lease_use_transport(session, "CS-NYC-PIPE", "CL", 10)


if __name__ == "__main__":
    s = initialize_session()
    
    # test_get_position(s)
    # test_ticker_bid_ask(s)
    # test_get_tick(s)
    # test_get_orders(s)
    # test_get_nlv(s)
    # test_get_portfolio(s)
    
    # test_lease_storage(s)

    # time.sleep(3)

    # test_place_order(s)

    # time.sleep(3)

    # test_lease_refinery(s)

    # time.sleep(3)

    # test_use_refinery(s)

    # test_close_unused_storage_leases(s)
    # test_get_refinery_lease_info(s)
    # test_wait_and_close_refinery(s)

    test_lease_use_transport(s)

    
