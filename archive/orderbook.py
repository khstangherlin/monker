class Order:
    def __init__(self, price, qnty):
        self.price = float(price)
        self.qnty = float(qnty)
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return f'Order({self.price:.2f}, {self.qnty})'
    def dump(self):
        return self.price, self.qnty

class Book(dict):
    def __init__(self):
        super().__init__()

    def add(self, order):
        if order.qnty > 0.0:
            self[order.price] = order
        else:
            try:
                del self[order.price]
            except KeyError:
                pass

    def dump(self):
        return [ order.dump() for order in self.values() ]

class Trade:
    def __init__(self, ts, price, qnty):
        self.ts = float(ts)
        self.price = float(price)
        self.qnty = float(qnty)
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return f'Trade({self.ts:.6f}, {self.price:.2f}, {self.qnty})'
    def dump(self):
        return self.ts, self.price, self.qnty

class Trades(list):
    MAX = 10
    def append(self, *items):
        for item in items:
            super().append(item)
        if len(self) > self.MAX:
            del self[0:-self.MAX]

    def get_quote(self):
        ## TODO come up with better method to get a quote of 
        ##      trading price based on timestamp and quantity
        ##      as well
        return self[-1].price

    def dump(self):
        return [ trade.dump() for trade in self ]

class OrderBook:
    def __init__(self):
        self.bids = Book()
        self.asks = Book()
        self.trades = Trades()

    def get_trading_quote(self):
        return self.trades.get_quote()

    def _get_price_for(self, book, qnty):
        total_price = 0.0
        for price in sorted(book):
            total_price += price * qnty
            qnty -= book[price].qnty
            if qnty < 0:
                break
        return total_price

    def flush(self):
        self.bids.clear()
        self.asks.clear()
        self.trades.clear()

    def get_bid_for(self, qnty):
        return self._get_price_for(self.bids, qnty)

    def get_ask_for(self, qnty):
        return self._get_price_for(self.asks, qnty)

    def update_trades(self, objs):
        ## implement this on extended classes...
        raise NotImplemented

    def update_book(self, objs):
        ## implement this on extended classes...
        raise NotImplemented

    def dump(self, **kargs):
        obj = {
            'bids'   : self.bids.dump(),
            'asks'   : self.asks.dump(),
            'trades' : self.trades.dump(),
        }
        obj.update(kargs)
        return obj

