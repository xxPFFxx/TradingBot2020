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
print('Начало работы...')
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
    clock = api.get_clock()
    close = clock.next_close - clock.timestamp
    if clock.is_open:
        if close.total_seconds()>900:
            try:
                replace_stop_loss(api)
            except Exception as error:
                print(error)
            watch_list = api.get_watchlists()
            watch_list = watch_list[0].id
            mylist = api.get_watchlist(watch_list)

            dif_symbols = len(mylist.assets)
            print('Number of symbols: ', dif_symbols)

            for each in mylist.assets:


                unit = each['symbol']
                print('Symbol: ', unit)
                account = api.get_account()


                df = get_dataframe(unit,100)
                price = get_last_price(df[0],'c')
                print('Current price: ', price)

                todo = check_indicator(df[0],'hhll')


                trend = df[0].iloc[-1]['trend']
                if (trend == 'Buy' and todo == 'Buy'):
                    todo = 'Buy'
                elif (trend == 'Sell' and todo == 'Sell'):
                    todo = 'Sell'
                else:
                    todo = 'Skip'
                print('Action: ', todo)


                stop_price, qnty = risk(todo, unit,api)
                qnty = int(qnty)
                print('Stop price: ', stop_price)
                print('Quantity: ', int(qnty))

                total = qnty * price
                money = float(account.buying_power)

                if total>money:
                    qnty = int(money/price)
                if (qnty>0):
                    try:
                        api.submit_order(
                            symbol=unit,
                            qty=int(qnty/dif_symbols),
                            side=todo.lower(),
                            type='market',
                            time_in_force='gtc',
                            order_class='oto',
                            stop_loss={'stop_price':stop_price})
                    except Exception as error:
                        print(error)
        else:
            api.close_all_positions()
            api.cancel_all_orders()
    else:
        print('Рынок закрыт')


        
    
socket = "wss://data.alpaca.markets/stream"

ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever()
