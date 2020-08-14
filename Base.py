import alpaca_trade_api as tradeapi 
from alpaca_trade_api import StreamConn
import time, websocket, json
import os 
import config
from replace_stop_loss import replace_stop_loss
import asyncio
from Risk import risk
from candlestick import get_dataframe, get_last_price, check_indicator
api = tradeapi.REST(config.KEY_ID, config.SECRET_Key, config.BASE_URL,api_version=config.API_VERSION)


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
    account = api.get_account()
    replace_stop_loss(api)
    # Получение информации из Candlestick
    df = get_dataframe(unit,100)
    price = get_last_price(df[0],'c')
    print('Current price: ', price)
    todo = check_indicator(df[0],'hhll')
    print('Action: ', todo)
    stop_price, qnty = risk(todo, unit,api)
    
    print('Stop price: ', stop_price)
    print('Quantity: ', int(qnty))
    total = qnty * price
    money = float(account.buying_power)
    if total>money:
        qnty = money/price
    if (stop_price>0 and qnty>0):
        try:
            api.submit_order(
                symbol=unit,
                qty=int(qnty),
                side=todo.lower(),
                type='market',
                time_in_force='gtc',
                order_class='oto',
                stop_loss={'stop_price':stop_price})
        except Exception as error:
            print(error)        
        
    
socket = "wss://data.alpaca.markets/stream"

ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever()
