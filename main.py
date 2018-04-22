import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
import numpy as np
from collections import OrderedDict


def MakingProfitLine_B():
    val = order['price']+(margin['profit']+(order['price']*margin['profit_rate']))
    print('元値:'+str(order['price'])+'利確ライン:'+str(val))
    return val
def MakingStopLine_B():
    val = order['price']-(margin['lost']+(order['price']*margin['lost_rate']))
    print('元値:'+str(order['price'])+'損切ライン:'+str(val))
    return val

def MakingProfitLine_S():
    val = order['price']-(margin['profit']+(order['price']*margin['profit_rate']))
    print('元値:'+str(order['price'])+'利確ライン:'+str(val))
    return val
def MakingStopLine_S():
    val = order['price']+(margin['lost']+(order['price']*margin['lost_rate']))
    print('元値:'+str(order['price'])+'損切ライン:'+str(val))
    return val

#-----
# Initial Setting
#-----

money = 200             # unit = $
threshold = {
    'volume': 5000000,
    'div': 0.55,
}
margin = {
    "order": 2.5,
    "order_cancel": 10,
    "profit": 12,       #unit = $
    "profit_rate": 0,  #unit = [100%]
    "lost": 30,         #unit = $
    "lost_rate": 0,    #unit = [100%]
}
span = {
    "long": 480,
    "short": 120,
    "volume": 10,
}

counter = OrderedDict()
counter['bpos'] = 0
counter['bposprofit'] = 0
counter['bposlost'] = 0
counter['spos'] = 0
counter['sposprofit'] = 0
counter['sposlost'] = 0
counter['volume'] = 0

cashier = OrderedDict()
cashier['bposprofit'] = 0
cashier['bposlost'] = 0
cashier['sposprofit'] = 0
cashier['sposlost'] = 0

current = {
    'pos': 'none',
}
order = {}

#空のデータフレームを作成 = 残高用
account = pd.DataFrame(index=[], columns=['money','time'])

data = pd.read_csv("historical_data.csv",
                 header=None,
                 parse_dates=True,
                 index_col='datetime',
                 names=['datetime', 'price', 'volume'])

data['ewma_long'] = data['price'].ewm(span=span['long'], adjust=True).mean()
data['ewma_short'] = data['price'].ewm(span=span['short'], adjust=True).mean()
data['volume_avg'] = data['volume'].ewm(span=span['volume'], adjust=True).mean()

data['div_long'] = (data['price'] - data['ewma_long']) / data['ewma_long'] * 100 # 長時間移動平均に対する乖離率
data['div_short'] = (data['price'] - data['ewma_short']) / data['ewma_short'] * 100 # 短時間移動平均に対するそのときの乖離率

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
data["price"].plot(label="label-Price",legend=True,ax = ax1,)
data['ewma_long'].plot(label="ewma long",legend=True,ax = ax1,)
data['ewma_short'].plot(label="ewma short",legend=True,ax = ax1,)
data['div_long'].plot(label="div long",legend=True,ax = ax2,  linestyle='dashed')
data['div_short'].plot(label="div short",legend=True,ax = ax2,  linestyle='dashed')



