import time
import threading
from datetime import datetime

from flask_socketio import emit
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import TickerId, TickAttrib, TagValueList
from ibapi.ticktype import TickType, TickTypeEnum


REQID_CONTRACT_MAP = {}


class IBAPP(EWrapper, EClient):
    def __init__(self, socketio):
        self.socketio = socketio
        EClient.__init__(self, self)
        self.data = []

    def connect_tws(self, client_id=0):
        self.connect("127.0.0.1", 7496, clientId=client_id)

    def reqMktData(
        self,
        reqId: TickerId,
        contract: Contract,
        genericTickList: str,
        snapshot: bool,
        regulatorySnapshot: bool,
        mktDataOptions: TagValueList,
    ):
        REQID_CONTRACT_MAP[reqId] = contract
        super().reqMktData(
            reqId=reqId,
            contract=contract,
            genericTickList=genericTickList,
            snapshot=snapshot,
            regulatorySnapshot=regulatorySnapshot,
            mktDataOptions=mktDataOptions,
        )

    def tickPrice(
        self,
        reqId: TickerId,
        tickType: TickType,
        price: float,
        attrib: TickAttrib,
    ):
        print("*" * 60)
        print(
            "Tick Price. Ticker Id:",
            reqId,
            "tickType:",
            tickType,
            TickTypeEnum.to_str(tickType),
            "Price:",
            price,
            "TickAttrib:",
            attrib,
            end=" ",
        )
        print()
        if tickType == TickTypeEnum.LAST:
            print("*" * 20 + "get Last price")
            contract = REQID_CONTRACT_MAP[reqId]
            data = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "stock": contract.symbol,
                "price": price,
                "gap": 0.00,
            }
            self.socketio.emit("intraday_high", data)
