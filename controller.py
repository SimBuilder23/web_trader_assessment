#!/usr/bin/env python3

from flask import Flask, render_template, request

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

@app.route('/lookup', methods = ['GET', 'POST'])
def lookup():
    if request.method == 'GET':
        return render_template('lookup.html')
    else:
        user_submission = request.form.get('user_submission')
        return render_template('lookup.html', msg=model.lookup_passthrough(user_submission))


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






if __name__ == "__main__":
    app.run(debug=True)
