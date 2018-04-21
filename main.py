import ccxt
import json
import pandas as pd
import numpy as np


#---Settings---#
timeframe = '1h'                        #
timespan = {'long': 24, 'short': 12}    # unit = [timeframe]


bitmex = ccxt.bitmex({
    'apiKey': 'apikey',
    'secret': 'secret',
})

fetchdata = {}
ewma = {}
grad = {}

#---Source---#



ticker = bitmex.fetch_ticker('BTC/USD')

fetchdata['raw'] = pd.DataFrame(bitmex.fetch_ohlcv(symbol = 'BTC/USD', timeframe = '1h'))
fetchdata['raw'].columns = ['timestamp', 'open', 'highest', 'lowest', 'closing', 'volume']

fetchdata['long'] = fetchdata['raw'][-1*timespan['long']:]
fetchdata['short'] = fetchdata['raw'][-1*timespan['short']:]

ewma['long'] = fetchdata['long']['closing'].ewm(span=3,min_periods=0,adjust=True,ignore_na=False).mean()
ewma['short'] = fetchdata['short']['closing'].ewm(span=3,min_periods=0,adjust=True,ignore_na=False).mean()
grad['long'] = np.gradient(ewma['long'])
grad['short'] = np.gradient(ewma['short'])

print (ewma['short'])
print (ewma['long'])
print (grad['short'])
print (grad['long'])

#def ewma(data,range):



#print(bitmex.fetch_ohlcv(symbol = 'BTC/USD', timeframe = '1m', limit = 10))

#[
#    [
#        1504541580000, // UTC timestamp in milliseconds, integer
#        4235.4,        // (O)pen price, float
#        4240.6,        // (H)ighest price, float
#        4230.0,        // (L)owest price, float
#        4230.7,        // (C)losing price, float
#        37.72941911    // (V)olume (in terms of the base currency), float
#    ],
#    ...
#]
