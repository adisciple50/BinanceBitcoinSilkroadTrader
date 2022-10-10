from binance.spot import Spot
import os
import time
import math
client = Spot(key=os.environ['binance-scout-key'],secret=os.environ['binance-scout-secret'])

def get_balance_for_currency(currency='GBP'):
    for balance in client.account_snapshot('SPOT')['snapshotVos'][0]['data']['balances']:
        if balance['asset'] == currency:
            return float(balance['free'])

def get_price(pair:str):
    return float(client.ticker_price(pair)['price'])

def market_sell_order(symbol,amount):
    first_order_params = {
        'symbol': symbol,
        'side': 'SELL',
        'type': 'MARKET',
        'amount': amount
    }
    return client.new_order(**first_order_params)

def timeout(wallet_currency_to_wait_for,starting_wallet_balance):
    retries = 0
    while get_balance_for_currency(currency='ETH') == starting_wallet_balance or retries <= 5:
        time.sleep(0.1)
        retries += 1
    return retries < 5

def truncate(i,n):
    decimal_place_point = str(i).find('.')
    tenths = len(i[decimal_place_point + 1:-1])
    truncated = n - tenths
    return i[0:truncated]


def make_trades(trading=True):
    while trading:
        gbp_balance = get_balance_for_currency('GBP')
        eth_balance = get_balance_for_currency('ETH')
        btc_balance = get_balance_for_currency('BTC')
        order1price = get_price('ETHGBP')
        order2price = get_price('ETHBTC')
        order3price = get_price('BTCGBP')
        secret_sauce_stage_1 = order1price * order2price * order3price
        secret_sauce_stage_2 = secret_sauce_stage_1 / order1price
        profit = secret_sauce_stage_2 - order1price
        if profit > 0.05:
            first_order_mod = gbp_balance % order1price
            amount_to_order_with = gbp_balance - first_order_mod
            first_order = amount_to_order_with / order1price
            first_order_params = {
                'symbol': 'ETHGBP',
                'side': 'BUY',
                'type': 'MARKET',
                'amount':first_order
            }
            order1 = client.new_order(**first_order_params)
            if check_if_filled(order1):
                if get_price('ETHBTC') > order2price:
                    order2 = market_sell_order('ETHBTC',str(truncate(get_balance_for_currency('ETH'),4)))
                    if check_if_filled(order2):
                        if get_price('BTCGBP') > order3price:
                            order3 = market_sell_order('BTCGBP',str(truncate(get_balance_for_currency('GBP'),5)))
                        else:
                            while get_price('BTCGBP') < order3price:
                                time.sleep(0.1)
                            order3 = market_sell_order('BTCGBP',str(truncate(get_balance_for_currency('GBP'),5)))
                    else:
                        while get_price('ETHBTC') < order2price:
                            time.sleep(0.1)
                        order2 = market_sell_order('ETHBTC',str(truncate(get_balance_for_currency('ETH'),4)))
                        if check_if_filled(order2):
                            if get_price('BTCGBP') > order3price:
                                order3 = market_sell_order('BTCGBP',str(truncate(get_balance_for_currency('GBP'),5)))
                            else:
                                while get_price('BTCGBP') < order3price:
                                    time.sleep(0.1)
                                order3 = market_sell_order('BTCGBP',str(truncate(get_balance_for_currency('GBP'),5)))
                        else:
                            if timeout('ETH', eth_balance):
                                if get_price('ETHBTC') > order2price:
                                    order2 = market_sell_order('ETHBTC',str(truncate(get_balance_for_currency('ETH'),4)))
                                    if check_if_filled(order2):
                                        order3 = market_sell_order('BTCGBP', get_balance_for_currency('BTC'))
                                    else:
                                        continue
                else:
                    while get_price('ETHBTC') < order2price:
                        time.sleep(0.1)
                    order2 = market_sell_order('ETHBTC', str(get_balance_for_currency('ETH')))
            else:
                if timeout('ETH',eth_balance):
                    if get_price('ETHBTC') > order2price:
                        order2 = market_sell_order('ETHBTC',get_balance_for_currency('ETH'))
                        if check_if_filled(order2):
                            order3 = market_sell_order('BTCGBP', get_balance_for_currency('BTC'))
                        else:
                            while get_price('ETHBTC') * get_price('BTCGBP') /
                else:
                    continue


def check_if_filled(order):
    return order['status'] == 'FILLED'


if __name__ == '__main__':
    print(make_trades())