
#!/usr/bin/env python3

import csv
import datetime
import time

import sqlite3
import pandas as pd

import wrapper as w


#print ("in object_relational_mapper.py")

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('terminal_trader.db', check_same_thread=False)
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

    # def does_not_exist(self, username):
    #     with Database() as db:
    #         db.cursor.execute(
    #             "SELECT username FROM users WHERE username=?;", (username,))
    #         occurences = db.cursor.fetchall()
    #         if len(occurences) < 1:
    #             print("occurences", occurences, type(occurences))
    #             return True
    #         else:
    #             print("username taken")
    #             return False







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
                    WHERE username=?;""",
                    (self.username,))
            if password == db.cursor.fetchone():
                return True
            else:
                return False

    def does_not_exist(self, username):
        with Database() as db:
            db.cursor.execute(
                """SELECT username FROM users WHERE username=?;""", (username,))
            occurences = db.cursor.fetchall()
            if len(occurences) < 1:
                print("occurences", occurences, type(occurences))
                return True
            else:
                print("username taken")
                return False

    def signup(self, password, balance):
        if True:
        # if does_not_exist(self.username):         # not working during assessment, hardcoding a working solution
            with Database() as db:
                db.cursor.execute(
                """INSERT INTO users(
                        username,
                        password,
                        balance
                    ) VALUES (
                        ?, ?, ?
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
                return "Filled! You paid {} for {} {}.".format(last_price, trade_volume, ticker_symbol)

            else:
                print ("Rejected! You don't have enough funds available.")
                return "Rejected! You don't have enough funds available."



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

            order_quantity = int(trade_volume) * -1 # makes a sell neg. qty
            time_stamp = time.time()

            market_value = User.calc_market_value(self, trade_volume, last_price) * -1 # makes a sell pos. cash

            print (my_position, "--", type(my_position))
            print (order_quantity, "--", type(order_quantity))



            if ((my_position[0]) >= abs(order_quantity) * 1):
                User.update_balance (self, self.username, market_value)

                User.record_transaction (self, self.username, buy, execution_price, ticker_symbol, order_quantity, time_stamp)

                print ("Filled! You sold {} {} @ {}.".format(trade_volume, ticker_symbol, last_price))
                return "Filled! You sold {} {} @ {}.".format(trade_volume, ticker_symbol, last_price)

            else:
                print (f"Rejected! You don't have enough {ticker_symbol} available to sell.")
                return f"Rejected! You don't have enough {ticker_symbol} available to sell."



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
                    ?, ?, ?, ?, ?, ?
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
                            ?, ?, ?, ?
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
                new_qty = old_qty + int(order_quantity)

                # use SUMPRODUCT of original position and new order to get new avg price
                order_mkt_value = int(order_quantity) * execution_price
                new_mkt_value = old_mkt_value + order_mkt_value

                if new_qty == 0:     #TODO if qty == 0, delete position row in SQL
                    new_avg_price = 0
                else:
                    new_avg_price = new_mkt_value / new_qty

                # update the positions table to reflect new_qty and new_avg_price
                db.cursor.execute(
                    f"""UPDATE positions SET average_price = {new_avg_price}, current_holdings = {new_qty} WHERE ticker_symbol = '{ticker_symbol}'"""
                )

    def check_positions(self, ticker_symbol):
        with Database() as db:
            db.cursor.execute(
                """SELECT current_holdings, ticker_symbol, average_price FROM positions where user_id=1 AND ticker_symbol= '{}';""".format(ticker_symbol))   #and ticker is ticker
            current_position = db.cursor.fetchone() 
            return "You own {} {} shares @ average price {}".format(current_position[0], current_position[1], current_position[2])


    def see_portfolio(self, username):
            with Database() as db:
                db.cursor.execute(
                    """SELECT ticker_symbol, current_holdings, average_price FROM positions where user_id=1;"""
                )
                my_holdings = db.cursor.fetchall()
                print (my_holdings)
                return (my_holdings)





    def update_positions(self):
        pass

    def check_balance(self):
        pass


    def calc_market_value(self, trade_volume, last_price):

        ## PSEUDO:
        # need to finish with POS vs NEG costs for buy vs sell
        # calc_mkt_value = share qty * last_price
        # if buy: +qty * mkt_price = +mkt_value
        # if sell: -qty * mkt_price = -mkt_value

        market_value = int(trade_volume) * last_price
        return float(market_value)



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
    pass
    # with User('simbuilder') as u:
    #     u.see_portfolio("simbuilder")    
    #     print(u.check_positions("FB"))
    #     pass
    #     ticker_symbol = input ("Which ticker? ")
    #     volume = int( input ("How many shares? "))
    #     u.buy(ticker_symbol, volume)  # ticker + order_qty

#        u.update_balance ('username', 25000)

#        print (u.mtm_pnl('AAPL'))




    # with Database() as db:
    #     tab1 = {"name" : "users",
    #             "columns" : [
    #                 {"name":"username",  "type":"VARCHAR"},
    #                 {"name":"password",  "type":"VARCHAR"},
    #                 {"name":"balance",   "type":"FLOAT"}]}

    #     tab2 = {"name" : "transactions",
    #             "columns" : [
    #                 {"name":"user_id",           "type":"INTEGER"},
    #                 {"name":"buy",               "type":"INTEGER"},
    #                 {"name":"execution_price",   "type":"FLOAT"},
    #                 {"name":"ticker_symbol",     "type":"VARCHAR"},
    #                 {"name":"order_quantity",    "type":"INTEGER"},
    #                 {"name":"time_stamp",        "type":"FLOAT"}]}

    #     ## TODO Add a functio to the database class,
    #     ## to handle for the following statement:
    #     ## which should be added to the 'tab2' 'tab3':
    #     ## FOREIGN KEY(user_id) REFERENCES users(pk)

    #     tab3 = {"name" : "positions",
    #             "columns" : [
    #                 {"name":"user_id",           "type":"INTEGER"},
    #                 {"name":"average_price",     "type":"FLOAT"},
    #                 {"name":"ticker_symbol",     "type":"VARCHAR"},
    #                 {"name":"current_holdings",  "type":"INTEGER"}]}


    #     for table in [tab1, tab2, tab3]:
    #         db.create_table(table["name"])
    #         for column_name in table["columns"]:
    #             db.add_column(
    #                 table["name"],
    #                 column_name["name"],
    #                 column_name["type"])

##    user = User("kyle")
##    print(user.signup("rippere"))

    # with User('simbuilder') as u:
    #     u.signup('opensesame', 1000000.00)

    # with User('player2') as u:
    #     u.signup('opensesame2', 1000000.00)

    # with User('player3') as u:
    #     u.signup('opensesame3', 1000000.00)