for i, v in data.iterrows():


    current['time'] = i
    current['price'] = v['price']
    current['volume'] = v['volume_avg']
    current['ewma_short'] = v['ewma_short']
    current['ewma_long'] = v['ewma_long']
    current['div_short'] = v['div_short']
    current['div_long'] = v['div_long']

    #    print ('Time:' + str(i))
    #    print ('Pos:' + str(current['pos']))
    #    print ('Money:' + str(money))
    print('Vol' + str(current['volume']))

    if current['pos'] == 'none':
        if threshold['div'] > abs(current['div_long']):
            if threshold['volume'] > current['volume']:
                if (current['ewma_short'] > current['ewma_long'] and current['price'] > current['ewma_short']) or (current['ewma_short'] < current['ewma_long'] and current['price'] > current['ewma_short']):         # 買いポジ
                    order['price'] = current['price'] - margin['order']
                    order['price_cancel_entry'] = current['price'] + margin['order_cancel']
                    current['pos'] = 'bought_w'
                if (current['ewma_short'] < current['ewma_long'] and current['price'] < current['ewma_short']) or (current['ewma_short'] > current['ewma_long'] and current['price'] < current['ewma_short']):         # 売りポジ
                    order['price'] = current['price'] + margin['order']
                    order['price_cancel_entry'] = current['price'] - margin['order_cancel']
                    current['pos'] = 'sold_w'
            else:
                counter['volume'] +=1

    elif current['pos'] == 'bought_w':               #買いポジエントリーまちの時
        if order['price'] > current['price']:
            order['size'] = money / current['price']
            order['profitline'] = MakingProfitLine_B()
            order['stopline'] = MakingStopLine_B()
            counter['bpos'] += 1
            current['pos'] = 'bought'
            money = money - (order['size'] * order['price'])
        if order['price_cancel_entry'] < current['price']:
            current['pos'] = 'none'
            print('買いポジエントリー待ちキャンセル')

    elif current['pos'] == 'sold_w':               #売りポジエントリーまちの時
        if order['price'] < current['price']:
            order['size'] = money / current['price']
            order['profitline'] = MakingProfitLine_S()
            order['stopline'] = MakingStopLine_S()
            current['pos'] = 'sold'
            counter['spos'] += 1
            money = money + (order['size'] * order['price'])
        if order['price_cancel_entry'] > current['price']:
            current['pos'] = 'none'
            print('売りポジエントリー待ちキャンセル')

    elif current['pos'] == 'bought':                #買いポジ持ってるとき
        if order['profitline'] < current['price']:   #利確
            print('買いポジ利確/利確ライン:'+str(order['profitline'])+'現在値:'+str(current['price'])+'エントリー:'+str(order['price']))
            current['pos'] = 'none'
            counter['bposprofit'] += 1
            cashier['bposprofit'] += order['size'] * (order['profitline'] - order['price'])
            money = money + (order['size'] * order['profitline'])
            series = pd.Series([money, current['time']], index=account.columns)
            account = account.append(series, ignore_index=True)
        elif order['stopline'] > current['price']:   #損切り
            print('買いポジ損切/損切ライン:'+str(order['stopline'])+'現在値:'+str(current['price'])+'エントリー:'+str(order['price']))
            current['pos'] = 'none'
            counter['bposlost'] += 1
            cashier['bposlost'] += order['size'] * (order['stopline'] - order['price'])
            money = money + (order['size'] * order['stopline'])
            series = pd.Series([money, current['time']], index=account.columns)
            account = account.append(series, ignore_index=True)

    elif current['pos'] == 'sold':  # 売りポジ持ってるとき
        if order['profitline'] > current['price']:   #利確
            print('売りポジ利確/利確ライン:'+str(order['profitline'])+'現在値:'+str(current['price'])+'エントリー:'+str(order['price']))
            current['pos'] = 'none'
            counter['sposprofit'] += 1
            money = money - (order['size'] * order['profitline'])
            cashier['sposprofit'] += order['size'] * (order['price'] - order['profitline'])
            series = pd.Series([money, current['time']], index=account.columns)
            account = account.append(series, ignore_index=True)
        elif order['stopline'] < current['price']:   #損切り
            print('売りポジ損切/損切ライン:'+str(order['stopline'])+'現在値:'+str(current['price'])+'エントリー:'+str(order['price']))

            current['pos'] = 'none'
            counter['sposlost'] += 1
            money = money - (order['size'] * order['stopline'])
            cashier['sposlost'] += order['size'] * (order['price'] - order['stopline'])
            series = pd.Series([money, current['time']], index=account.columns)
            account = account.append(series, ignore_index=True)

#print (account)

print ('------Pos Counter------')
for key, val in counter.items():
    print(key, val)

print ('------Cash Counter------')
for key, val in cashier.items():
    print(key, val)

account.plot(x='time',y = 'money')
plt.show()

pd.set_option("display.max_rows", 2000)
print (data['div_long'])
