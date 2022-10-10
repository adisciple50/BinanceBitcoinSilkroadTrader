from binance.spot import Spot
import os

client = Spot(key=os.environ['binance-scout-key'],secret=os.environ['binance-scout-secret'])

def get_balance_for_currency(currency='GBP'):
    for balance in client.account_snapshot('SPOT')['snapshotVos'][0]['data']['balances']:
        if balance['asset'] == currency:
            return float(balance['free'])

def make_trades():
    gbp_balance = get_balance_for_currency()
    eth_balance = get_balance_for_currency('ETH')
    btc_balance = get_balance_for_currency('BTC')
    order1price = float(client.ticker_price('ETHGBP')['price'])
    order2price = float(client.ticker_price('ETHBTC')['price'])
    order3price = float(client.ticker_price('BTCGBP')['price'])
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
        if order1['status'] == 'FILLED':

        else:
            while get_balance_for_currency(currency='ETH')



if __name__ == '__main__':
    print(make_trades())