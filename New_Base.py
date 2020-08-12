import alpaca_trade_api as tradeapi 
from alpaca_trade_api import StreamConn
import time, websocket, json
import os 
import config
from replace_stop_loss import replace_stop_loss
import asyncio
from Risk import risk
from candlestick import get_dataframe, get_last_price, check_indicator
api = tradeapi.REST('PKI5VSIHBY5QD660GUDG', '2BSNsP8amM0q7eFk0dq/xV4IOHhcYKQpcaWndd4u', 'https://paper-api.alpaca.markets',api_version='v2')


# Ввод нужной акции для работы
print("Введите акцию для отслеживания: ")
unit = input().upper()


def on_open(ws):
    print("opened")
    auth_data = {
        "action": "authenticate",
        "data": {"key_id": config.KEY_ID, "secret_key": config.SECRET_Key}
    }

    ws.send(json.dumps(auth_data))

    listen_message = {"action": "listen", "data": {"streams": ["AM.AAPL"]}}

    ws.send(json.dumps(listen_message))
   


def on_message(ws, message):
    print("received a message")
    print(message)
    workplace()
    
    

def on_close(ws):
    print("closed connection")

def workplace():
    #Получение информации из API ALPACA
    barset = api.get_barset(unit,'day',limit=5)
    account = api.get_account()
    aapl_bars = barset[unit]
    replace_stop_loss(api)
    print('equity ')
    print('bars ', aapl_bars[-1].c)
    # Получение информации из Candlestick
    df = get_dataframe(unit,100)
    price = get_last_price(df[0],'c')
    print('price ', price)
    todo = check_indicator(df[0],'hhll')
    print('todo: ', todo)
    stop_price, qnty = risk(todo, unit,api)
    print('risks: ', stop_price, qnty)
    total = qnty * price
    money = float(account.last_equity)
    if (stop_price>0 and qnty>0):
        if (total<money):
            api.submit_order(
                symbol=unit,
                qty=qnty,side=todo.lower(),
                type='market',
                time_in_force='gtc',
                order_class='oto',
                stop_loss={'stop_price':stop_price})
        else:
            qnty = money / price
            api.submit_order(
                symbol=unit,
                qty=qnty,side=todo.lower(),
                type='market',
                time_in_force='gtc',
                order_class='oto',
                stop_loss={'stop_price':stop_price})
        
        
    
socket = "wss://data.alpaca.markets/stream"

ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever()
