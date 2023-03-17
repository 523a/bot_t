# -*- coding: utf-8 -*-

from flask import Flask , request, render_template
#import bot1b as bt
#from config import api_key, api_secret
from binance.client import Client
from binance.spot import Spot
from pandas import DataFrame
#import sys
import time

btapp = Flask(__name__)

#par1=None;par2=None;par3=None;par4=None;par5=None;par6=None;
api_key=[]
api_secret=[]

SYMBOL = 'ALGOUSDT'
INTERVAL = '1m'
LIMIT = '200'
QNTY = 60
SPAN = 8


client = Client(api_key, api_secret)
cl = Spot()

def renum():
    global SYMBOL
    global INTERVAL
    global LIMIT
    global QNTY
    global SPAN
    SYMBOL = str(request.form.get("par1"))
    INTERVAL = str('5m')
    LIMIT = request.form.get("par3")
    QNTY = request.form.get("par5")
    SPAN = int(request.form.get("par6"))
    print(SYMBOL,INTERVAL,LIMIT,QNTY,SPAN)
    return()
#def ex(par1,par2,par3,par4):
#    print(type(par1))
#    return(par1,par2,par3,par4)

#получение данных со спотового рынка и расчет дончин
def get_data():
    r = cl.klines (SYMBOL, INTERVAL,  limit=35)
    df = DataFrame(r).iloc[:, :5]
    df.columns = list("tohlc")
    df['ema'] = df['c'].ewm(span=5, adjust=False).mean()
    df['ud'] = df['h'].rolling(SPAN).max()
    df['ld'] =df['l'].rolling(SPAN).min()
    df['md'] = (df['ud'] + df['ld']) / 2
    ud = float(df['ud'][-1:])
    ld = float(df['ld'][-1:])
    md = float(df['md'][-1:])
    ema =round(float(df['ema'][-1:]),4)
    ap = float(df['c'][-1:])
    return (ud,ld,md,ema,ap)
#####################################################################
def place_order(order_type):
    if(order_type == 'buy'):
        order = client.create_order(symbol=SYMBOL, side='buy', type='MARKET', quantity= QNTY)
        print('Open position', order)
    else:
        order = client.create_order(symbol=SYMBOL, side='sell', type='MARKET', quantity= QNTY)
        print('Close position', order)
    return


def go():
    global par4
    par4=0
    par4 = request.form.get("par4")
#    print(par4,id(par4))
    buy = False
    sell = True
    pp=0
    
    while int(par4) >= 1:
        
        par4 = request.form.get("par4")
#        print(par4,"##########",id(par4))
        ud,ld,md,ema,ap = get_data()
        take_profit = (ap-pp)/ap
#        print (ld, ap, ema, pp)
        if( ap >= ema and ap <= ld  and not buy):
            pp=ap
            place_order('BUY')
            buy = not buy
            sell = not sell
            print("bay")

        if(take_profit >= 0.01  and not sell):
            place_order('SELL')
            buy = not buy
            sell = not sell
            print("sell")

        time.sleep(1)          
        






# API ================================================================
@btapp.route('/', methods=['POST', 'GET'])

def data():

    api_key = request.form.get("api_key")  # запрос к данным формы
    api_secret = request.form.get("api_secret")
    par1 = request.form.get("par1")
    par2 = request.form.get("par2")
    par3 = request.form.get("par3")
    par4 = request.form.get("par4")
    par5 = request.form.get("par5")
    par6 = request.form.get("par6")
    renum()
    ud,ld,md,ema,ap = get_data()
    go()
    #ex(par1,par2,par3,par4)
#    par4=1
#   if int(par4) > 0:
#    go()
#    else:
#        print(par4,'#########################################')
#        sys.exit()
        
    return render_template('index.html', api_key=api_key, api_secret=api_secret, 
                           par1=par1, par2=par2, par3=par3, par4=par4, 
                           par5=par5, par6=par6, ld=ld, ap=ap, ema=ema)




if __name__ == '__main__': 
    btapp.run(host='0.0.0.0', port=5600)