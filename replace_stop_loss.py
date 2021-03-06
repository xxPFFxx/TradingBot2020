# Поскольку все stoploss хранятся как заявки типа "стоп", считываем все открытые заявки, находим среди них stop и, если
# цена пошла в нужную сторону, обновляем стоплоссы до значений, найденных с помощью функции Саши
from stop_loss import stop_loss

def replace_stop_loss(api):
    opened_orders = api.list_orders()  # Получаем все открытые заявки
    for each in opened_orders:
        if each.order_type == 'stop':  # Рассматриваем только стоп-ордеры
            new_stop = stop_loss(each.side, each.symbol, api)  # С помощью функции Саши получаем новый стоплосс
            if each.side == 'sell':
                if new_stop > float(each.stop_price):  # Если акция выросла в цене, обновляем стоплосс
                    api.replace_order(order_id=each.id, stop_price=new_stop)
            else:
                if new_stop < float(each.stop_price):  # Если акции подешевели, обнавляем стоплосс
                    api.replace_order(order_id=each.id, stop_price=new_stop)
