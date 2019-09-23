import signalr_aio, base64, zlib, hashlib, hmac
import time, urllib, threading, json
import requests, asyncio, websockets
from pdb import set_trace as trace

from orderbook import OrderBook, Order

class Bittrex(OrderBook):
    key    = '15f7f668f7b548e08ebd7b50e8e1b544'
    secret = '7225f7821ff54835a963a445e9e2375c'
    url    = 'https://api.bittrex.com'

    def __init__(self):
        super().__init__()
        self.s = requests.Session()
        self.thread = threading.Thread(target=self.thread_entry_point)
        self.conn = None
        self.initial_nonce = None
        self.buff_deltas = []


    def process_message(self, msg):
        deflated_msg = zlib.decompress(base64.b64decode(msg, validate=True), -zlib.MAX_WBITS)
        return json.loads(deflated_msg.decode())

    async def on_receive(self, **msg):
        if 'R' in msg and type(msg['R']) is not bool:
            book = self.process_message(msg['R'])
            self.initial_nonce = book['N']
            self.update_book(book)

    async def on_exchange_deltas(self, msg):
        delta = self.process_message(msg[0])
        self.update_delta(delta)

    def thread_entry_point(self):
        try:
            self.conn = signalr_aio.Connection('https://beta.bittrex.com/signalr', session=None)
            hub = self.conn.register_hub('c2')
            self.conn.received += self.on_receive
            hub.client.on('uE', self.on_exchange_deltas)
            hub.server.invoke('SubscribeToExchangeDeltas', 'BTC-ETH')
            hub.server.invoke('QueryExchangeState', 'BTC-ETH')
            self.conn.start()
        except websockets.exceptions.ConnectionClosedOK:
            pass

    def update_book(self, book):
        bids = book['Z']
        for bid in bids:
            self.bids.add(Order(bid['R'], bid['Q']))
        asks = book['S']
        for ask in asks:
            self.asks.add(Order(ask['R'], ask['Q']))

    def update_delta(self, delta):
        if self.initial_nonce is None:
            self.buff_deltas.append(delta)
        else:
            if self.buff_deltas:
                for delta in self.buff_deltas:
                    if delta['N'] > self.initial_nonce:
                        self.update_book(delta)
                self.buff_deltas = []
            self.update_book(delta)

if __name__ == '__main__':
    b = Bittrex()
    b.thread.start()
    try:
        from pprint import pprint
        while True:
            time.sleep(2)
            if not b.thread.is_alive():
                print('thread has died')
            print('Bids:')
            pprint(b.bids)
            print('Asks:')
            pprint(b.asks)
    except KeyboardInterrupt:
        b.conn.close()
        b.thread.join()
        print('\nquitting politely')

