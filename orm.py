
#!/usr/bin/env python3

import csv
import datetime
import time

import psycopg2
import pandas as pd

import wrapper as w


#print ("in object_relational_mapper.py")

class Database:
    def __init__(self):
        self.connection = psycopg2.connect(dbname = 'terminal_trader')
        self.cursor     = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        if self.connection:
            if self.cursor:
                self.connection.commit()
                self.cursor.close()
            self.connection.close()

    def create_table(self, table_name):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        self.cursor.execute(
            """CREATE TABLE {table_name}(
                pk SERIAL PRIMARY KEY
            );""".format(table_name = table_name))

    def add_column(self, table_name, column_name, column_type):
        self.cursor.execute(
            """ALTER TABLE {table_name}
                ADD COLUMN {column_name} {column_type}
                ;""".format(table_name = table_name, column_name = column_name, column_type = column_type))

    def does_not_exist(username):
        with Database() as db:
            db.cursor.execute(
                "SELECT username FROM users WHERE username=%s;", (username,))
            occurences = db.cursor.fetchall()
            if len(occurences) < 1:
                print("occurences", occurences, type(occurences))
                return True
            else:
                print("username taken")
                return False







class User:

    def __init__(self, username):
        self.username = username

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        pass

    def login(self, password):
        with Database() as db:
            db.cursor.execute(
                """SELECT password
                    FROM users
                    WHERE username=%s;""",
                    (self.username,))
            if password == db.cursor.fetchone():
                return True
            else:
                return False

    def signup(self, password, balance):
        if does_not_exist(self.username):
            with Database() as db:
                db.cursor.execute(
                """INSERT INTO users(
                        username,
                        password,
                        balance
                    ) VALUES (
                        %s, %s, %s
                    );""", (self.username, password, balance)
                )
                return True
        else:
            return False



    def buy(self, ticker_symbol, trade_volume):
        # TODO connect to the model, un-hardcode the username, un-hardcode the price, un-hardcode the trade_volume

        buy = 1

        with Database() as db:
            db.cursor.execute(
                f"""SELECT balance from users where username='{self.username}';""")
            my_cash = db.cursor.fetchone()

            last_price = w.quote(ticker_symbol)
            execution_price = last_price

            market_value = User.calc_market_value(self, trade_volume, last_price)

            order_quantity = trade_volume
            time_stamp = time.time()

            if (float(my_cash[0]) >= market_value):
                User.update_balance (self, self.username, market_value)

                User.record_transaction (self, self.username, buy, execution_price, ticker_symbol, order_quantity, time_stamp)

                print ("Filled! You paid {} for {} {}.".format(last_price, trade_volume, ticker_symbol))

            else:
                print ("Rejected! You don't have enough funds available.")



    def sell(self, ticker_symbol, trade_volume):
        # TODO connect to the model, un-hardcode the username, un-hardcode the price, un-hardcode the trade_volume

        buy = 0   # zero value indicates a sell

        with Database() as db:
            db.cursor.execute(
                f"""SELECT current_holdings FROM positions
                    WHERE ticker_symbol = '{ticker_symbol}';""")  #TODO add back username
            my_position = db.cursor.fetchone()

            last_price = w.quote(ticker_symbol)
            execution_price = last_price

            order_quantity = trade_volume * -1 # makes a sell neg. qty
            time_stamp = time.time()

            market_value = User.calc_market_value(self, trade_volume, last_price) * -1 # makes a sell pos. cash


            if ((my_position[0]) >= abs(order_quantity)):
                User.update_balance (self, self.username, market_value)

                User.record_transaction (self, self.username, buy, execution_price, ticker_symbol, order_quantity, time_stamp)

                print ("Filled! You sold {} {} @ {}.".format(trade_volume, ticker_symbol, last_price))

            else:
                print (f"Rejected! You don't have enough {ticker_symbol} available to sell.")



    def mtm_pnl(self, ticker_symbol):

        ## pseudo: (current price - my avg price ) * my_position

        last_price = w.quote(ticker_symbol)

        with Database() as db:
            db.cursor.execute(
                f"""SELECT average_price FROM positions WHERE ticker_symbol = '{ticker_symbol}';""")
            my_avg_price = db.cursor.fetchone()
            my_avg_price = my_avg_price[0]

            db.cursor.execute(
                f"""SELECT current_holdings FROM positions WHERE ticker_symbol = '{ticker_symbol}';""")
            my_current_qty = db.cursor.fetchone()
            my_current_qty = my_current_qty[0]

        current_pnl = (last_price - my_avg_price) * my_current_qty
        return current_pnl


    def record_transaction(self, username, buy, execution_price, ticker_symbol, order_quantity, time_stamp):
        with Database() as db:
            db.cursor.execute(
            """INSERT INTO transactions(
                    user_id,
                    buy,
                    execution_price,
                    ticker_symbol,
                    order_quantity,
                    time_stamp
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                );""", (1, buy, execution_price, ticker_symbol, order_quantity, time_stamp)
            )

            # need to know if the ticker already exits in transactions, for that user; if yes, update the existing data
            db.cursor.execute(
            """SELECT ticker_symbol, current_holdings, average_price FROM positions where user_id=1;""")   #and ticker is ticker
            prior_positions = list(db.cursor.fetchall())   # should be one, if greater raise an error

            prior_tickers = []
            for item in prior_positions:
                prior_tickers.append(item[0])

            #if ticker_symbol has NOT been traded prior, set holdings equal to current transaction
            if ticker_symbol not in prior_tickers:
                db.cursor.execute(
                    """INSERT INTO positions(
                            user_id,
                            average_price,
                            ticker_symbol,
                            current_holdings
                        ) VALUES (
                            %s, %s, %s, %s
                        );""", (1, execution_price, ticker_symbol, order_quantity)
                )

            #else:
                #if ticker has been traded prior, but current position is zero, update holdings equal to current transaction
                #for item in prior_positions:
                #    if item[0] == ticker_symbol and item[1] == 0:
                #            db.cursor.execute(
                #                f"""UPDATE positions SET average_price = {execution_price}, current_holdings = {order_quantity} WHERE ticker_symbol = '{ticker_symbol}'"""
                #            )


            # creates single function that take existing holdings @ avg price, and updates to reflect new holdings qty and new avg price
            else:
                for item in prior_positions:
                    if item[0] == ticker_symbol:
                        old_qty = item[1]
                        old_avg_price = item[2]
                        old_mkt_value = old_qty * old_avg_price
                        break                       # is this good style/syntax - using a break here?

                # add original qty to order qty to get the updated holdings qty
                new_qty = old_qty + order_quantity

                # use SUMPRODUCT of original position and new order to get new avg price
                order_mkt_value = order_quantity * execution_price
                new_mkt_value = old_mkt_value + order_mkt_value

                if new_qty == 0:     #TODO if qty == 0, delete position row in SQL
                    new_avg_price = 0
                else:
                    new_avg_price = new_mkt_value / new_qty

                # update the positions table to reflect new_qty and new_avg_price
                db.cursor.execute(
                    f"""UPDATE positions SET average_price = {new_avg_price}, current_holdings = {new_qty} WHERE ticker_symbol = '{ticker_symbol}'"""
                )



            # if the ticker doesn't already exist in the transactions table, then need to insert ticker_symbol, and add the data

    def update_positions():
        pass




    def calc_market_value(self, trade_volume, last_price):

        ## PSEUDO:
        # need to finish with POS vs NEG costs for buy vs sell
        # calc_mkt_value = share qty * last_price
        # if buy: +qty * mkt_price = +mkt_value
        # if sell: -qty * mkt_price = -mkt_value

        market_value = trade_volume * last_price
        return market_value



    def update_balance(self, username, market_value):
        with Database() as db:
            db.cursor.execute(
                """SELECT balance FROM users where username = '{}';""".format(username))
            balance_start = db.cursor.fetchone()
            # balance_start returns a tuple; next line extracts the single value I want
            balance_start = balance_start[0]
            order_cost = market_value                   #TODO pass in the market_value
            balance_end = balance_start - order_cost   #TODO need to wrap in FLOAT? or already float??

            db.cursor.execute(
                """UPDATE users
                    SET balance = {}
                    WHERE username = '{}';""".format(balance_end, username))





if __name__ == "__main__":
    with User('simbuilder') as u:
        #ticker_symbol = input ("Which ticker? ")
        #volume = int( input ("How many shares? "))
        #u.sell(ticker_symbol, volume)  # ticker + order_qty

#        u.update_balance ('username', 25000)

        print(u.mtm_pnl('AAPL'))
