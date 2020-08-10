from candlestick import get_last_ATR, get_dataframe, get_last_price


# аргументом функции является название акции


def risk(action, stock):
    if action == 'Buy':
        return risk_buy(stock)
    elif action == 'Sell' :
        return risk_sell(stock)
    elif action == 'Skip' :
        pass
    else :
        return 'error, action must be buy or sell'
        
        
        
def risk_buy(stock):
    df, time = get_dataframe(stock, 500)
    atr = get_last_ATR(df)
    price = get_last_price(df, 'c')
    if price < 10000:
        stop = price - 2 * atr
        return stop, (stop / price) * 10   #сколько акций мы можем себе позволить, учитывая стоп лосс
    else:
        return 0, 0
      


def risk_sell(stock):
    df, time = get_dataframe(stock, 500)
    atr = get_last_ATR(df)
    price = get_last_price(df, 'c')
    if price > 10000:
        stop = price + 2 * atr
        return stop, (stop / price) * 10   #сколько акций мы можем себе позволить, учитывая стоп лосс
    else:
        return 0, 0