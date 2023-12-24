# bot.py | Binance coin tradebot made with Python
# *-* coding:utf-8 *-*

# modules
from binance.client import Client
from binance.enums import *

from pprint import pprint
import websocket
import json
import talib
import numpy


# ...
API_KEY = 'yourbinanceapikey'
API_SECRET = 'yourbinancesecret'

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.01

closes = []
in_position = False


# methods
def binance_order(synbol, side, quantity, order_type=ORDER_TYPE_MARKET):
    try:
        print('sending binance order')
        order = Client.create_order(synbol=synbol, side=side, quantity=quantity, type=order_type)
        print(order)
    except Exception as e:
        print('an exception occured - {}'.format(e))
        return False

def check_sell_or_buy(last_rsi):
    global in_position

    if last_rsi > RSI_OVERBOUGHT:
        if in_position:
            print('Overbought! SELL')
            order_status = binance_order(TRADE_SYMBOL, SIDE_SELL, TRADE_QUANTITY)
            if order_status:
                in_position = False
        else:
            print('It is overbought but we don\' t own any')
    if last_rsi < RSI_OVERSOLD:
        if in_position:
            print('It is oversold but we already own it')
        else:
            print('Oversold! BUY')
            order_status = binance_order(TRADE_SYMBOL, SIDE_BUY, TRADE_QUANTITY)
            if order_status:
                in_position = True

def on_open(ws):
    print('connection opened')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    print('received message')
    json_message = json.loads(message)
    #pprint(json_message)
    candle = json_message['k']
    close = candle['c']
    is_candle_closed = candle['x']
    if is_candle_closed:
        print('candle closed at: ', close)
        closes.append(float(close))
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print('all RSIs calculated so far')
            print(rsi)
            last_rsi = rsi[-1]
            print('the current RSI value is ', last_rsi)
            check_sell_or_buy(last_rsi)

# ...
ws = websocket.WebSocketApp(
    SOCKET,
    on_open=on_open,
    on_close=on_close,
    on_message=on_message
)
ws.run_forever()