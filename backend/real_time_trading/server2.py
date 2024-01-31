async_mode = None  # "eventlet"

import eventlet

eventlet.monkey_patch(socket=True, thread=True, time=True)


import time
import threading
from flask import Flask, request, jsonify, copy_current_request_context
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS

from ibapi.contract import Contract
from backend.real_time_trading.ibapp_bkp import IBAPP

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


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
# CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app,
    logger=True,
    engineio_logger=True,
    cors_allowed_origins=["http://localhost:8000", "http://localhost:5001"],
    async_mode=async_mode,
)


class IBAPP(EWrapper, EClient):
    def __init__(self):
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
            socketio.emit("intraday_high", data)


ibapp = IBAPP()
ibapp.connect_tws()
thread = socketio.start_background_task(target=ibapp.run)
time.sleep(1)


@app.route("/")
def index():
    return "Hello world!!"


@socketio.event
def connect(auth):
    print("connected")
    print(request.sid, auth)

    emit("connected", {"data": "Connected"})


@socketio.event
def get_data():
    print("get_data")
    emit("get_data_received", "get_data")

    print("requesting data")
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    ibapp.reqMktData(1, contract, "", False, False, [])
    print("requested data")
    # time.sleep(10)
    # ibapp.disconnect()
    print("-" * 60)
    print("ibapp disconnected")
    print("-" * 60)


@socketio.event
def disconnect():
    print("user disconnected")


mock_intraday_high = {
    "time": "09:30:00",
    "symbol": "AAPL",
    "price": 100.00,
    "gap": 0.00,
    "cnt": 0,
}


def intraday_high():
    socketio.emit("intraday_high", mock_intraday_high)


def intraday_low():
    socketio.emit("intraday_low", mock_intraday_high)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
