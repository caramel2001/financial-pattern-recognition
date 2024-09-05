from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest,LimitOrderRequest,GetOrdersRequest,GetAssetsRequest
from alpaca.trading.enums import OrderSide, TimeInForce,QueryOrderStatus,AssetClass,AssetStatus
from alpaca.trading.stream import TradingStream

# set environment variables
#APCA_API_BASE_URL = https://paper-api.alpaca.markets

class PaperFolio:
    def __init__(self,api_key:str,secret_key:str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.client = TradingClient(api_key,secret_key,paper=True)
        self.account = self.client.get_account()

    def create_market_order(self,symbol:str,qty:int,side:OrderSide,time_in_force:TimeInForce = TimeInForce.DAY):
        market_order_data = MarketOrderRequest(
            symbol=symbol,  
            qty=qty,
            side=side,
            time_in_force=time_in_force
        )
        order = self.client.submit_order(market_order_data)
        return order
    
    def create_limit_order(self,symbol:str,qty:int,side:OrderSide,limit_price:float,time_in_force:str = TimeInForce.DAY):
        limit_order_data = LimitOrderRequest(
            symbol=symbol,  
            qty=qty,
            side=side,
            limit_price=limit_price,
            time_in_force=time_in_force
        )
        order = self.client.submit_order(limit_order_data)
        return order
    
    def get_orders(self,open_orders:bool = True,buy_orders:bool = False):
        request_params = GetOrdersRequest(
                    status=QueryOrderStatus.OPEN if open_orders else QueryOrderStatus.ALL,
                    side=OrderSide.BUY if buy_orders else OrderSide.SELL
         )
        orders = self.client.get_orders(filter=request_params)
        return orders
    
    def cancel_orders(self,UUIDs:list,all_orders:bool=False):
        if all_orders:
            cancel_statuses = self.client.cancel_all_orders()
        else:
            cancel_statuses = []
            for id in UUIDs:
                cancel_status = self.client.cancel_order_by_id(id)
                cancel_statuses.append(cancel_status)
        return cancel_statuses
    
    def get_positions(self):
        positions = self.client.get_all_positions()
        return positions
    
    def close_positions(self,symbols_or_asset_ids:list,all_positions:bool=False):
        if all_positions:
            self.client.close_all_positions(cancel_orders=True)
        else:
            for symbol in symbols_or_asset_ids:
                self.client.close_position(symbol,cancel_orders=True)

    def get_all_equity_assets(self):
        request = GetAssetsRequest(
            asset_class=AssetClass.US_EQUITY,
            status=AssetStatus.ACTIVE
        )
        assets = self.client.get_all_assets(request)
        return assets
    
    def check_asset_availability(self,symbols:list):
        assets = self.get_all_equity_assets()
        avail_symbols = set([asset.symbol for asset in assets])
        return [x in avail_symbols for x in symbols]

    def get_stream_order_updates(self):
        trading_stream = TradingStream(self.api_key, self.secret_key, paper=True)
        async def update_handler(data):
            # trade updates will arrive in our async handler
            print(data)
        # subscribe to trade updates and supply the handler as a parameter
        trading_stream.subscribe_trade_updates(update_handler)
        # start our websocket streaming
        trading_stream.run()