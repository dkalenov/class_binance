import hashlib
import hmac
import time
import urllib.parse
from requests import request


class BinanceApi:
    spot_link = "https://api.binance.com"
    futures_link = "https://fapi.binance.com"

    def __init__(self, api_key=None, secret_key=None, futures=False):
        self.api_key = api_key
        self.secret_key = secret_key
        self.futures = futures
        self.base_link = self.futures_link if self.futures else self.spot_link
        self.header = {'X-MBX-APIKEY': self.api_key}

    def gen_signature(self, params):
        params_str = urllib.parse.urlencode(params)
        sign = hmac.new(bytes(self.secret_key, "utf-8"), params_str.encode("utf-8"), hashlib.sha256).hexdigest()
        return sign


    def http_request(self, method, endpoint, params=None, sign_need=False):
        """
        Sends a http request to the trading platform server
        :param endpoint: request url
        :param method: request type (GET, POST, DELETE)
        :param params: request body (params)
        :param sign_need: check if a signature needs to be inserted
        :return: :class:Response (requests.models.Response)
        """
        if params is None:
            params = {}
        # If necessary, add parameters for the signature to the dictionary - the time stamp and the signature itself.
        if sign_need:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self.gen_signature(params)

        url = self.base_link + endpoint
        response = request(method=method, url=url, params=params, headers=self.header)

        if response:  # Check if the answer is not empty - so as not to get an error when formatting an empty answer.
            response = response.json()
        else:
            print(response.text)
        return response
        
    def get_recent_trades(self, symbol: str, limit: int = 500):
        if self.futures:
            endpoint = '/fapi/v1/trades'
        else:
            endpoint = '/api/v3/trades'
        method = 'GET'
        params = {
            'symbol': symbol,
            'limit': limit
        }
        return self.http_request(endpoint=endpoint, method=method, params=params)

    def get_klines(self, symbol: str, interval: str, startTime: int = None, endTime: int = None, limit=500):
        if self.futures:
            endpoint = "/fapi/v1/klines"
        else:
            endpoint = "/api/v3/klines"
        method = "GET"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

    def get_order_book(self, symbol: str, limit=100):
        if self.futures:
            endpoint = "/fapi/v1/depth"
        else:
            endpoint = "/api/v3/depth"
        method = "GET"
        params = {
            'symbol': symbol,
            'limit': limit
        }

        return self.http_request(method=method, endpoint=endpoint, params=params)
        
    def get_server_time(self):
        if self.futures:
            endpoint = '/fapi/v1/time'
        else:
            endpoint = '/api/v3/time'

        method = "GET"

        return self.http_request(endpoint=endpoint, method=method)
        
    def post_limit_order(self, symbol: str, side, qnt, price, reduce_only=False):
        if self.futures:
            endpoint = "/fapi/v1/order"
        else:
            endpoint = "/api/v3/order"
        method = 'POST'
        params = {
            'symbol': symbol,
            'side': side,
            'quantity': qnt,
            'type': 'LIMIT',
            'price': price,
            'timeInForce': 'GTC'
        }
        if reduce_only:
            params['reduceOnly'] = True

        return self.http_request(endpoint=endpoint, method=method, params=params, sign_need=True)

    def post_market_order(self, symbol: str, side, qnt: float = None, quoteOrderQty: float = None):
        if self.futures:
            endpoint = "/fapi/v1/order"
            if not qnt:
                print("Mandatory parameter for futures - quantity is missing!")
                return
        else:
            endpoint = "/api/v3/order"
        method = 'POST'
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'MARKET',
        }
        if qnt or quoteOrderQty:
            if qnt:
                params['quantity'] = qnt
            if quoteOrderQty:
                params['quoteOrderQty'] = quoteOrderQty

        else:
            print("One of the mandatory parameters quantity or quoteOrderQty is not specified")
            return

        return self.http_request(endpoint=endpoint, method=method, params=params, sign_need=True)
        if startTime:
            params['startTime'] = startTime
        if endTime:
            params['endTime'] = endTime
        return self.http_request(method=method, endpoint=endpoint, params=params)
