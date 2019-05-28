#!/usr/bin/env python3

from flask import Flask, render_template, request

import model
import orm


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def frontpage():
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        ticker_symbol = request.form.get('ticker_symbol')
        order_quantity = request.form.get('order_quantity')
        #print (ticker_symbol, order_quantity)
        # TODO Fix the following stub method
        return render_template('confirmation.html', ticker_symbol = ticker_symbol, order_quantity = order_quantity)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return render_template('index.html')

@app.route('/lookup', methods = ['GET', 'POST'])
def lookup():
    if request.method == 'GET':
        return render_template('lookup.html')
    else:
        user_submission = request.form.get('user_submission')
        return render_template('lookup.html', msg=model.lookup_passthrough(user_submission))


@app.route('/quote', methods = ['GET', 'POST'])
def quote():
    if request.method == 'GET':
        return render_template('quote.html')
    else:
        user_submission = request.form.get('user_submission')
        return render_template('quote.html', msg=model.lookup_passthrough(user_submission))  ## need to update to quote


@app.route('/mtm_pnl', methods = ['GET', 'POST'])
def pnl_position():
    if request.method == 'GET':
        return render_template('pnl_position.html')
    else:
        user_submission = request.form.get('user_submission')
        return render_template('pnl_position.html', msg=model.lookup_passthrough(user_submission))  ## need to update to PNL position

@app.route('/mtm_pnl_portfolio', methods = ['GET', 'POST'])
def pnl_portfolio():
    if request.method == 'GET':
        return render_template('pnl_portfolio.html')
    else:
        user_submission = request.form.get('user_submission')
        return render_template('pnl_portfolio.html', msg=model.lookup_passthrough(user_submission))  ## need to update to PNL portfolio




@app.route('/check_balance', methods = ['GET', 'POST'])
def check_balance():
    if request.method == 'GET':
        return render_template('check_balance.html')
    else:
        print ('check_balance')
        # ticker_symbol = request.form.get('ticker_symbol')   #TODO correct this for check_balance coding
        # order_quantity = request.form.get('order_quantity')


@app.route('/check_positions', methods = ['GET', 'POST'])
def check_positions():
    if request.method == 'GET':
        return render_template('check_positions.html')
    else:
        print ('check_positions')
        # ticker_symbol = request.form.get('ticker_symbol')   #TODO correct this for check_balance coding
        # order_quantity = request.form.get('order_quantity')


@app.route('/buy', methods = ['GET', 'POST'])
def buy():
    if request.method == 'GET':
        return render_template('buy.html')
    else:
        ticker_symbol = request.form.get('ticker_symbol')
        order_quantity = request.form.get('order_quantity')
        print (ticker_symbol, order_quantity)
        # confirmation_message = model.User('kyle').buy(ticker_symbol, order_quantity)
        #return render_template('confirm.html', msg = confirmation_message)

@app.route('/sell', methods = ['GET', 'POST'])
def sell():
    if request.method == 'GET':
        return render_template('sell.html')
    else:
        ticker_symbol = request.form.get('ticker_symbol')
        order_quantity = request.form.get('order_quantity')
        print (ticker_symbol, order_quantity)
        # confirmation_message = model.User('kyle').buy(ticker_symbol, order_quantity)
        #return render_template('confirm.html', msg = confirmation_message)




if __name__ == "__main__":
    app.run(debug=True)
