#!/usr/bin/env python3

import json

import requests


def lookup(company_name):
    response = json.loads(requests.get(f'http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input={company_name}').text)
    ticker_symbol = response[0]['Symbol']
    return ticker_symbol

def quote(ticker_symbol):
    response = json.loads(requests.get(f'http://dev.markitondemand.com/MODApis/Api/v2/quote/json?symbol={ticker_symbol}').text)
    quote = response['LastPrice']
    return quote

if __name__ == "__main__":
 #   response = json.loads(requests.get('http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input=TSLA').text)
 #   user_input = input("What company name? ")
 #   print (lookup(user_input))

    user_input = input ("Which ticker symbol? ")
    print (quote(user_input))
